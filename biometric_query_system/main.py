"""
main.py - Main entry point for the biometric query system
# Purpose:
- Provide command-line interface for the biometric system
- Handle different operation modes (sensor listener, simulation, testing)
- Integrate all system components
- Provide easy deployment and testing options
Created by: Guilherme (Python adaptation)
Version: 1.0.0
Date: 2025-09-11
"""

import argparse
import sys
import logging
from datetime import datetime
from typing import Optional
from config import config
from database import db_manager
from biometric_service import BiometricQueryService, simulate_sensor_input
from sensor_interface import SensorInterface, SensorSimulator

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.logging.level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=config.logging.file if config.logging.file else None
)

logger = logging.getLogger(__name__)


class BiometricSystemManager:
    """
    Main system manager for biometric access control
    Coordinates all system components and operation modes
    """
    
    def __init__(self):
        """Initialize system manager"""
        self.unit_code = "DEFAULT"
        logger.info("Biometric system manager initialized")
    
    def run_sensor_listener(self, unit_code: str, port: Optional[str] = None) -> None:
        """
        Run sensor listener mode for real R307 sensor
        
        Args:
            unit_code (str): School unit code
            port (Optional[str]): Serial port for sensor
        """
        print(f"\\n🔊 STARTING SENSOR LISTENER MODE")
        print(f"Unit Code: {unit_code}")
        print(f"Serial Port: {port or config.sensor.port}")
        print(f"Baudrate: {config.sensor.baudrate}")
        print("Press Ctrl+C to stop\\n")
        
        try:
            # Initialize sensor interface
            interface = SensorInterface(unit_code, port)
            
            # Test database connection
            if not interface.biometric_service.test_database_connection():
                print("❌ Database connection failed. Please check configuration.")
                return
            
            # Connect to sensor
            if not interface.connect_sensor():
                print("❌ Failed to connect to R307 sensor. Please check connection.")
                return
            
            print("✅ Sensor connected successfully")
            print("🎯 Listening for biometric queries...")
            
            # Start listening for commands
            interface.listen_for_commands()
            
        except KeyboardInterrupt:
            print("\\n🛑 Sensor listener stopped by user")
        except Exception as e:
            logger.error(f"Error in sensor listener: {e}")
            print(f"❌ Error: {e}")
    
    def run_simulation_mode(self, unit_code: str) -> None:
        """
        Run simulation mode for testing without physical sensor
        
        Args:
            unit_code (str): School unit code
        """
        print(f"\\n🧪 STARTING SIMULATION MODE")
        print(f"Unit Code: {unit_code}")
        
        try:
            # Run simulation tests
            simulator = SensorSimulator(unit_code)
            simulator.run_test_scenarios()
            
        except Exception as e:
            logger.error(f"Error in simulation mode: {e}")
            print(f"❌ Simulation error: {e}")
    
    def run_single_query(self, template: str, finger: str, unit_code: str) -> None:
        """
        Run single biometric query for testing
        
        Args:
            template (str): Base64 encoded biometric template
            finger (str): Finger type
            unit_code (str): School unit code
        """
        print(f"\\n🔍 RUNNING SINGLE BIOMETRIC QUERY")
        print(f"Unit Code: {unit_code}")
        print(f"Finger: {finger}")
        print(f"Template: {template[:50]}{'...' if len(template) > 50 else ''}")
        
        try:
            # Use the simulation function from biometric_service
            simulate_sensor_input(template, finger, unit_code)
            
        except Exception as e:
            logger.error(f"Error in single query: {e}")
            print(f"❌ Query error: {e}")
    
    def test_database_connection(self) -> None:
        """Test database connectivity"""
        print("\\n🔗 TESTING DATABASE CONNECTION")
        
        try:
            if db_manager.test_connection():
                print("✅ Database connection: SUCCESS")
                print(f"Database URL: {config.database.url}")
            else:
                print("❌ Database connection: FAILED")
                print("Please check your DATABASE_URL configuration")
                
        except Exception as e:
            logger.error(f"Database test error: {e}")
            print(f"❌ Database test error: {e}")
    
    def show_system_info(self) -> None:
        """Display system information"""
        print("\\n" + "="*60)
        print("📋 BIOMETRIC ACCESS CONTROL SYSTEM INFO")
        print("="*60)
        print(f"Version: 1.0.0")
        print(f"Created by: Arthur Roberto Weege Pontes")
        print(f"Date: 2025-09-11")
        print(f"Python Version: {sys.version}")
        print("\\n📊 CONFIGURATION:")
        print(f"  Database URL: {config.database.url}")
        print(f"  Sensor Device: {config.sensor.device}")
        print(f"  Sensor Port: {config.sensor.port}")
        print(f"  Sensor Baudrate: {config.sensor.baudrate}")
        print(f"  Log Level: {config.logging.level}")
        print(f"  Log File: {config.logging.file or 'Console only'}")
        print("="*60)


def main():
    """Main entry point with command-line interface"""
    parser = argparse.ArgumentParser(
        description="Biometric Access Control System for Schools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode listener --unit ETEC01
  python main.py --mode simulation --unit FATEC02
  python main.py --mode query --template "VGVzdA==" --finger index_right --unit ETEC01
  python main.py --mode test-db
  python main.py --mode info
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['listener', 'simulation', 'query', 'test-db', 'info'],
        required=True,
        help='Operation mode'
    )
    
    parser.add_argument(
        '--unit',
        default='DEFAULT',
        help='School unit code (default: DEFAULT)'
    )
    
    parser.add_argument(
        '--port',
        help='Serial port for R307 sensor (overrides config)'
    )
    
    parser.add_argument(
        '--template',
        help='Base64 encoded biometric template (for query mode)'
    )
    
    parser.add_argument(
        '--finger',
        help='Finger type (for query mode)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set verbose logging if requested
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize system manager
    manager = BiometricSystemManager()
    
    # Execute based on mode
    try:
        if args.mode == 'listener':
            manager.run_sensor_listener(args.unit, args.port)
            
        elif args.mode == 'simulation':
            manager.run_simulation_mode(args.unit)
            
        elif args.mode == 'query':
            if not args.template or not args.finger:
                print("❌ Error: --template and --finger are required for query mode")
                sys.exit(1)
            manager.run_single_query(args.template, args.finger, args.unit)
            
        elif args.mode == 'test-db':
            manager.test_database_connection()
            
        elif args.mode == 'info':
            manager.show_system_info()
            
    except KeyboardInterrupt:
        print("\\n🛑 System stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"System error: {e}")
        print(f"❌ System error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

