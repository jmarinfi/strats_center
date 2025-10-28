# Strats Center

Sistema de trading algorítmico basado en eventos para backtesting y trading en vivo, con arquitectura modular y extensible.

## 🏗️ Arquitectura

El sistema utiliza un **Event Bus** síncrono para la comunicación entre componentes:

```text
Data Handler → MarketEvent → Strategy → SignalEvent → Order Manager → OrderEvent → Execution → FillEvent → Portfolio
```

### Componentes Principales

- Event Bus: Núcleo de comunicación entre componentes
- Data Handlers: Gestión de datos históricos y en tiempo real
- Models: Eventos y estructuras de datos
- Configuration: Sistema de configuración flexible

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
├── config/                 # Archivos de configuración YAML
│   └── strategy_config.yaml
├── data/                   # Handlers de datos y loaders
│   ├── __init__.py
│   ├── i_data_handler.py   # Interfaz para data handlers
│   ├── historic_csv_data_handler.py  # Handler para datos históricos CSV
│   ├── loaders/            # Data loaders para diferentes exchanges
│   │   ├── __init__.py
│   │   ├── i_data_loader.py
│   │   └── binance_csv_loader.py
├── event_bus/              # Sistema de eventos
│   ├── __init__.py
│   ├── event_bus.py        # EventBus principal
│   ├── handlers.py         # Registry y handlers base
│   └── exceptions.py       # Excepciones específicas
├── models/                 # Modelos de datos y configuración
│   ├── __init__.py
│   ├── config.py           # Configuración del sistema (Pydantic)
│   ├── enums.py            # Enumeraciones del sistema
│   └── events.py           # Modelos de eventos
├── strategies/             # Estrategias de trading
│   ├── __init__.py
│   ├── base_strategy.py    # Clase base para estrategias
│   └── simple_price_strategy.py  # Estrategia de ejemplo
├── tests/                  # Tests unitarios e integración
│   ├── __init__.py
│   ├── test_enums.py
│   ├── test_events.py
│   ├── test_data_handler.py
│   ├── test_data_loader.py
├── backtest_data/          # Datos para backtesting
├── logs/                   # Archivos de log
├── main.py                 # Punto de entrada principal
├── pyproject.toml          # Configuración del proyecto
└── README.md
```

## 🔧 Event Bus

### Uso Básico

```python
from event_bus import EventBus, EventHandlerRegistry, BaseEventHandler
from models.events import MarketEvent
from models.enums import EventType
from datetime import datetime

# Crear Event Bus
registry = EventHandlerRegistry()
event_bus = EventBus(registry, max_history=100)

# Crear handler
class MyHandler(BaseEventHandler):
    @property
    def supported_events(self):
        return {EventType.MARKET}
    
    def handle(self, event):
        print(f"Recibido: {event.type}")

# Registrar y usar
handler = MyHandler()
registry.register_handler(handler)

# Publicar evento
event = MarketEvent(symbol="BTCUSDT", timestamp=datetime.now())
event_bus.publish(event)
```

### Características

- Síncrono: Procesamiento inmediato de eventos
- Tolerante a fallos: Errores en handlers no tumban el sistema
- Historial opcional: Debugging y análisis
- Estadísticas: Métricas de rendimiento

## 📊 Modelos de Eventos

| Evento | Descripción | Atributos principales |
|--------|-------------|----------------------|
| **MarketEvent** | Datos de mercado (OHLCV) | `symbol`, `timestamp`, `data` |
| **SignalEvent** | Señales de trading | `symbol`, `timestamp`, `signal_type` |
| **OrderEvent** | Órdenes de trading | `symbol`, `order_type`, `quantity`, `direction`, `timestamp`, `price` |
| **FillEvent** | Ejecuciones completadas | `timestamp`, `symbol`, `exchange`, `quantity`, `direction`, `fill_cost`, `commission` |
| **PortfolioEvent** | Actualizaciones de portafolio | `timestamp`, `total_value`, `cash`, `positions` |
| **BacktestEvent** | Control de backtesting | `action`, `timestamp`, `message` |
| **ErrorEvent** | Errores del sistema | `timestamp`, `source`, `error_type`, `message`, `details` |

### Tipos de Señales

- `LONG`: Señal de entrada en posición larga
- `SHORT`: Señal de entrada en posición corta
- `EXIT`: Señal de salida de posición

### Tipos de Órdenes

- `MARKET`: Orden a mercado
- `LIMIT`: Orden limitada

### Direcciones de Órdenes

- `BUY`: Compra
- `SELL`: Venta

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests específicos
pytest tests/test_event_bus.py
pytest tests/test_integration_*
```

## 📈 Configuración

El sistema utiliza archivos YAML para configuración:

```yaml
# config/settings.yaml
events:
  max_history: 1000
  enable_logging: true

data:
  default_source: "csv"
  cache_enabled: true
```

## 🛣️ Roadmap

### ✅ Completado

- [x] **Event Bus síncrono** con registry de handlers
- [x] **Modelos de eventos completos** (Market, Signal, Order, Fill, Portfolio, Backtest, Error)
- [x] **Sistema de configuración** con Pydantic y archivos YAML
- [x] **Data handlers** para CSV histórico (Binance)
- [x] **Estrategias base** con SimplePriceStrategy de ejemplo
- [x] **Tests unitarios** completos para todos los componentes
- [x] **Sistema de logging** configurable
- [x] **Arquitectura modular** con paquetes organizados

### 🚧 En Desarrollo

- [ ] **Motor de backtesting** completo
- [ ] **Gestión de órdenes** (Order Manager)
- [ ] **Seguimiento de portfolio** en tiempo real
- [ ] **Conexión a APIs** de exchanges en vivo
- [ ] **Persistencia de datos** en base de datos
- [ ] **Dashboard web** para monitoreo
- [ ] **Optimización de estrategias**

### 🔮 Planificado

- [ ] **Trading en vivo** con ejecución real
- [ ] **Análisis de rendimiento** avanzado
- [ ] **Machine Learning** integration
- [ ] **Multi-asset** support
- [ ] **Risk management** avanzado
- [ ] **API REST** para integración externa

## 🔍 Estado Actual

### ✅ **Funcionalidades Implementadas**

#### 🚌 Event Bus Completo

- EventBus síncrono con historial configurable
- Registry de handlers con soporte para múltiples tipos de eventos
- Sistema de excepciones específico para event bus
- Handlers base y función helper para crear handlers simples

#### 📊 Modelos de Datos

- 7 tipos de eventos completos (Market, Signal, Order, Fill, Portfolio, Backtest, Error)
- Enumeraciones para tipos de señales, órdenes y direcciones
- Sistema de configuración completo con Pydantic
- Validación automática de datos

#### 💾 Data Management

- Data handler para datos históricos CSV
- Loader específico para formato Binance
- Interfaz extensible para nuevos sources de datos
- Normalización automática de datos

#### 🎯 Sistema de Estrategias

- Clase base abstracta para estrategias
- SimplePriceStrategy como ejemplo funcional
- Integración completa con Event Bus
- Patrón extensible para nuevas estrategias

#### 🧪 Testing Completo

- Tests unitarios para todos los componentes
- Tests de integración end-to-end
- Cobertura completa de modelos y lógica de negocio
- Framework de testing con pytest

#### ⚙️ Configuración y Logging

- Sistema de configuración YAML flexible
- Logging configurable con múltiples handlers
- Validación de configuración en tiempo real
- Manejo de errores robusto

### 🚀 **Ejemplo Funcional**

El sistema incluye un ejemplo completo (`setup_and_run_simple_strategy_example`) que demuestra:

- Configuración del Event Bus
- Registro de estrategias
- Procesamiento de eventos de mercado
- Generación de señales de trading
- Verificación de resultados

### 📈 **Arquitectura Sólida**

- **DDD/EDA**: Domain-Driven Design con Event-Driven Architecture
- **Modular**: Componentes desacoplados e intercambiables
- **Extensible**: Fácil agregar nuevas estrategias, data sources y handlers
- **Type-safe**: Validación completa con Pydantic
- **Testable**: Cobertura completa con tests automatizados

## 📄 Licencia

MIT License - ver LICENSE para detalles.
