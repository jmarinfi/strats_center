# Strats Center

Sistema de trading algorítmico basado en eventos para backtesting y trading en vivo, con arquitectura modular y extensible.

## 🏗️ Arquitectura

El sistema utiliza un **Event Bus** síncrono para la comunicación entre componentes:

```
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

```
strats_center/
├── config/                 # Configuración del sistema
├── data/                   # Handlers de datos (CSV, APIs)
├── event_bus/              # Sistema de eventos
│   ├── event_bus.py        # EventBus principal
│   ├── handlers.py         # Registry y handlers base
│   └── exceptions.py       # Excepciones específicas
├── models/                 # Modelos de datos y eventos
│   ├── events.py           # Eventos del sistema
│   └── enums.py            # Enumeraciones
└── tests/                  # Tests unitarios e integración
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

| Evento | Descripción | Uso |
|--------|-------------|-----|
| MarketEvent | Datos de mercado (OHLCV) | Alimentar estrategias |
| SignalEvent | Señales de trading | Generar órdenes |
| OrderEvent | Órdenes de trading | Ejecutar operaciones |
| FillEvent | Ejecuciones completadas | Actualizar portfolio |
| ErrorEvent | Errores del sistema | Logging y debugging |

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

- [x] Event Bus básico
- [x] Data handlers (CSV)
- [x] Modelos de eventos
- [ ] Sistema de estrategias
- [ ] Order management
- [ ] Portfolio tracking
- [ ] Backtesting engine
- [ ] Live trading

## 🔍 Estado Actual

✅ Completado:
- Event Bus síncrono con registry
- Modelos de eventos y enums
- Data handler para CSV histórico
- Sistema de configuración
- Tests unitarios e integración

🚧 En desarrollo:
- Componentes de estrategias
- Motor de backtesting
- Gestión de órdenes

## 📄 Licencia

MIT License - ver LICENSE para detalles.
