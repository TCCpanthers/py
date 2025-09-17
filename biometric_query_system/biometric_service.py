"""
biometric_service.py - Main biometric query service for R307 sensor integration
# Purpose:
- Process biometric data received from R307 sensor
- Query database for matching biometric templates
- Return access authorization (yes/no) to sensor
- Log all access attempts for security audit
Created by: Guilherme (Python adaptation)
Version: 1.0.0
Date: 2025-09-11
"""

import base64
import logging
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from database import db_manager
from config import config

# Configure logging
logger = logging.getLogger(__name__)


class AccessResult(Enum):
    """Access authorization results"""
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    ERROR = "ERROR"


class FingerType(Enum):
    """Supported finger types for biometric recognition"""
    THUMB_RIGHT = "thumb_right"
    INDEX_RIGHT = "index_right"
    MIDDLE_RIGHT = "middle_right"
    RING_RIGHT = "ring_right"
    PINKY_RIGHT = "pinky_right"
    THUMB_LEFT = "thumb_left"
    INDEX_LEFT = "index_left"
    MIDDLE_LEFT = "middle_left"
    RING_LEFT = "ring_left"
    PINKY_LEFT = "pinky_left"


class BiometricQueryService:
    """
    Main service for biometric queries and access control
    Integrates with R307 sensor and school database
    """
    
    def __init__(self, unit_code: str = "DEFAULT"):
        """
        Initialize biometric query service
        
        Args:
            unit_code (str): School unit code for access logging
        """
        self.unit_code = unit_code
        self.unit_info = None
        self._initialize_unit()
        logger.info(f"Biometric query service initialized for unit: {unit_code}")
    
    def _initialize_unit(self) -> None:
        """Initialize and validate unit information"""
        try:
            self.unit_info = db_manager.get_unit_by_code(self.unit_code)
            if not self.unit_info:
                logger.warning(f"Unit not found for code: {self.unit_code}")
                # Create a default unit entry for logging purposes
                self.unit_info = {
                    'id': 1,  # Default unit ID
                    'name': 'Default Unit',
                    'unit_code': self.unit_code
                }
        except Exception as e:
            logger.error(f"Error initializing unit: {e}")
            raise
    
    def process_biometric_query(self, template_base64: str, finger: str) -> Dict[str, Any]:
        """
        Main method to process biometric query from R307 sensor
        
        Args:
            template_base64 (str): Base64 encoded biometric template from sensor
            finger (str): Finger type used for biometric reading
        
        Returns:
            Dict containing access result and person information
        """
        logger.info(f"Processing biometric query for finger: {finger}")
        
        try:
            # Validate input parameters
            validation_result = self._validate_input(template_base64, finger)
            if not validation_result['valid']:
                return self._create_error_response(validation_result['error'])
            
            # Convert base64 template to binary data
            template_data = self._convert_template(template_base64)
            
            # Search for matching biometric in database
            person_info = db_manager.find_biometric_by_template(template_data, finger)
            
            # Determine access result
            if person_info:
                access_result = AccessResult.GRANTED
                logger.info(f"Access GRANTED for {person_info['full_name']} (CPF: {person_info['cpf']})")
            else:
                access_result = AccessResult.DENIED
                logger.info("Access DENIED - No matching biometric found")
            
            # Log access attempt
            self._log_access_attempt(person_info, access_result)
            
            # Return response for sensor
            return self._create_response(access_result, person_info)
            
        except Exception as e:
            logger.error(f"Error processing biometric query: {e}")
            return self._create_error_response(f"System error: {str(e)}")
    
    def _validate_input(self, template_base64: str, finger: str) -> Dict[str, Any]:
        """
        Validate input parameters
        
        Args:
            template_base64 (str): Base64 encoded template
            finger (str): Finger type
        
        Returns:
            Dict with validation result
        """
        # Check if template is provided
        if not template_base64 or not template_base64.strip():
            return {'valid': False, 'error': 'Template data is required'}
        
        # Check if finger type is valid
        try:
            FingerType(finger)
        except ValueError:
            valid_fingers = [f.value for f in FingerType]
            return {
                'valid': False, 
                'error': f'Invalid finger type. Valid options: {valid_fingers}'
            }
        
        # Validate base64 format
        try:
            base64.b64decode(template_base64)
        except Exception:
            return {'valid': False, 'error': 'Invalid base64 template format'}
        
        return {'valid': True, 'error': None}
    
    def _convert_template(self, template_base64: str) -> bytes:
        """
        Convert base64 template to binary data
        
        Args:
            template_base64 (str): Base64 encoded template
        
        Returns:
            bytes: Binary template data
        """
        try:
            template_data = base64.b64decode(template_base64)
            logger.debug(f"Template converted successfully, size: {len(template_data)} bytes")
            return template_data
        except Exception as e:
            logger.error(f"Error converting template: {e}")
            raise ValueError(f"Invalid template format: {e}")
    
    def _log_access_attempt(self, person_info: Optional[Dict[str, Any]], 
                           access_result: AccessResult) -> None:
        """
        Log access attempt to database
        
        Args:
            person_info (Optional[Dict]): Person information if found
            access_result (AccessResult): Access authorization result
        """
        try:
            person_id = person_info['person_id'] if person_info else None
            unit_id = self.unit_info['id']
            python_verified = (access_result == AccessResult.GRANTED)
            
            access_log_id = db_manager.log_access_attempt(
                person_id=person_id,
                unit_id=unit_id,
                biometric_device=config.sensor.device,
                python_verified=python_verified
            )
            
            logger.debug(f"Access attempt logged with ID: {access_log_id}")
            
        except Exception as e:
            logger.error(f"Error logging access attempt: {e}")
            # Don't raise exception here to avoid blocking the main process
    
    def _create_response(self, access_result: AccessResult, 
                        person_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create standardized response for sensor
        
        Args:
            access_result (AccessResult): Access authorization result
            person_info (Optional[Dict]): Person information if found
        
        Returns:
            Dict: Standardized response
        """
        response = {
            'access_granted': access_result == AccessResult.GRANTED,
            'result': access_result.value,
            'timestamp': None,  # Will be set by calling system
            'unit_code': self.unit_code,
            'device': config.sensor.device
        }
        
        if person_info:
            response['person'] = {
                'id': person_info['person_id'],
                'name': person_info['full_name'],
                'cpf': person_info['cpf'],
                'type': person_info['person_type'],
                'finger_used': person_info['finger']
            }
        else:
            response['person'] = None
        
        return response
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Create error response
        
        Args:
            error_message (str): Error description
        
        Returns:
            Dict: Error response
        """
        return {
            'access_granted': False,
            'result': AccessResult.ERROR.value,
            'error': error_message,
            'timestamp': None,
            'unit_code': self.unit_code,
            'device': config.sensor.device,
            'person': None
        }
    
    def test_database_connection(self) -> bool:
        """
        Test database connectivity
        
        Returns:
            bool: True if connection is successful
        """
        try:
            result = db_manager.test_connection()
            if result:
                logger.info("Database connection test: SUCCESS")
            else:
                logger.error("Database connection test: FAILED")
            return result
        except Exception as e:
            logger.error(f"Database connection test error: {e}")
            return False


# Example usage and testing functions
def simulate_sensor_input(template_base64: str, finger: str, unit_code: str = "ETEC01") -> None:
    """
    Simulate input from R307 sensor for testing
    
    Args:
        template_base64 (str): Base64 encoded biometric template
        finger (str): Finger type
        unit_code (str): School unit code
    """
    print(f"\\n=== SIMULATING R307 SENSOR INPUT ===")
    print(f"Unit Code: {unit_code}")
    print(f"Finger: {finger}")
    print(f"Template (first 50 chars): {template_base64[:50]}...")
    
    # Initialize biometric service
    service = BiometricQueryService(unit_code)
    
    # Process biometric query
    result = service.process_biometric_query(template_base64, finger)
    
    # Display result
    print(f"\\n=== QUERY RESULT ===")
    print(f"Access Granted: {result['access_granted']}")
    print(f"Result: {result['result']}")
    
    if result.get('person'):
        person = result['person']
        print(f"Person Found: {person['name']} (CPF: {person['cpf']})")
        print(f"Person Type: {person['type']}")
        print(f"Finger Used: {person['finger_used']}")
    else:
        print("Person: Not found")
    
    if result.get('error'):
        print(f"Error: {result['error']}")
    
    print(f"\\n=== SENSOR RESPONSE ===")
    sensor_response = "YES" if result['access_granted'] else "NO"
    print(f"Response to R307 Sensor: {sensor_response}")
    print(f"=== END SIMULATION ===\\n")


if __name__ == "__main__":
    # Test database connection
    service = BiometricQueryService()
    if service.test_database_connection():
        print("✅ Database connection successful!")
        
        # Example simulation with dummy data
        dummy_template = base64.b64encode(b"dummy_biometric_template_data").decode('utf-8')
        simulate_sensor_input(dummy_template, "index_right", "ETEC01")
    else:
        print("❌ Database connection failed!")

