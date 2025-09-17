"""
sensor_interface.py - Interface for R307 sensor communication
# Purpose:
- Handle communication protocol with R307 biometric sensor
- Process sensor commands and responses
- Integrate with biometric query service
- Provide real-time access control responses
Created by: Guilherme (Python adaptation)
Version: 1.0.0
Date: 2025-09-11
"""

import serial
import time
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from biometric_service import BiometricQueryService
from config import config

# Configure logging
logger = logging.getLogger(__name__)


class SensorInterface:
    """
    Interface for R307 biometric sensor communication
    Handles serial communication and command processing
    """
    
    def __init__(self, unit_code: str = "DEFAULT", port: Optional[str] = None, 
                 baudrate: Optional[int] = None):
        """
        Initialize sensor interface
        
        Args:
            unit_code (str): School unit code
            port (Optional[str]): Serial port for sensor communication
            baudrate (Optional[int]): Serial communication speed
        """
        self.unit_code = unit_code
        self.port = port or config.sensor.port
        self.baudrate = baudrate or config.sensor.baudrate
        self.serial_connection = None
        self.biometric_service = BiometricQueryService(unit_code)
        
        logger.info(f"Sensor interface initialized for unit: {unit_code}")
        logger.info(f"Serial port: {self.port}, Baudrate: {self.baudrate}")
    
    def connect_sensor(self) -> bool:
        """
        Establish connection with R307 sensor
        
        Returns:
            bool: True if connection successful
        """
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=5,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            
            logger.info(f"Sensor connected successfully on {self.port}")
            return True
            
        except serial.SerialException as e:
            logger.error(f"Failed to connect to sensor: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to sensor: {e}")
            return False
    
    def disconnect_sensor(self) -> None:
        """Disconnect from R307 sensor"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logger.info("Sensor disconnected")
    
    def listen_for_commands(self) -> None:
        """
        Main loop to listen for sensor commands
        Processes biometric queries and sends responses
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            logger.error("Sensor not connected. Call connect_sensor() first.")
            return
        
        logger.info("Starting sensor command listener...")
        
        try:
            while True:
                # Check for incoming data from sensor
                if self.serial_connection.in_waiting > 0:
                    command = self._read_sensor_command()
                    if command:
                        response = self._process_command(command)
                        self._send_response(response)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("Sensor listener stopped by user")
        except Exception as e:
            logger.error(f"Error in sensor listener: {e}")
        finally:
            self.disconnect_sensor()
    
    def _read_sensor_command(self) -> Optional[Dict[str, Any]]:
        """
        Read and parse command from R307 sensor
        
        Returns:
            Optional[Dict]: Parsed command data
        """
        try:
            # Read data from sensor
            raw_data = self.serial_connection.readline().decode('utf-8').strip()
            
            if not raw_data:
                return None
            
            logger.debug(f"Raw sensor data received: {raw_data}")
            
            # Parse command (assuming format: COMMAND:TEMPLATE:FINGER)
            parts = raw_data.split(':')
            
            if len(parts) >= 3:
                command = {
                    'type': parts[0],
                    'template': parts[1],
                    'finger': parts[2],
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.info(f"Command parsed: {command['type']} for finger {command['finger']}")
                return command
            else:
                logger.warning(f"Invalid command format: {raw_data}")
                return None
                
        except Exception as e:
            logger.error(f"Error reading sensor command: {e}")
            return None
    
    def _process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process sensor command and generate response
        
        Args:
            command (Dict): Parsed sensor command
        
        Returns:
            Dict: Response data for sensor
        """
        try:
            command_type = command.get('type', '').upper()
            
            if command_type == 'QUERY' or command_type == 'VERIFY':
                # Process biometric query
                template = command.get('template', '')
                finger = command.get('finger', '')
                
                logger.info(f"Processing biometric query: finger={finger}")
                
                # Query biometric service
                result = self.biometric_service.process_biometric_query(template, finger)
                
                # Add timestamp to result
                result['timestamp'] = command.get('timestamp')
                
                return result
                
            elif command_type == 'TEST':
                # Test command
                return {
                    'access_granted': True,
                    'result': 'TEST_OK',
                    'timestamp': command.get('timestamp'),
                    'unit_code': self.unit_code,
                    'device': config.sensor.device,
                    'person': None
                }
                
            else:
                # Unknown command
                logger.warning(f"Unknown command type: {command_type}")
                return {
                    'access_granted': False,
                    'result': 'UNKNOWN_COMMAND',
                    'error': f'Unknown command: {command_type}',
                    'timestamp': command.get('timestamp'),
                    'unit_code': self.unit_code,
                    'device': config.sensor.device,
                    'person': None
                }
                
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return {
                'access_granted': False,
                'result': 'ERROR',
                'error': str(e),
                'timestamp': command.get('timestamp'),
                'unit_code': self.unit_code,
                'device': config.sensor.device,
                'person': None
            }
    
    def _send_response(self, response: Dict[str, Any]) -> None:
        """
        Send response back to R307 sensor
        
        Args:
            response (Dict): Response data
        """
        try:
            # Create simple response for sensor (YES/NO)
            sensor_response = "YES" if response.get('access_granted', False) else "NO"
            
            # Send response to sensor
            self.serial_connection.write(f"{sensor_response}\\n".encode('utf-8'))
            self.serial_connection.flush()
            
            logger.info(f"Response sent to sensor: {sensor_response}")
            
            # Log detailed response for debugging
            if response.get('person'):
                person = response['person']
                logger.info(f"Access granted for: {person['name']} (CPF: {person['cpf']})")
            elif response.get('error'):
                logger.warning(f"Access denied - Error: {response['error']}")
            else:
                logger.info("Access denied - No matching biometric found")
                
        except Exception as e:
            logger.error(f"Error sending response to sensor: {e}")
    
    def simulate_sensor_query(self, template_base64: str, finger: str) -> Dict[str, Any]:
        """
        Simulate a sensor query for testing purposes
        
        Args:
            template_base64 (str): Base64 encoded biometric template
            finger (str): Finger type
        
        Returns:
            Dict: Query result
        """
        logger.info("=== SIMULATING SENSOR QUERY ===")
        
        # Create simulated command
        command = {
            'type': 'QUERY',
            'template': template_base64,
            'finger': finger,
            'timestamp': datetime.now().isoformat()
        }
        
        # Process command
        response = self._process_command(command)
        
        # Log result
        sensor_response = "YES" if response.get('access_granted', False) else "NO"
        logger.info(f"Simulated sensor response: {sensor_response}")
        
        return response


class SensorSimulator:
    """
    Simulator for R307 sensor for testing without physical hardware
    """
    
    def __init__(self, unit_code: str = "ETEC01"):
        """
        Initialize sensor simulator
        
        Args:
            unit_code (str): School unit code
        """
        self.unit_code = unit_code
        self.interface = SensorInterface(unit_code)
        logger.info(f"Sensor simulator initialized for unit: {unit_code}")
    
    def run_test_scenarios(self) -> None:
        """Run various test scenarios"""
        print("\\n" + "="*60)
        print("🔬 RUNNING R307 SENSOR SIMULATION TESTS")
        print("="*60)
        
        # Test database connection
        print("\\n1. Testing database connection...")
        if self.interface.biometric_service.test_database_connection():
            print("✅ Database connection: SUCCESS")
        else:
            print("❌ Database connection: FAILED")
            return
        
        # Test scenarios
        test_cases = [
            {
                'name': 'Valid biometric template',
                'template': 'VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YQ==',  # Base64: "Test biometric template data"
                'finger': 'index_right'
            },
            {
                'name': 'Invalid finger type',
                'template': 'VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YQ==',
                'finger': 'invalid_finger'
            },
            {
                'name': 'Empty template',
                'template': '',
                'finger': 'thumb_left'
            },
            {
                'name': 'Invalid base64 template',
                'template': 'invalid_base64_data!!!',
                'finger': 'middle_right'
            }
        ]
        
        for i, test_case in enumerate(test_cases, 2):
            print(f"\\n{i}. Testing: {test_case['name']}")
            print(f"   Finger: {test_case['finger']}")
            print(f"   Template: {test_case['template'][:30]}{'...' if len(test_case['template']) > 30 else ''}")
            
            try:
                result = self.interface.simulate_sensor_query(
                    test_case['template'], 
                    test_case['finger']
                )
                
                print(f"   Result: {result['result']}")
                print(f"   Access: {'✅ GRANTED' if result['access_granted'] else '❌ DENIED'}")
                
                if result.get('error'):
                    print(f"   Error: {result['error']}")
                
                if result.get('person'):
                    person = result['person']
                    print(f"   Person: {person['name']} (CPF: {person['cpf']})")
                
            except Exception as e:
                print(f"   ❌ Test failed: {e}")
        
        print("\\n" + "="*60)
        print("🏁 SIMULATION TESTS COMPLETED")
        print("="*60)


if __name__ == "__main__":
    # Run sensor simulation tests
    simulator = SensorSimulator("ETEC01")
    simulator.run_test_scenarios()

