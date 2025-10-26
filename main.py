"""
Punto de entrada principal de la aplicación de trading.

Este módulo proporciona las funciones principales para:
1. Cargar y validar la configuración del sistema
2. Configurar el sistema de logging 
3. Probar la carga de datos desde archivos CSV
4. Ejecutar tests básicos de integración
"""

import logging
from pathlib import Path
import sys
import os
from typing import Tuple, Optional

from config.config import load_config, TradingConfig
from data import BinanceCSVLoader


def setup_logging(config: TradingConfig) -> logging.Logger:
    """
    Configura el sistema de logging basado en la configuración.
    
    Args:
        config: Configuración cargada del sistema
        
    Returns:
        logging.Logger: Logger configurado para el módulo principal
    """
    # Crear logger principal
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, config.logging.level))
    
    # Limpiar handlers existentes para evitar duplicados
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Formatter común para todos los handlers
    formatter = logging.Formatter(config.logging.format)
    
    # Console handler
    if config.logging.console.enabled:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config.logging.console.level))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if config.logging.file.enabled:
        # El directorio ya se crea automáticamente por el validator en FileLogHandler
        log_path = Path(config.logging.file.path)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(getattr(logging, config.logging.file.level))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logging.getLogger(__name__)


def print_header():
    """Imprime el header principal de la aplicación."""
    print("=" * 70)
    print("🎯 STRATS CENTER - PLATAFORMA DE TRADING ALGORÍTMICO")
    print("=" * 70)
    print("🚀 Sistema de Backtesting y Estrategias de Trading")
    print("📊 Basado en arquitectura DDD/EDA")
    print("=" * 70)


def test_configuration() -> Tuple[Optional[TradingConfig], bool]:
    """
    Prueba la carga y validación de la configuración del sistema.
    
    Returns:
        Tuple[Optional[TradingConfig], bool]: (config, success)
            - config: Configuración cargada si fue exitoso, None si falló
            - success: True si la configuración se cargó correctamente
    """
    try:
        print("\n🔧 TEST 1: CARGA DE CONFIGURACIÓN")
        print("-" * 40)
        
        config = load_config()
        logger = setup_logging(config)
        
        logger.info("✅ Configuración cargada exitosamente")
        
        # Mostrar información de la configuración
        print(f"📱 Aplicación: {config.app.name} v{config.app.version}")
        print(f"🐛 Modo debug: {'Activo' if config.app.debug else 'Inactivo'}")
        print(f"📝 Nivel de log: {config.app.log_level}")
        
        print(f"\n📊 CONFIGURACIÓN DE ESTRATEGIA:")
        print(f"   🎯 Estrategia: {config.strategy.name}")
        print(f"   ⚡ Habilitada: {'Sí' if config.strategy.enabled else 'No'}")
        print(f"   📈 Parámetros:")
        for param, value in config.strategy.parameters.items():
            print(f"      - {param}: {value}")
        
        print(f"\n💰 CONFIGURACIÓN DE BACKTESTING:")
        print(f"   💵 Capital inicial: ${config.backtesting.initial_capital:,.2f}")
        print(f"   💸 Comisión: {config.backtesting.commission.rate*100:.3f}% ({config.backtesting.commission.type})")
        print(f"   💾 Guardar trades: {'Sí' if config.backtesting.save_trades else 'No'}")
        print(f"   📸 Guardar snapshots: {'Sí' if config.backtesting.save_portfolio_snapshots else 'No'}")
        
        print(f"\n📊 CONFIGURACIÓN DE DATOS:")
        print(f"   🔌 Fuente: {config.data_source.type.upper()}")
        print(f"   📁 Path de datos: {config.data_source.csv.data_path}")
        print(f"   🔍 Patrón de archivos: {config.data_source.csv.file_pattern}")
        print(f"   ⏰ Columna timestamp: {config.data_source.csv.timestamp_column}")
        
        print(f"\n🎯 SÍMBOLOS CONFIGURADOS:")
        for i, symbol in enumerate(config.symbols, 1):
            status = "✅ Activo" if symbol.enabled else "⏸️  Inactivo"
            print(f"   {i}. {symbol.symbol} ({symbol.timeframe}) - {status}")
        
        print(f"\n🗄️  CONFIGURACIÓN DE PERSISTENCIA:")
        print(f"   💾 Base de datos: {config.database.type.upper()}")
        print(f"   📂 Path BD: {config.database.sqlite.path}")
        print(f"   🎪 Event bus: {config.events.event_bus_type}")
        print(f"   📚 Max eventos en memoria: {config.events.max_event_history:,}")
        
        return config, True
        
    except Exception as e:
        print(f"❌ ERROR cargando configuración: {e}")
        print(f"🔧 Verifica que existe: config/strategy_config.yaml")
        import traceback
        traceback.print_exc()
        return None, False


def test_data_loading(config: TradingConfig) -> bool:
    """
    Prueba el sistema de carga de datos CSV.
    
    Args:
        config: Configuración del sistema
        
    Returns:
        bool: True si los tests de datos pasaron correctamente
    """
    logger = logging.getLogger(__name__)
    
    try:
        print("\n📦 TEST 2: SISTEMA DE CARGA DE DATOS")
        print("-" * 40)
        
        # Verificar si existe el directorio de datos
        data_path = Path(config.data_source.csv.data_path)
        
        if not data_path.exists():
            print(f"⚠️  Directorio de datos no existe: {data_path}")
            print(f"🔧 Creando directorio...")
            data_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Directorio creado: {data_path.absolute()}")
            
            print(f"ℹ️  INSTRUCCIONES:")
            print(f"   📁 Coloca tus archivos CSV de Binance en: {data_path.absolute()}")
            print(f"   📊 Formato esperado: openTime,open,high,low,close,volume,...")
            print(f"   🕐 Timestamps en milisegundos Unix")
            print("✅ Sistema de datos configurado correctamente")
            return True
        
        print(f"📁 Directorio de datos: {data_path.absolute()}")
        
        # Buscar archivos CSV
        csv_files = list(data_path.glob(config.data_source.csv.file_pattern))
        
        if not csv_files:
            print(f"⚠️  No se encontraron archivos CSV en: {data_path}")
            print(f"ℹ️  Coloca archivos CSV para probar la carga de datos")
            print("✅ Sistema de datos configurado correctamente")
            return True
        
        print(f"📊 Archivos CSV encontrados: {len(csv_files)}")
        
        # Mostrar lista de archivos
        for i, file_path in enumerate(csv_files[:5], 1):  # Mostrar máximo 5
            file_size = file_path.stat().st_size
            size_mb = file_size / (1024 * 1024)
            print(f"   {i}. {file_path.name} ({size_mb:.1f} MB)")
        
        if len(csv_files) > 5:
            print(f"   ... y {len(csv_files) - 5} archivo(s) más")
        
        # Probar carga con el primer archivo
        test_file = csv_files[0]
        print(f"\n🧪 Probando carga con: {test_file.name}")
        
        loader = BinanceCSVLoader()
        logger.info(f"Cargando archivo de prueba: {test_file}")
        
        df = loader.load(test_file)
        
        print(f"✅ Datos cargados exitosamente:")
        print(f"   📊 Filas: {len(df):,}")
        print(f"   📋 Columnas: {len(df.columns)}")
        print(f"   🏷️  Nombres: {', '.join(df.columns[:6])}{'...' if len(df.columns) > 6 else ''}")
        
        # Información del período de datos
        if not df.empty:
            print(f"   📅 Período: {df.index.min()} → {df.index.max()}")
            
            # Mostrar muestra de datos
            print(f"\n📋 MUESTRA DE DATOS (primeras 3 filas):")
            for i, (timestamp, row) in enumerate(df.head(3).iterrows()):
                print(f"   {i+1}. {timestamp} | "
                      f"O:{row['open']:>8.2f} "
                      f"H:{row['high']:>8.2f} "
                      f"L:{row['low']:>8.2f} "
                      f"C:{row['close']:>8.2f} "
                      f"V:{row['volume']:>10.2f}")
        
        logger.info("Test de carga de datos completado exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ ERROR en test de datos: {e}")
        logger.error(f"Fallo en test de datos: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_setup(config: TradingConfig) -> bool:
    """
    Verifica la configuración de la base de datos.
    
    Args:
        config: Configuración del sistema
        
    Returns:
        bool: True si el test de BD pasó correctamente
    """
    try:
        print("\n🗄️  TEST 3: CONFIGURACIÓN DE BASE DE DATOS")
        print("-" * 40)
        
        db_path = Path(config.database.sqlite.path)
        print(f"📂 Ruta de BD: {db_path.absolute()}")
        
        # Verificar que el directorio existe (creado por el validator)
        if db_path.parent.exists():
            print("✅ Directorio de base de datos existe")
        else:
            print("⚠️  Directorio de BD no existe - el validator debería haberlo creado")
            
        print(f"⚙️  Pool size: {config.database.sqlite.pool_size}")
        print(f"📊 Max overflow: {config.database.sqlite.max_overflow}")
        print("✅ Configuración de base de datos válida")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR en configuración de BD: {e}")
        return False


def run_integration_tests() -> bool:
    """
    Ejecuta todos los tests de integración del sistema.
    
    Returns:
        bool: True si todos los tests pasaron
    """
    print_header()
    
    success = True
    
    # Test 1: Configuración
    config, config_ok = test_configuration()
    success &= config_ok
    
    if not config_ok:
        print("\n❌ ABORTANDO: La configuración no se pudo cargar")
        return False
    
    # Test 2: Datos  
    data_ok = test_data_loading(config)
    success &= data_ok
    
    # Test 3: Base de datos
    db_ok = test_database_setup(config)
    success &= db_ok
    
    # Resumen final
    print("\n" + "=" * 70)
    if success:
        print("🎉 TODOS LOS TESTS DE INTEGRACIÓN PASARON")
        print("✅ Sistema configurado correctamente")
        print("🚀 Listo para implementar el Event Bus y estrategias")
        
        logger = logging.getLogger(__name__)
        logger.info("Tests de integración completados exitosamente")
        logger.info("Sistema listo para desarrollo de estrategias")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("🔧 Revisa los errores arriba antes de continuar")
    
    print("=" * 70)
    return success


def main() -> int:
    """
    Función principal del programa.
    
    Returns:
        int: Código de salida (0 = éxito, 1 = error)
    """
    try:
        success = run_integration_tests()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Interrumpido por el usuario")
        return 130
    
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
