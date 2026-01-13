#!/usr/bin/env python3
"""
Test Automation Orchestrator para Shopee API

Sistema inteligente de orquestração de testes com:
- Descoberta e classificação automática de testes
- Execução paralela otimizada
- Gestão de recursos
- Monitoramento e analytics
- Integração CI/CD
"""

import concurrent.futures
import dataclasses
import enum
import io
import json
import os
import re
import subprocess
import sys
import threading
import time
import traceback
import unittest
import ast
import importlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type
import importlib.util
import inspect

# ============================================================
# CLASSIFICAÇÃO E TIPOS DE TESTE
# ============================================================


class TestCategory(enum.Enum):
    """Categorias de teste para orquestração inteligente."""
    UNIT = "unit"                     # Testes unitários rápidos (< 1s)
    INTEGRATION = "integration"       # Testes de integração médios (< 10s)
    API = "api"                       # Testes de API lentos (> 10s)
    MOCK = "mock"                     # Testes com mocks (rápidos)
    PROPERTY = "property"             # Testes de propriedade
    FLAKY = "flaky"                   # Testes instáveis (requerem retry)


class TestPriority(enum.Enum):
    """Prioridade de execução."""
    CRITICAL = 0      # Testes críticos (executam primeiro)
    HIGH = 1          # Alta prioridade
    MEDIUM = 2        # Prioridade média
    LOW = 3           # Baixa prioridade


@dataclass
class TestMetadata:
    """Metadados de um teste para orquestração."""
    name: str
    module: str
    file_path: str
    line_number: int
    category: TestCategory
    priority: TestPriority
    estimated_duration: float = 1.0  # segundos
    dependencies: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    flaky: bool = False
    requires_network: bool = False
    requires_auth: bool = False
    parallel_safe: bool = True


# ============================================================
# DESCOBERTA E CLASSIFICAÇÃO DE TESTES
# ============================================================


class TestDiscovery:
    """Descobre e classifica testes automaticamente."""

    def __init__(self, test_dirs: List[str] = None):
        # Se não especificado, usar diretório atual onde o script está
        if test_dirs is None:
            script_dir = Path(__file__).parent
            self.test_dirs = [str(script_dir)]
        else:
            self.test_dirs = test_dirs
        self.tests: Dict[str, TestMetadata] = {}

    def discover(self) -> Dict[str, TestMetadata]:
        """Descobre todos os testes nos diretórios especificados."""
        self.tests = {}

        for test_dir in self.test_dirs:
            test_path = Path(test_dir)
            if not test_path.exists():
                continue

            for test_file in test_path.rglob("test_*.py"):
                self._analyze_test_file(test_file)

        return self.tests

    def _analyze_test_file(self, test_file: Path) -> None:
        """Analisa um arquivo de teste e extrai metadados."""
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Usar análise manual (mais robusta)
        self._manual_analyze(test_file, content)

    def _iterate_suite(self, suite, test_file: Path, content: str) -> None:
        """Itera recursivamente sobre uma suite de testes."""
        for test in suite:
            if isinstance(test, unittest.TestCase):
                self._process_test_case(test, test_file, content)
            elif isinstance(test, unittest.TestSuite):
                self._iterate_suite(test, test_file, content)

    def _process_test_case(self, test: unittest.TestCase, test_file: Path, content: str) -> None:
        """Processa um TestCase individual."""
        test_id = test.id()
        if not test_id:
            return

        # Extrair nome da classe e método
        parts = test_id.split('.')
        if len(parts) >= 2:
            class_name = parts[-2]
            method_name = parts[-1]
            full_name = f"{class_name}.{method_name}"

            # Criar metadados básicos
            metadata = TestMetadata(
                name=full_name,
                module='.'.join(parts[:-2]),
                file_path=str(test_file.resolve()),
                line_number=0,
                category=self._detect_category_from_name(method_name, content),
                priority=TestPriority.MEDIUM,
                estimated_duration=0.1,
                parallel_safe=True
            )
            self.tests[full_name] = metadata

    def _manual_analyze(self, test_file: Path, content: str) -> None:
        """Análise manual do arquivo usando AST parsing."""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Verificar se herda de TestCase
                    is_test_case = False
                    for base in node.bases:
                        if isinstance(base, ast.Name) and 'TestCase' in base.id:
                            is_test_case = True
                            break
                        elif isinstance(base, ast.Attribute) and 'TestCase' in base.attr:
                            is_test_case = True
                            break

                    if is_test_case:
                        class_name = node.name
                        # Encontrar métodos test_*
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                                method_name = item.name
                                full_name = f"{class_name}.{method_name}"

                                metadata = TestMetadata(
                                    name=full_name,
                                    module=test_file.stem,
                                    file_path=str(test_file.resolve()),
                                    line_number=item.lineno or 0,
                                    category=self._detect_category_from_name(method_name, content),
                                    priority=TestPriority.MEDIUM,
                                    estimated_duration=0.1,
                                    parallel_safe=True
                                )
                                self.tests[full_name] = metadata
        except (SyntaxError, ValueError) as e:
            # Fallback para regex se AST parsing falhar
            self._manual_analyze_fallback(test_file, content)

    def _manual_analyze_fallback(self, test_file: Path, content: str) -> None:
        """Análise manual usando regex como fallback."""
        # Encontrar classes de teste
        class_pattern = r'class\s+(\w+)\s*\(.*TestCase.*\):'
        for class_match in re.finditer(class_pattern, content):
            class_name = class_match.group(1)

            # Encontrar métodos de teste
            method_pattern = r'def\s+(test_\w+)\s*\('
            class_start = class_match.end()
            next_class = content.find('class ', class_start)
            if next_class == -1:
                class_content = content[class_start:]
            else:
                class_content = content[class_start:next_class]

            for method_match in re.finditer(method_pattern, class_content):
                method_name = method_match.group(1)
                full_name = f"{class_name}.{method_name}"

                metadata = TestMetadata(
                    name=full_name,
                    module=test_file.stem,
                    file_path=str(test_file.resolve()),
                    line_number=0,
                    category=self._detect_category_from_name(method_name, content),
                    priority=TestPriority.MEDIUM,
                    estimated_duration=0.1,
                    parallel_safe=True
                )
                self.tests[full_name] = metadata

    def _detect_category_from_name(self, name: str, content: str) -> TestCategory:
        """Detecta categoria baseada no nome e conteúdo."""
        if "mock" in name.lower() or "@patch" in content:
            return TestCategory.MOCK
        if "api" in name.lower() or "request" in name.lower():
            return TestCategory.API
        return TestCategory.UNIT

    def _analyze_test_class(self, test_class: Type, test_file: Path, content: str) -> None:
        """Analisa uma classe de teste."""
        for method_name, method in inspect.getmembers(test_class, inspect.ismethod):
            if method_name.startswith("test_"):
                test_id = f"{test_class.__name__}.{method_name}"
                metadata = self._extract_metadata(test_class, method, test_file, content)
                self.tests[test_id] = metadata

    def _extract_metadata(self, test_class: Type, test_method: Callable,
                         test_file: Path, content: str) -> TestMetadata:
        """Extrai metadados de um teste."""

        # Encontrar linha do método
        source_lines, start_line = inspect.getsourcelines(test_method)
        abs_path = str(test_file.resolve())

        # Categorização baseada em padrões
        name = f"{test_class.__name__}.{test_method.__name__}"
        doc = test_method.__doc__ or ""

        # Detectar categoria
        category = self._detect_category(test_class, test_method, content, doc)

        # Detectar prioridade
        priority = self._detect_priority(name, doc, content)

        # Detectar se requer network/auth
        requires_network = self._requires_network(name, doc, content)
        requires_auth = self._requires_auth(name, doc, content)

        # Detectar se é flaky
        flaky = self._is_flaky(name, doc, content)

        # Estimar duração
        duration = self._estimate_duration(category, name, content)

        return TestMetadata(
            name=name,
            module=test_class.__module__,
            file_path=abs_path,
            line_number=start_line,
            category=category,
            priority=priority,
            estimated_duration=duration,
            flaky=flaky,
            requires_network=requires_network,
            requires_auth=requires_auth,
            parallel_safe=not (requires_auth or flaky)
        )

    def _detect_category(self, test_class: Type, test_method: Callable,
                         content: str, doc: str) -> TestCategory:
        """Detecta a categoria do teste."""

        name = test_method.__name__
        full_name = f"{test_class.__name__}.{name}"

        # Padrões para detectar categoria
        if "mock" in name.lower() or "mock" in doc.lower():
            return TestCategory.MOCK

        if "integration" in name.lower() or "integration" in doc.lower():
            return TestCategory.INTEGRATION

        if "api" in name.lower() or "request" in name.lower():
            return TestCategory.API

        if "property" in name.lower() or "property" in doc.lower():
            return TestCategory.PROPERTY

        # Verificar se usa mocks
        source = inspect.getsource(test_method)
        if "@patch" in content or "Mock" in source or "mock" in source:
            return TestCategory.MOCK

        return TestCategory.UNIT

    def _detect_priority(self, name: str, doc: str, content: str) -> TestPriority:
        """Detecta a prioridade do teste."""

        if "critical" in name.lower() or "critical" in doc.lower():
            return TestPriority.CRITICAL

        if "important" in name.lower() or "important" in doc.lower():
            return TestPriority.HIGH

        if "flaky" in name.lower() or "slow" in name.lower():
            return TestPriority.LOW

        return TestPriority.MEDIUM

    def _requires_network(self, name: str, doc: str, content: str) -> bool:
        """Detecta se o teste requer rede."""
        return bool("api" in name.lower() or "network" in doc.lower())

    def _requires_auth(self, name: str, doc: str, content: str) -> bool:
        """Detecta se o teste requer autenticação."""
        return bool("auth" in name.lower() or "login" in doc.lower())

    def _is_flaky(self, name: str, doc: str, content: str) -> bool:
        """Detecta se o teste é instável."""
        return bool("flaky" in name.lower() or "unstable" in doc.lower())

    def _estimate_duration(self, category: TestCategory, name: str, content: str) -> float:
        """Estima a duração do teste."""
        base_durations = {
            TestCategory.UNIT: 0.1,
            TestCategory.MOCK: 0.05,
            TestCategory.INTEGRATION: 2.0,
            TestCategory.API: 5.0,
            TestCategory.PROPERTY: 1.0,
        }
        return base_durations.get(category, 1.0)


# ============================================================
# ORQUESTRAÇÃO E EXECUÇÃO
# ============================================================


@dataclass
class ExecutionConfig:
    """Configuração de execução dos testes."""
    max_workers: int = 4
    parallel: bool = True
    fail_fast: bool = False
    retry_flaky: int = 3
    verbose: bool = True
    coverage: bool = False
    categories: Set[TestCategory] = field(default_factory=lambda: set(TestCategory))


@dataclass
class TestResult:
    """Resultado de execução de um teste."""
    test_id: str
    status: str  # "passed", "failed", "skipped", "error"
    duration: float
    output: str = ""
    error: str = ""
    retries: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionSummary:
    """Resumo da execução dos testes."""
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration: float = 0.0
    results: List[TestResult] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso."""
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100

    @property
    def finished(self) -> bool:
        """Se a execução terminou."""
        return self.end_time is not None


class TestOrchestrator:
    """Orquestrador inteligente de testes."""

    def __init__(self, config: ExecutionConfig = None):
        self.config = config or ExecutionConfig()
        self.discovery = TestDiscovery()
        self.tests: Dict[str, TestMetadata] = {}
        self.summary = ExecutionSummary()
        self._stop_event = threading.Event()
        self._summary_lock = threading.Lock()

    def discover_tests(self) -> None:
        """Descobre todos os testes."""
        print("🔍 Descobrindo testes...")
        self.tests = self.discovery.discover()
        print(f"✅ {len(self.tests)} testes descobertos")

        # Mostrar distribuição por categoria
        by_category = {}
        for test in self.tests.values():
            by_category.setdefault(test.category, 0)
            by_category[test.category] += 1

        for cat, count in sorted(by_category.items()):
            print(f"   {cat.value}: {count} testes")

    def run(self) -> ExecutionSummary:
        """Executa os testes conforme a configuração."""
        self.summary.start_time = datetime.now()

        print(f"\n🚀 Iniciando execução de {len(self.tests)} testes...")
        print(f"   Paralelo: {self.config.parallel}")
        print(f"   Workers: {self.config.max_workers}")
        print(f"   Fail fast: {self.config.fail_fast}\n")

        # Filtrar testes por categoria se especificado
        tests_to_run = self._filter_tests()

        # Ordenar por prioridade
        tests_to_run = sorted(
            tests_to_run,
            key=lambda t: (t.priority.value, t.estimated_duration)
        )

        self.summary.total = len(tests_to_run)

        if self.config.parallel and len(tests_to_run) > 1:
            self._run_parallel(tests_to_run)
        else:
            self._run_sequential(tests_to_run)

        self.summary.end_time = datetime.now()
        self.summary.duration = (
            self.summary.end_time - self.summary.start_time
        ).total_seconds()

        return self.summary

    def _filter_tests(self) -> List[TestMetadata]:
        """Filtra testes baseado na configuração."""
        tests = list(self.tests.values())

        # Se categorias específicas foram configuradas, filtrar
        if self.config.categories and self.config.categories != set(TestCategory):
            tests = [t for t in tests if t.category in self.config.categories]

        return tests

    def _run_sequential(self, tests: List[TestMetadata]) -> None:
        """Executa testes sequencialmente."""
        for i, test in enumerate(tests, 1):
            if self._stop_event.is_set():
                break

            print(f"[{i}/{len(tests)}] {test.name}... ", end="", flush=True)

            result = self._execute_single_test(test)
            self.summary.results.append(result)

            self._update_summary(result)
            self._print_result(result)

            if self.config.fail_fast and result.status in ("failed", "error"):
                print("\n⛔ Fail fast: parando execução")
                break

    def _run_parallel(self, tests: List[TestMetadata]) -> None:
        """Executa testes em paralelo."""
        # Separar testes paralelos de sequenciais
        parallel_tests = [t for t in tests if t.parallel_safe]
        sequential_tests = [t for t in tests if not t.parallel_safe]

        completed = 0
        total = len(tests)

        # Executar testes paralelos
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = {
                executor.submit(self._execute_single_test, test): test
                for test in parallel_tests
            }

            for future in as_completed(futures):
                if self._stop_event.is_set():
                    break

                test = futures[future]
                try:
                    result = future.result()
                    with self._summary_lock:
                        self.summary.results.append(result)
                        self._update_summary(result)

                    completed += 1
                    print(f"[{completed}/{total}] {test.name}... ", end="", flush=True)
                    self._print_result(result)

                    if self.config.fail_fast and result.status in ("failed", "error"):
                        print("\n⛔ Fail fast: cancelando testes restantes")
                        executor.shutdown(wait=False, cancel_futures=True)
                        break

                except Exception as e:
                    print(f"❌ Erro ao executar {test.name}: {e}")

        # Executar testes sequenciais
        for test in sequential_tests:
            if self._stop_event.is_set():
                break

            completed += 1
            print(f"[{completed}/{total}] {test.name}... ", end="", flush=True)

            result = self._execute_single_test(test)
            self.summary.results.append(result)
            self._update_summary(result)
            self._print_result(result)

    def _execute_single_test(self, test: TestMetadata) -> TestResult:
        """Executa um único teste."""
        start_time = time.time()

        try:
            # Importar e executar o teste
            module = importlib.import_module(test.module)
            test_class_name = test.name.split('.')[0]
            test_method_name = test.name.split('.')[1]

            test_class = getattr(module, test_class_name)
            suite = unittest.TestSuite()
            suite.addTest(test_class(test_method_name))

            # Usar context manager para fechar o file handle
            with open(os.devnull, 'w', encoding='utf-8') as stream:
                runner = unittest.TextTestRunner(stream=stream, verbosity=0)
                result = runner.run(suite)

            duration = time.time() - start_time

            if result.wasSuccessful():
                return TestResult(
                    test_id=test.name,
                    status="passed",
                    duration=duration
                )
            elif result.errors:
                error_msg = str(result.errors[0][1]) if result.errors else ""
                return TestResult(
                    test_id=test.name,
                    status="error",
                    duration=duration,
                    error=error_msg
                )
            else:
                failure_msg = str(result.failures[0][1]) if result.failures else ""
                return TestResult(
                    test_id=test.name,
                    status="failed",
                    duration=duration,
                    error=failure_msg
                )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_id=test.name,
                status="error",
                duration=duration,
                error=str(e)
            )

    def _update_summary(self, result: TestResult) -> None:
        """Atualiza o resumo com o resultado."""
        if result.status == "passed":
            self.summary.passed += 1
        elif result.status == "failed":
            self.summary.failed += 1
        elif result.status == "error":
            self.summary.errors += 1
        elif result.status == "skipped":
            self.summary.skipped += 1

    def _print_result(self, result: TestResult) -> None:
        """Imprime o resultado do teste."""
        if result.status == "passed":
            print(f"✅ {result.duration:.3f}s")
        elif result.status == "failed":
            print(f"❌ {result.duration:.3f}s")
            if self.config.verbose and result.error:
                print(f"   {result.error[:100]}")
        elif result.status == "error":
            print(f"💥 {result.duration:.3f}s")
            if self.config.verbose and result.error:
                print(f"   {result.error[:100]}")
        else:
            print(f"⏭️  {result.duration:.3f}s")

    def print_summary(self) -> None:
        """Imprime o resumo da execução."""
        duration = self.summary.duration or 0.0

        print("\n" + "=" * 60)
        print("📊 RESUMO DA EXECUÇÃO")
        print("=" * 60)
        print(f"Total:     {self.summary.total}")
        print(f"✅ Passou:  {self.summary.passed}")
        print(f"❌ Falhou:  {self.summary.failed}")
        print(f"💥 Erros:   {self.summary.errors}")
        print(f"⏭️  Pulado:  {self.summary.skipped}")
        print(f"⏱️  Duração: {duration:.2f}s")
        print(f"📈 Taxa:    {self.summary.success_rate:.1f}%")

        if self.summary.failed > 0 or self.summary.errors > 0:
            print("\n❌ TESTES FALHARAM:")
            for result in self.summary.results:
                if result.status in ("failed", "error"):
                    print(f"   - {result.test_id}: {result.error[:60]}...")

        print("=" * 60)


# ============================================================
# INTEGRAÇÃO CI/CD
# ============================================================


class CIOrchestrator:
    """Orquestrador específico para ambientes CI/CD."""

    def __init__(self, config: ExecutionConfig = None):
        self.config = config or ExecutionConfig()
        self.orchestrator = TestOrchestrator(self.config)

    def run_ci_pipeline(self) -> bool:
        """Executa o pipeline completo de CI."""
        print("🔧 Pipeline CI/CD Shopee API")

        # Etapa 1: Descobrir testes
        self.orchestrator.discover_tests()

        # Etapa 2: Executar testes
        summary = self.orchestrator.run()

        # Etapa 3: Relatório
        self.orchestrator.print_summary()

        # Etapa 4: Exit code apropriado
        success = summary.failed == 0 and summary.errors == 0

        # Salvar relatório em JSON
        self._save_json_report(summary)

        return success

    def _save_json_report(self, summary: ExecutionSummary) -> None:
        """Salva relatório em JSON para CI."""
        report = {
            "timestamp": summary.start_time.isoformat(),
            "duration": summary.duration,
            "total": summary.total,
            "passed": summary.passed,
            "failed": summary.failed,
            "errors": summary.errors,
            "skipped": summary.skipped,
            "success_rate": summary.success_rate,
            "results": [
                {
                    "test_id": r.test_id,
                    "status": r.status,
                    "duration": r.duration,
                    "error": r.error[:200] if r.error else None,
                }
                for r in summary.results
            ]
        }

        output_path = Path("test-results.json")
        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Relatório salvo em: {output_path}")
        except OSError as e:
            print(f"⚠️  Erro ao salvar relatório: {e}")


# ============================================================
# CLI
# ============================================================


def main():
    """Ponto de entrada principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Orquestrador Inteligente de Testes"
    )
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="Executar testes em paralelo"
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=4,
        help="Número de workers para execução paralela"
    )
    parser.add_argument(
        "--fail-fast", "-f",
        action="store_true",
        help="Parar no primeiro erro"
    )
    parser.add_argument(
        "--category", "-c",
        choices=[c.value for c in TestCategory],
        action="append",
        help="Executar apenas categorias específicas"
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Modo CI/CD"
    )

    args = parser.parse_args()

    # Configurar orquestrador
    categories = set()
    if args.category:
        categories = {TestCategory(c) for c in args.category}

    config = ExecutionConfig(
        parallel=args.parallel,
        max_workers=args.workers,
        fail_fast=args.fail_fast,
        categories=categories
    )

    if args.ci:
        ci = CIOrchestrator(config)
        success = ci.run_ci_pipeline()
        sys.exit(0 if success else 1)
    else:
        orchestrator = TestOrchestrator(config)
        orchestrator.discover_tests()
        orchestrator.run()
        orchestrator.print_summary()

        success = orchestrator.summary.failed == 0
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
