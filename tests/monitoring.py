#!/usr/bin/env python3
"""
Monitoramento e Analytics para Test Automation

Coleta métricas, gera relatórios e fornece insights sobre
a execução dos testes ao longo do tempo.
"""

import json
import sqlite3
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class TestMetrics:
    """Métricas de um teste específico."""
    test_id: str
    avg_duration: float
    min_duration: float
    max_duration: float
    success_rate: float
    total_runs: int
    failures: int
    flakiness_score: float  # 0-1, quanto maior mais instável
    last_run: datetime


@dataclass
class ExecutionMetrics:
    """Métricas de uma execução completa."""
    timestamp: datetime
    total_duration: float
    total_tests: int
    passed: int
    failed: int
    errors: int
    success_rate: float
    parallel: bool
    workers: int


class TestAnalytics:
    """Analisa métricas históricas dos testes."""

    def __init__(self, db_path: str = "test_analytics.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Inicializa o banco de dados SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Habilitar foreign keys
        cursor.execute("PRAGMA foreign_keys = ON")

        # Tabela de execuções
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                duration REAL NOT NULL,
                total_tests INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                failed INTEGER NOT NULL,
                errors INTEGER NOT NULL,
                success_rate REAL NOT NULL,
                parallel INTEGER NOT NULL,
                workers INTEGER NOT NULL
            )
        """)

        # Criar índice para timestamp
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_executions_timestamp
            ON executions(timestamp)
        """)

        # Tabela de resultados individuais
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id INTEGER NOT NULL,
                test_id TEXT NOT NULL,
                status TEXT NOT NULL,
                duration REAL NOT NULL,
                error TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (execution_id) REFERENCES executions (id)
            )
        """)

        conn.commit()
        conn.close()

    def record_execution(self, execution_id: int, summary: Dict) -> None:
        """Registra uma execução completa."""
        from orchestrator import ExecutionSummary

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO executions
            (timestamp, duration, total_tests, passed, failed, errors, success_rate, parallel, workers)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            summary.get("duration", 0),
            summary.get("total", 0),
            summary.get("passed", 0),
            summary.get("failed", 0),
            summary.get("errors", 0),
            summary.get("success_rate", 0),
            1 if summary.get("parallel") else 0,
            summary.get("workers", 1)
        ))

        conn.commit()
        conn.close()

    def get_test_metrics(self, test_id: str, days: int = 30) -> TestMetrics:
        """Obtém métricas de um teste específico."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute("""
            SELECT
                test_id,
                AVG(duration) as avg_duration,
                MIN(duration) as min_duration,
                MAX(duration) as max_duration,
                COUNT(*) as total_runs,
                SUM(CASE WHEN status != 'passed' THEN 1 ELSE 0 END) as failures,
                MAX(timestamp) as last_run
            FROM test_results
            WHERE test_id = ? AND timestamp > ?
            GROUP BY test_id
        """, (test_id, cutoff))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return TestMetrics(
                test_id=test_id,
                avg_duration=0,
                min_duration=0,
                max_duration=0,
                success_rate=0,
                total_runs=0,
                failures=0,
                flakiness_score=0,
                last_run=datetime.now()
            )

        test_id, avg_dur, min_dur, max_dur, total, failures, last_run = row
        success_rate = ((total - failures) / total * 100) if total > 0 else 0

        # Calcular flakiness (variação na taxa de sucesso)
        flakiness = failures / total if total > 0 else 0

        return TestMetrics(
            test_id=test_id,
            avg_duration=avg_dur,
            min_duration=min_dur,
            max_duration=max_dur,
            success_rate=success_rate,
            total_runs=total,
            failures=failures,
            flakiness_score=flakiness,
            last_run=datetime.fromisoformat(last_run)
        )

    def get_flaky_tests(self, threshold: float = 0.2, days: int = 30) -> List[TestMetrics]:
        """Retorna testes instáveis acima do threshold."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute("""
            SELECT
                test_id,
                AVG(duration) as avg_duration,
                MIN(duration) as min_duration,
                MAX(duration) as max_duration,
                COUNT(*) as total_runs,
                SUM(CASE WHEN status != 'passed' THEN 1 ELSE 0 END) as failures
            FROM test_results
            WHERE timestamp > ?
            GROUP BY test_id
            HAVING (CAST(SUM(CASE WHEN status != 'passed' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*)) > ?
            ORDER BY failures DESC
        """, (cutoff, threshold))

        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            test_id, avg_dur, min_dur, max_dur, total, failures = row
            flakiness = failures / total if total > 0 else 0
            results.append(TestMetrics(
                test_id=test_id,
                avg_duration=avg_dur,
                min_duration=min_dur,
                max_duration=max_dur,
                success_rate=((total - failures) / total * 100),
                total_runs=total,
                failures=failures,
                flakiness_score=flakiness,
                last_run=datetime.now()
            ))

        return results

    def get_slow_tests(self, threshold: float = 1.0, days: int = 30) -> List[TestMetrics]:
        """Retorna testes lentos acima do threshold (segundos)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute("""
            SELECT
                test_id,
                AVG(duration) as avg_duration,
                MIN(duration) as min_duration,
                MAX(duration) as max_duration,
                COUNT(*) as total_runs,
                SUM(CASE WHEN status != 'passed' THEN 1 ELSE 0 END) as failures
            FROM test_results
            WHERE timestamp > ?
            GROUP BY test_id
            HAVING AVG(duration) > ?
            ORDER BY avg_duration DESC
        """, (cutoff, threshold))

        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            test_id, avg_dur, min_dur, max_dur, total, failures = row
            results.append(TestMetrics(
                test_id=test_id,
                avg_duration=avg_dur,
                min_duration=min_dur,
                max_duration=max_dur,
                success_rate=((total - failures) / total * 100),
                total_runs=total,
                failures=failures,
                flakiness_score=failures / total,
                last_run=datetime.now()
            ))

        return results

    def generate_report(self, days: int = 30) -> str:
        """Gera relatório de analytics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff = (datetime.now() - timedelta(days=days)).isoformat()

        # Métricas gerais com COALESCE para NULL handling
        cursor.execute("""
            SELECT
                COALESCE(COUNT(*), 0) as total_executions,
                COALESCE(AVG(duration), 0) as avg_duration,
                COALESCE(AVG(success_rate), 0) as avg_success_rate,
                COALESCE(SUM(passed), 0) as total_passed,
                COALESCE(SUM(failed), 0) as total_failed,
                COALESCE(SUM(errors), 0) as total_errors
            FROM executions
            WHERE timestamp > ?
        """, (cutoff,))

        row = cursor.fetchone()
        total_execs, avg_dur, avg_success, total_passed, total_failed, total_errors = row or (0, 0, 0, 0, 0, 0)

        report = []
        report.append("=" * 60)
        report.append(f"📊 RELATÓRIO DE ANALYTICS ({days} dias)")
        report.append("=" * 60)
        report.append(f"\nExecuções totais: {total_execs}")
        report.append(f"Duração média: {avg_dur:.2f}s")
        report.append(f"Taxa de sucesso média: {avg_success:.1f}%")
        report.append(f"Testes passados: {total_passed}")
        report.append(f"Testes falhados: {total_failed}")
        report.append(f"Erros: {total_errors}")

        # Testes instáveis
        flaky = self.get_flaky_tests(days=days)
        if flaky:
            report.append(f"\n⚠️  TESTES INSTÁVEIS ({len(flaky)}):")
            for metrics in flaky[:10]:
                report.append(f"   - {metrics.test_id}")
                report.append(f"     Falhas: {metrics.failures}/{metrics.total_runs} ({metrics.flakiness_score*100:.1f}%)")

        # Testes lentos
        slow = self.get_slow_tests(days=days)
        if slow:
            report.append(f"\n🐌 TESTES LENTOS ({len(slow)}):")
            for metrics in slow[:10]:
                report.append(f"   - {metrics.test_id}")
                report.append(f"     Duração média: {metrics.avg_duration:.2f}s")

        report.append("=" * 60)

        conn.close()
        return "\n".join(report)


class PerformanceAnalyzer:
    """Analisa performance de execução de testes."""

    def __init__(self, analytics: TestAnalytics):
        self.analytics = analytics

    def suggest_parallelization(self) -> Dict[str, Any]:
        """Sugere estratégia de paralelização."""
        slow_tests = self.analytics.get_slow_tests(threshold=0.5, days=7)

        # Separar por categoria de duração
        fast = [t for t in slow_tests if t.avg_duration < 1.0]
        medium = [t for t in slow_tests if 1.0 <= t.avg_duration < 5.0]
        slow = [t for t in slow_tests if t.avg_duration >= 5.0]

        suggested_workers = max(2, min(8, len(medium) + len(slow)))

        return {
            "fast_tests": len(fast),
            "medium_tests": len(medium),
            "slow_tests": len(slow),
            "suggested_workers": suggested_workers,
            "estimated_speedup": self._estimate_speedup(slow_tests, suggested_workers)
        }

    def _estimate_speedup(self, metrics: List[TestMetrics], workers: int = 4) -> float:
        """Estima ganho de speed com paralelização."""
        if not metrics:
            return 1.0

        sequential_time = sum(m.avg_duration for m in metrics)
        parallel_time = sequential_time / max(1, workers)

        return sequential_time / parallel_time if parallel_time > 0 else 1.0

    def optimize_execution_order(self) -> List[str]:
        """Sugere ordem ótima de execução."""
        # Buscar todas as métricas
        conn = sqlite3.connect(self.analytics.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                test_id,
                AVG(duration) as avg_duration,
                SUM(CASE WHEN status != 'passed' THEN 1 ELSE 0 END) as failures
            FROM test_results
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY test_id
            ORDER BY failures DESC, avg_duration DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        # Retornar apenas IDs ordenados
        return [row[0] for row in rows]


def main():
    """CLI para analytics."""
    import argparse

    parser = argparse.ArgumentParser(description="Analytics de Testes")
    parser.add_argument("--report", "-r", action="store_true", help="Gerar relatório")
    parser.add_argument("--flaky", "-f", action="store_true", help="Listar testes instáveis")
    parser.add_argument("--slow", "-s", action="store_true", help="Listar testes lentos")
    parser.add_argument("--days", "-d", type=int, default=30, help="Período em dias")
    parser.add_argument("--optimize", "-o", action="store_true", help="Sugerir otimizações")

    args = parser.parse_args()

    analytics = TestAnalytics()

    if args.report:
        print(analytics.generate_report(days=args.days))

    if args.flaky:
        flaky = analytics.get_flaky_tests(days=args.days)
        print(f"\n⚠️  TESTES INSTÁVEIS ({len(flaky)}):")
        for m in flaky:
            print(f"  {m.test_id}: {m.failures}/{m.total_runs} falhas ({m.flakiness_score*100:.1f}%)")

    if args.slow:
        slow = analytics.get_slow_tests(days=args.days)
        print(f"\n🐌 TESTES LENTOS ({len(slow)}):")
        for m in slow:
            print(f"  {m.test_id}: {m.avg_duration:.2f}s (média)")

    if args.optimize:
        analyzer = PerformanceAnalyzer(analytics)
        suggestions = analyzer.suggest_parallelization()
        print(f"\n💡 SUGESTÕES DE OTIMIZAÇÃO:")
        print(f"  Testes rápidos: {suggestions['fast_tests']}")
        print(f"  Testes médios: {suggestions['medium_tests']}")
        print(f"  Testes lentos: {suggestions['slow_tests']}")
        print(f"  Workers sugeridos: {suggestions['suggested_workers']}")
        print(f"  Speedup estimado: {suggestions['estimated_speedup']:.2f}x")


if __name__ == "__main__":
    main()
