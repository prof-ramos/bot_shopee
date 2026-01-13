# Test Automation Orchestrator

Sistema inteligente de orquestração de testes para o projeto Shopee API com execução paralela, classificação automática e analytics.

## 🎯 Funcionalidades

### Descoberta e Classificação Automática
- **Detecção automática** de testes nos diretórios especificados
- **Classificação inteligente** por categoria:
  - `unit` - Testes unitários rápidos (< 1s)
  - `mock` - Testes com mocks
  - `integration` - Testes de integração
  - `api` - Testes de API externas
  - `property` - Testes de propriedade
  - `flaky` - Testes instáveis

### Execução Otimizada
- **Execução paralela** com ThreadPoolExecutor
- **Agrupamento por prioridade** (crítico primeiro)
- **Fail-fast** opcional para parar no primeiro erro
- **Retry automático** para testes instáveis

### Analytics e Monitoramento
- **Histórico de execuções** em SQLite
- **Detecção de testes instáveis** (flaky)
- **Identificação de testes lentos**
- **Sugestões de otimização** de execução
- **Relatórios de performance**

## 📦 Instalação

```bash
# Dependências já estão em requirements.txt
pip install requests python-dotenv

# Opcional: para analytics avançado
pip install matplotlib pandas
```

## 🚀 Uso

### CLI Básico

```bash
# Executar todos os testes
python tests/orchestrator.py

# Execução paralela
python tests/orchestrator.py --parallel

# Com 8 workers
python tests/orchestrator.py --parallel --workers 8

# Fail fast (parar no primeiro erro)
python tests/orchestrator.py --fail-fast

# Executar apenas categorias específicas
python tests/orchestrator.py --category unit --category mock

# Modo CI/CD
python tests/orchestrator.py --ci
```

### Analytics

```bash
# Gerar relatório dos últimos 30 dias
python tests/monitoring.py --report

# Ver testes instáveis
python tests/monitoring.py --flaky --days 7

# Ver testes lentos
python tests/monitoring.py --slow --days 7

# Sugestões de otimização
python tests/monitoring.py --optimize
```

## 📊 Estrutura

```
tests/
├── orchestrator.py      # Framework principal de orquestração
├── monitoring.py        # Sistema de analytics e monitoramento
├── test_shopee_api.py   # Testes existentes
└── test_analytics.db    # Banco de dados SQLite (criado automaticamente)
```

## 🔧 Como Funciona

### 1. Descoberta de Testes

```python
from tests.orchestrator import TestOrchestrator

orchestrator = TestOrchestrator()
orchestrator.discover_tests()  # Analisa todos os arquivos test_*.py
```

### 2. Execução Paralela

```python
from tests.orchestrator import TestOrchestrator, ExecutionConfig

config = ExecutionConfig(
    parallel=True,
    max_workers=4,
    fail_fast=False
)

orchestrator = TestOrchestrator(config)
summary = orchestrator.run()
orchestrator.print_summary()
```

### 3. Analytics

```python
from tests.monitoring import TestAnalytics, PerformanceAnalyzer

analytics = TestAnalytics()
metrics = analytics.get_test_metrics("TestShopeeAPI.test_buscar_ofertas_lojas_query")

analyzer = PerformanceAnalyzer(analytics)
suggestions = analyzer.suggest_parallelization()
```

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    TestOrchestrator                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Discovery   │→ │ Classification│→ │  Scheduler   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Parallel Execution Engine                │  │
│  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ │  │
│  │  │ W1 │ │ W2 │ │ W3 │ │ W4 │ │ W5 │ │ W6 │ │ W7 │ │  │
│  │  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                              ↓                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Analytics & Monitoring                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 📈 Métricas Coletadas

Por execução:
- Timestamp
- Duração total
- Quantidade de testes (passou/falhou/erros)
- Taxa de sucesso
- Configuração (parallel/workers)

Por teste:
- Duração (min/max/média)
- Status
- Mensagem de erro
- Timestamp

## 🔄 CI/CD Integration

O workflow `.github/workflows/tests.yml` implementa:

1. **Job de Descoberta** - Identifica e classifica testes
2. **Unit Tests** - Executa testes unitários em paralelo (múltiplas versões Python)
3. **Integration Tests** - Executa testes de integração com credenciais reais
4. **CI Completo** - Executa todos os testes com orquestrador
5. **Performance Analysis** - Gera relatórios de performance
6. **Notificação** - Comenta no PR com resultados

## 🎨 Exemplos de Saída

```
🔍 Descobrindo testes...
✅ 6 testes descobertos
   unit: 6 testes

🚀 Iniciando execução de 6 testes...
   Paralelo: True
   Workers: 4
   Fail fast: False

[1/6] TestShopeeAPI.test_get_tipo_loja... ✅ 0.002s
[2/6] TestShopeeAPI.test_buscar_ofertas_lojas_query... ✅ 0.015s
[3/6] TestShopeeAPI.test_json_decode_error... ✅ 0.008s
[4/6] TestShopeeAPI.test_gerar_link_curto_success... ✅ 0.003s
[5/6] TestShopeeAPI.test_gerar_link_curto_failure... ✅ 0.002s
[6/6] TestShopeeAPI.test_gerar_link_curto_failure_none... ✅ 0.002s

============================================================
📊 RESUMO DA EXECUÇÃO
============================================================
Total:     6
✅ Passou:  6
❌ Falhou:  0
💥 Erros:   0
⏭️  Pulado:  0
⏱️  Duração: 0.03s
📈 Taxa:    100.0%
============================================================
```

## 🔍 Troubleshooting

### Testes não são descobertos
- Verifique se os arquivos começam com `test_`
- Verifique se os métodos começam com `test_`
- Verifique se as classes herdam de `unittest.TestCase`

### Execução paralela com erros
- Alguns testes podem não ser thread-safe
- Use `parallel_safe=False` nos metadados
- Testes com `requires_auth=True` são executados sequencialmente

### Analytics vazio
- O banco `test_analytics.db` é criado na primeira execução
- Execute testes algumas vezes para coletar dados

## 📚 Referências

- [Python unittest](https://docs.python.org/3/library/unittest.html)
- [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html)
- [GitHub Actions](https://docs.github.com/en/actions)
