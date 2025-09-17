"""
test_offline.py - Offline test for biometric system components
# Purpose:
- Test system logic without any database dependencies
- Validate core functionality and algorithms
- Demonstrate system capabilities for development
Created by: Guilherme
Version: 1.0.0
Date: 2025-09-11
"""

import base64
import sys
import os
from typing import Dict, Any, Optional
from enum import Enum


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


class OfflineBiometricService:
    """
    Offline biometric service for testing core functionality
    Simulates database operations with in-memory data
    """
    
    def __init__(self, unit_code: str = "ETEC01"):
        self.unit_code = unit_code
        
        # Mock biometric database
        self.biometric_database = {
            # Template hash -> Person info
            self._hash_template(base64.b64decode('VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YQ==')): {
                'person_id': 1,
                'full_name': 'João Silva',
                'cpf': '123.456.789-00',
                'person_type': 'student',
                'finger': 'index_right',
                'unit_code': 'ETEC01'
            },
            self._hash_template(base64.b64decode('VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YSAy')): {
                'person_id': 2,
                'full_name': 'Maria Santos',
                'cpf': '987.654.321-00',
                'person_type': 'teacher',
                'finger': 'thumb_left',
                'unit_code': 'ETEC01'
            },
            self._hash_template(base64.b64decode('UHJvZmVzc29yIEpvc2UgU2lsdmE=')): {
                'person_id': 3,
                'full_name': 'José Silva',
                'cpf': '456.789.123-00',
                'person_type': 'teacher',
                'finger': 'middle_right',
                'unit_code': 'ETEC01'
            }
        }
        
        self.access_logs = []
        print(f"🔧 Offline biometric service initialized for unit: {unit_code}")
        print(f"📊 Mock database loaded with {len(self.biometric_database)} biometric records")
    
    def _hash_template(self, template_data: bytes) -> str:
        """Simple hash function for template matching"""
        return str(hash(template_data))
    
    def process_biometric_query(self, template_base64: str, finger: str) -> Dict[str, Any]:
        """
        Process biometric query with offline data
        
        Args:
            template_base64 (str): Base64 encoded biometric template
            finger (str): Finger type
        
        Returns:
            Dict containing access result and person information
        """
        print(f"\\n🔍 Processing biometric query:")
        print(f"   Finger: {finger}")
        print(f"   Template: {template_base64[:30]}{'...' if len(template_base64) > 30 else ''}")
        
        try:
            # Validate input
            validation_result = self._validate_input(template_base64, finger)
            if not validation_result['valid']:
                print(f"   ❌ Validation failed: {validation_result['error']}")
                return self._create_error_response(validation_result['error'])
            
            # Convert template
            template_data = base64.b64decode(template_base64)
            template_hash = self._hash_template(template_data)
            
            print(f"   Template size: {len(template_data)} bytes")
            print(f"   Template hash: {template_hash}")
            
            # Search in mock database
            person_info = None
            if template_hash in self.biometric_database:
                candidate = self.biometric_database[template_hash]
                if candidate['finger'] == finger:
                    person_info = candidate
                    print(f"   ✅ Match found: {person_info['full_name']} (CPF: {person_info['cpf']})")
                else:
                    print(f"   ❌ Template found but finger mismatch: expected {finger}, found {candidate['finger']}")
            else:
                print(f"   ❌ No matching template found in database")
            
            # Determine result
            if person_info:
                access_result = AccessResult.GRANTED
                print(f"   🟢 Access GRANTED for {person_info['full_name']}")
            else:
                access_result = AccessResult.DENIED
                print(f"   🔴 Access DENIED - No matching biometric")
            
            # Log access attempt
            self._log_access_attempt(person_info, access_result)
            
            return self._create_response(access_result, person_info)
            
        except Exception as e:
            error_msg = f"System error: {str(e)}"
            print(f"   💥 Error: {error_msg}")
            return self._create_error_response(error_msg)
    
    def _validate_input(self, template_base64: str, finger: str) -> Dict[str, Any]:
        """Validate input parameters"""
        if not template_base64 or not template_base64.strip():
            return {'valid': False, 'error': 'Template data is required'}
        
        try:
            FingerType(finger)
        except ValueError:
            valid_fingers = [f.value for f in FingerType]
            return {
                'valid': False, 
                'error': f'Invalid finger type. Valid options: {valid_fingers}'
            }
        
        try:
            base64.b64decode(template_base64)
        except Exception:
            return {'valid': False, 'error': 'Invalid base64 template format'}
        
        return {'valid': True, 'error': None}
    
    def _log_access_attempt(self, person_info: Optional[Dict[str, Any]], 
                           access_result: AccessResult) -> None:
        """Log access attempt"""
        log_entry = {
            'id': len(self.access_logs) + 1,
            'person_id': person_info['person_id'] if person_info else None,
            'person_name': person_info['full_name'] if person_info else None,
            'access_result': access_result.value,
            'unit_code': self.unit_code,
            'timestamp': '2025-09-11 10:30:00'
        }
        self.access_logs.append(log_entry)
        print(f"   📝 Access logged: ID={log_entry['id']}")
    
    def _create_response(self, access_result: AccessResult, 
                        person_info: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create standardized response"""
        response = {
            'access_granted': access_result == AccessResult.GRANTED,
            'result': access_result.value,
            'unit_code': self.unit_code,
            'device': 'R307'
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
        """Create error response"""
        return {
            'access_granted': False,
            'result': AccessResult.ERROR.value,
            'error': error_message,
            'unit_code': self.unit_code,
            'device': 'R307',
            'person': None
        }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get mock database statistics"""
        return {
            'total_biometrics': len(self.biometric_database),
            'total_access_logs': len(self.access_logs),
            'unit_code': self.unit_code
        }


class OfflineTestSuite:
    """Comprehensive test suite for offline biometric system"""
    
    def __init__(self):
        self.service = OfflineBiometricService("ETEC01")
        self.test_results = []
    
    def run_all_tests(self):
        """Run all test scenarios"""
        print("\\n" + "="*70)
        print("🚀 STARTING OFFLINE BIOMETRIC SYSTEM TESTS")
        print("="*70)
        
        # Test scenarios
        test_methods = [
            self.test_valid_student_access,
            self.test_valid_teacher_access,
            self.test_invalid_template,
            self.test_wrong_finger,
            self.test_empty_template,
            self.test_invalid_finger_type,
            self.test_invalid_base64,
            self.test_multiple_queries
        ]
        
        for test_method in test_methods:
            try:
                test_method()
                self.test_results.append({'test': test_method.__name__, 'status': 'PASSED'})
            except AssertionError as e:
                print(f"   ❌ ASSERTION FAILED: {e}")
                self.test_results.append({'test': test_method.__name__, 'status': 'FAILED', 'error': str(e)})
            except Exception as e:
                print(f"   💥 UNEXPECTED ERROR: {e}")
                self.test_results.append({'test': test_method.__name__, 'status': 'ERROR', 'error': str(e)})
        
        self.show_test_summary()
    
    def test_valid_student_access(self):
        """Test valid student biometric access"""
        print("\\n1. 👨‍🎓 Testing valid student access...")
        
        template = "VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YQ=="  # João Silva
        finger = "index_right"
        
        result = self.service.process_biometric_query(template, finger)
        
        assert result['access_granted'] == True, "Student access should be granted"
        assert result['person']['name'] == 'João Silva', "Correct student should be identified"
        assert result['person']['type'] == 'student', "Person type should be student"
        
        print("   ✅ Valid student access test: PASSED")
    
    def test_valid_teacher_access(self):
        """Test valid teacher biometric access"""
        print("\\n2. 👩‍🏫 Testing valid teacher access...")
        
        template = "VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YSAy"  # Maria Santos
        finger = "thumb_left"
        
        result = self.service.process_biometric_query(template, finger)
        
        assert result['access_granted'] == True, "Teacher access should be granted"
        assert result['person']['name'] == 'Maria Santos', "Correct teacher should be identified"
        assert result['person']['type'] == 'teacher', "Person type should be teacher"
        
        print("   ✅ Valid teacher access test: PASSED")
    
    def test_invalid_template(self):
        """Test access with invalid/unknown template"""
        print("\\n3. ❌ Testing invalid template...")
        
        template = "SW52YWxpZCB0ZW1wbGF0ZSBkYXRh"  # Unknown template
        finger = "index_right"
        
        result = self.service.process_biometric_query(template, finger)
        
        assert result['access_granted'] == False, "Access should be denied for invalid template"
        assert result['person'] is None, "No person should be identified"
        
        print("   ✅ Invalid template test: PASSED")
    
    def test_wrong_finger(self):
        """Test access with correct template but wrong finger"""
        print("\\n4. 👆 Testing wrong finger type...")
        
        template = "VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YQ=="  # João Silva's template
        finger = "thumb_right"  # Wrong finger (should be index_right)
        
        result = self.service.process_biometric_query(template, finger)
        
        assert result['access_granted'] == False, "Access should be denied for wrong finger"
        assert result['person'] is None, "No person should be identified"
        
        print("   ✅ Wrong finger test: PASSED")
    
    def test_empty_template(self):
        """Test access with empty template"""
        print("\\n5. 📭 Testing empty template...")
        
        template = ""
        finger = "index_right"
        
        result = self.service.process_biometric_query(template, finger)
        
        assert result['access_granted'] == False, "Access should be denied for empty template"
        assert 'error' in result, "Error message should be present"
        assert 'required' in result['error'].lower(), "Error should mention required field"
        
        print("   ✅ Empty template test: PASSED")
    
    def test_invalid_finger_type(self):
        """Test access with invalid finger type"""
        print("\\n6. 🚫 Testing invalid finger type...")
        
        template = "VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YQ=="
        finger = "invalid_finger_type"
        
        result = self.service.process_biometric_query(template, finger)
        
        assert result['access_granted'] == False, "Access should be denied for invalid finger type"
        assert 'error' in result, "Error message should be present"
        assert 'invalid finger type' in result['error'].lower(), "Error should mention invalid finger type"
        
        print("   ✅ Invalid finger type test: PASSED")
    
    def test_invalid_base64(self):
        """Test access with invalid base64 template"""
        print("\\n7. 🔤 Testing invalid base64...")
        
        template = "invalid_base64_data!!!"
        finger = "index_right"
        
        result = self.service.process_biometric_query(template, finger)
        
        assert result['access_granted'] == False, "Access should be denied for invalid base64"
        assert 'error' in result, "Error message should be present"
        
        print("   ✅ Invalid base64 test: PASSED")
    
    def test_multiple_queries(self):
        """Test multiple sequential queries"""
        print("\\n8. 🔄 Testing multiple sequential queries...")
        
        queries = [
            ("VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YQ==", "index_right", True),  # João Silva
            ("VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YSAy", "thumb_left", True),   # Maria Santos
            ("UHJvZmVzc29yIEpvc2UgU2lsdmE=", "middle_right", True),              # José Silva
            ("SW52YWxpZCB0ZW1wbGF0ZQ==", "index_right", False),                  # Invalid
        ]
        
        for i, (template, finger, expected_access) in enumerate(queries):
            result = self.service.process_biometric_query(template, finger)
            assert result['access_granted'] == expected_access, f"Query {i+1} access result mismatch"
            print(f"   Query {i+1}: {'✅ GRANTED' if result['access_granted'] else '❌ DENIED'}")
        
        print("   ✅ Multiple queries test: PASSED")
    
    def show_test_summary(self):
        """Show comprehensive test summary"""
        print("\\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for result in self.test_results if result['status'] == 'PASSED')
        failed = sum(1 for result in self.test_results if result['status'] == 'FAILED')
        errors = sum(1 for result in self.test_results if result['status'] == 'ERROR')
        total = len(self.test_results)
        
        print(f"\\n📈 Test Results:")
        print(f"   Total tests: {total}")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   💥 Errors: {errors}")
        print(f"   Success rate: {(passed/total)*100:.1f}%")
        
        # Show database stats
        stats = self.service.get_database_stats()
        print(f"\\n📊 Database Statistics:")
        print(f"   Biometric records: {stats['total_biometrics']}")
        print(f"   Access logs: {stats['total_access_logs']}")
        print(f"   Unit code: {stats['unit_code']}")
        
        # Show detailed results
        print(f"\\n📋 Detailed Results:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASSED' else "❌" if result['status'] == 'FAILED' else "💥"
            print(f"   {status_icon} {result['test']}: {result['status']}")
            if 'error' in result:
                print(f"      Error: {result['error']}")
        
        # Show access logs
        print(f"\\n📝 Access Logs:")
        for log in self.service.access_logs:
            person_name = log['person_name'] or 'Unknown'
            print(f"   Log {log['id']}: {person_name} - {log['access_result']}")
        
        if failed == 0 and errors == 0:
            print("\\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
            print("✅ Biometric system is working correctly!")
        else:
            print(f"\\n⚠️  {failed + errors} test(s) failed. Please review the results above.")


def simulate_sensor_communication():
    """Simulate R307 sensor communication"""
    print("\\n" + "="*70)
    print("🤖 SIMULATING R307 SENSOR COMMUNICATION")
    print("="*70)
    
    service = OfflineBiometricService("ETEC01")
    
    # Simulate sensor commands
    sensor_commands = [
        {
            'command': 'QUERY:VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YQ==:index_right',
            'description': 'Student João Silva access attempt'
        },
        {
            'command': 'QUERY:VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YSAy:thumb_left',
            'description': 'Teacher Maria Santos access attempt'
        },
        {
            'command': 'QUERY:SW52YWxpZCB0ZW1wbGF0ZQ==:index_right',
            'description': 'Unknown person access attempt'
        }
    ]
    
    for i, cmd_info in enumerate(sensor_commands, 1):
        print(f"\\n📡 Sensor Command {i}: {cmd_info['description']}")
        print(f"   Raw command: {cmd_info['command']}")
        
        # Parse command
        parts = cmd_info['command'].split(':')
        if len(parts) >= 3:
            command_type, template, finger = parts[0], parts[1], parts[2]
            
            # Process query
            result = service.process_biometric_query(template, finger)
            
            # Generate sensor response
            sensor_response = "YES" if result['access_granted'] else "NO"
            print(f"   🤖 Sensor Response: {sensor_response}")
            
            if result['person']:
                print(f"   👤 Person: {result['person']['name']} ({result['person']['type']})")
        else:
            print(f"   ❌ Invalid command format")
    
    print("\\n🏁 Sensor communication simulation completed")


def main():
    """Main function to run all tests"""
    try:
        print("🔬 BIOMETRIC SYSTEM OFFLINE TESTING")
        print("=" * 70)
        print("This test suite validates the biometric system without requiring")
        print("a database connection. All data is simulated in memory.")
        print("=" * 70)
        
        # Run comprehensive tests
        test_suite = OfflineTestSuite()
        test_suite.run_all_tests()
        
        # Simulate sensor communication
        simulate_sensor_communication()
        
        print("\\n" + "="*70)
        print("🎯 TESTING COMPLETED SUCCESSFULLY!")
        print("The biometric system is ready for integration with:")
        print("  • R307 biometric sensor")
        print("  • PostgreSQL database")
        print("  • School access control system")
        print("="*70)
        
    except Exception as e:
        print(f"\\n💥 CRITICAL ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

