# 🎯 Strats Center

Sistema de trading algorítmico basado en eventos para backtesting y trading en vivo, con arquitectura modular y extensible.

## 🏗️ Arquitectura

El sistema utiliza un Event Bus síncrono para la comunicación entre componentes. La arquitectura está diseñada para ser modular y desacoplada, permitiendo que cada componente se centre en una única responsabilidad.

### Flujo de Eventos Principal

El flujo de un backtest sigue esta secuencia de eventos:

```text
Data Handler → MarketEvent → Strategy → SignalEvent → Order Manager → OrderEvent → Broker → FillEvent → Portfolio
```

### Componentes Principales

- **EventBus**: El núcleo de comunicación síncrono que distribuye eventos.
- **DataHandler**: Lee datos (ej. CSV) y publica MarketEvent.
- **Strategy**: Escucha MarketEvent, aplica lógica y publica SignalEvent.
- **Portfolio**: Escucha FillEvent y actualiza el estado (efectivo, posiciones).
- **OrderManager**: Escucha SignalEvent, consulta IPortfolio y ISizer, y publica OrderEvent.
- **Sizer**: Calcula la cantidad (tamaño) de la orden. Es una dependencia del OrderManager.
- **Broker**: Escucha OrderEvent, simula la ejecución y publica FillEvent.
- **BacktestEngine**: Orquesta el bucle de backtesting, pasando los MarketEvent al EventBus.
- **Models**: Define todos los eventos, enumeraciones y modelos de configuración con Pydantic.
- **Config**: Carga y valida la configuración del sistema desde archivos YAML.

## 🚀 Instalación

```bash
# Clonar repositorio
git clone https://github.com/jmarinfi/strats_center.git
cd strats_center

# Instalar dependencias (requiere uv)
uv sync
```

## 📁 Estructura del Proyecto

```text
strats_center/
├── backtest/       # Motor de backtesting y broker simulado
├── broker/         # Interfaces para brokers (ejecución)
├── config/         # Archivos de configuración YAML
├── data/           # Handlers de datos y loaders
├── event_bus/      # Sistema de eventos (núcleo)
├── models/         # Modelos de datos, eventos y configuración
├── order_manager/  # Lógica de gestión de órdenes
├── portfolio/      # Lógica de seguimiento de portafolio
├── sizing/         # Lógica de dimensionamiento de órdenes
├── strategies/     # Estrategias de trading
├── tests/          # Tests unitarios e integración
├── main.py         # Punto de entrada principal
└── pyproject.toml
```

## 🔧 Modelos de Eventos

| Evento         | Origen      | Destino(s) Habituales | Descripción                                    |
|----------------|-------------|------------------------|------------------------------------------------|
| MarketEvent    | DataHandler | Strategy, Broker       | Nuevos datos de mercado (OHLCV).               |
| SignalEvent    | Strategy    | OrderManager           | Intención de operar (LONG, SHORT, EXIT).       |
| OrderEvent     | OrderManager| Broker                 | Orden concreta para ejecutar (MARKET, LIMIT).  |
| FillEvent      | Broker      | Portfolio              | Confirmación de orden ejecutada.               |
| PortfolioEvent | Portfolio   | (N/A)                  | Actualización del estado del portafolio.       |
| ErrorEvent     | (Cualquiera)| (N/A)                  | Reporte de errores del sistema.                |

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests específicos
pytest tests/test_event_bus.py
pytest tests/test_integration_*
```

## 📈 Configuración

El sistema utiliza `config/strategy_config.yaml` para la configuración, validado por Pydantic (`models/config.py`). Incluye una nueva sección sizing para controlar el tamaño de las órdenes:

```yaml
strategy:
  name: "simple_price_strategy"
  # ...
  sizing:
    type: "fixed"  # Opciones: "fixed", "percentage"
    value: 0.1     # 0.1 unidades si es "fixed"
```

## 🛣️ Roadmap

### ✅ Completado (v1)

- [x] Event Bus síncrono con registry de handlers.
- [x] Modelos de eventos completos (Market, Signal, Order, Fill).
- [x] Sistema de configuración con Pydantic y YAML.
- [x] Data handlers para CSV histórico (Binance).
- [x] Estrategias base (SimplePriceStrategy de ejemplo).
- [x] Gestión de Órdenes (SimpleOrderManager).
- [x] Seguimiento de Portfolio (SimplePortfolio).
- [x] Gestión de Sizing (FixedQuantitySizer).
- [x] Broker Simulado (SimulatedBroker).
- [x] Tests unitarios e integración para componentes clave.
- [x] Arquitectura modular (EDA/DDD) y extensible.

### 🚧 En Desarrollo

- [ ] Motor de backtesting (Ensamblaje final en main.py).
- [ ] Generación de Reportes de backtesting.
- [ ] Persistencia de datos (Guardar trades en BD).
- [ ] Conexión a APIs de exchanges en vivo.

### 🔮 Planificado

- [ ] Trading en vivo con ejecución real.
- [ ] Análisis de rendimiento avanzado (métricas, gráficos).
- [ ] Dashboard web para monitoreo.
- [ ] Optimización de estrategias.
- [ ] Gestión de Riesgo avanzada (Stop Loss, Take Profit a nivel de Portfolio).

## 📄 Licencia

MIT License
