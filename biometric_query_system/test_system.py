"""
test_system.py - Test script for biometric system without database dependency
# Purpose:
- Test system components without requiring database connection
- Validate input processing and response generation
- Demonstrate system functionality for development
Created by: Guilherme
Version: 1.0.0
Date: 2025-09-11
"""

import base64
import sys
import os

# Add current directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from biometric_service import BiometricQueryService, FingerType, AccessResult


class MockDatabaseManager:
    """Mock database manager for testing without real database"""
    
    def __init__(self):
        # Mock biometric data for testing
        self.mock_biometrics = [
            {
                'person_id': 1,
                'full_name': 'João Silva',
                'cpf': '123.456.789-00',
                'person_type': 'student',
                'biometric_id': 1,
                'finger': 'index_right',
                'registration_date': '2025-01-15',
                'unit_name': 'ETEC São Paulo',
                'unit_code': 'ETEC01',
                'template': base64.b64decode('VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YQ==')  # "Test biometric template data"
            },
            {
                'person_id': 2,
                'full_name': 'Maria Santos',
                'cpf': '987.654.321-00',
                'person_type': 'teacher',
                'biometric_id': 2,
                'finger': 'thumb_left',
                'registration_date': '2025-01-10',
                'unit_name': 'ETEC São Paulo',
                'unit_code': 'ETEC01',
                'template': base64.b64decode('VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YSAy')  # "Test biometric template data 2"
            }
        ]
        
        self.mock_units = [
            {
                'id': 1,
                'name': 'ETEC São Paulo',
                'unit_code': 'ETEC01',
                'unit_type': 'Etec',
                'address': 'Rua das Escolas, 123',
                'phone': '(11) 1234-5678'
            }
        ]
        
        self.access_logs = []
    
    def test_connection(self) -> bool:
        """Mock database connection test"""
        print("🔗 Mock database connection: SUCCESS")
        return True
    
    def find_biometric_by_template(self, template_data: bytes, finger: str):
        """Mock biometric search"""
        print(f"🔍 Searching for biometric: finger={finger}, template_size={len(template_data)} bytes")
        
        for biometric in self.mock_biometrics:
            if biometric['template'] == template_data and biometric['finger'] == finger:
                print(f"✅ Match found: {biometric['full_name']} (CPF: {biometric['cpf']})")
                return biometric
        
        print("❌ No match found")
        return None
    
    def log_access_attempt(self, person_id, unit_id, biometric_device="R307", python_verified=False):
        """Mock access logging"""
        log_id = len(self.access_logs) + 1
        log_entry = {
            'id': log_id,
            'person_id': person_id,
            'unit_id': unit_id,
            'biometric_device': biometric_device,
            'python_verified': python_verified,
            'timestamp': '2025-09-11 10:30:00'
        }
        self.access_logs.append(log_entry)
        print(f"📝 Access logged: ID={log_id}, person_id={person_id}, verified={python_verified}")
        return log_id
    
    def get_unit_by_code(self, unit_code: str):
        """Mock unit search"""
        for unit in self.mock_units:
            if unit['unit_code'] == unit_code:
                print(f"🏫 Unit found: {unit['name']} ({unit['unit_code']})")
                return unit
        
        print(f"❌ Unit not found: {unit_code}")
        return None


class TestBiometricSystem:
    """Test class for biometric system functionality"""
    
    def __init__(self):
        # Replace the real database manager with mock
        import database
        self.original_db_manager = database.db_manager
        database.db_manager = MockDatabaseManager()
        
        # Import after replacing db_manager
        from biometric_service import BiometricQueryService
        self.service = BiometricQueryService("ETEC01")
        
        print("🧪 Test system initialized with mock database")
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("\\n" + "="*60)
        print("🚀 STARTING BIOMETRIC SYSTEM TESTS")
        print("="*60)
        
        # Test 1: Database connection
        self.test_database_connection()
        
        # Test 2: Valid biometric query (should find match)
        self.test_valid_biometric_query()
        
        # Test 3: Invalid biometric query (no match)
        self.test_invalid_biometric_query()
        
        # Test 4: Input validation tests
        self.test_input_validation()
        
        # Test 5: Different finger types
        self.test_different_fingers()
        
        print("\\n" + "="*60)
        print("🏁 ALL TESTS COMPLETED")
        print("="*60)
    
    def test_database_connection(self):
        """Test database connectivity"""
        print("\\n1. 🔗 Testing database connection...")
        result = self.service.test_database_connection()
        assert result == True, "Database connection should succeed"
        print("   ✅ Database connection test: PASSED")
    
    def test_valid_biometric_query(self):
        """Test valid biometric query that should find a match"""
        print("\\n2. 🔍 Testing valid biometric query...")
        
        # Use the same template as in mock data
        template = "VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YQ=="  # "Test biometric template data"
        finger = "index_right"
        
        result = self.service.process_biometric_query(template, finger)
        
        print(f"   Template: {template}")
        print(f"   Finger: {finger}")
        print(f"   Access granted: {result['access_granted']}")
        print(f"   Result: {result['result']}")
        
        if result['person']:
            person = result['person']
            print(f"   Person found: {person['name']} (CPF: {person['cpf']})")
        
        assert result['access_granted'] == True, "Access should be granted for valid biometric"
        assert result['person'] is not None, "Person information should be returned"
        assert result['person']['name'] == 'João Silva', "Correct person should be found"
        
        print("   ✅ Valid biometric query test: PASSED")
    
    def test_invalid_biometric_query(self):
        """Test invalid biometric query that should not find a match"""
        print("\\n3. ❌ Testing invalid biometric query...")
        
        # Use a different template that won't match
        template = "SW52YWxpZCBiaW9tZXRyaWMgdGVtcGxhdGU="  # "Invalid biometric template"
        finger = "index_right"
        
        result = self.service.process_biometric_query(template, finger)
        
        print(f"   Template: {template}")
        print(f"   Finger: {finger}")
        print(f"   Access granted: {result['access_granted']}")
        print(f"   Result: {result['result']}")
        
        assert result['access_granted'] == False, "Access should be denied for invalid biometric"
        assert result['person'] is None, "No person information should be returned"
        
        print("   ✅ Invalid biometric query test: PASSED")
    
    def test_input_validation(self):
        """Test input validation functionality"""
        print("\\n4. 🛡️ Testing input validation...")
        
        # Test empty template
        result1 = self.service.process_biometric_query("", "index_right")
        assert result1['access_granted'] == False, "Empty template should be rejected"
        assert 'error' in result1, "Error message should be present"
        print("   ✅ Empty template validation: PASSED")
        
        # Test invalid finger type
        result2 = self.service.process_biometric_query("VGVzdA==", "invalid_finger")
        assert result2['access_granted'] == False, "Invalid finger should be rejected"
        assert 'error' in result2, "Error message should be present"
        print("   ✅ Invalid finger validation: PASSED")
        
        # Test invalid base64
        result3 = self.service.process_biometric_query("invalid_base64!!!", "index_right")
        assert result3['access_granted'] == False, "Invalid base64 should be rejected"
        assert 'error' in result3, "Error message should be present"
        print("   ✅ Invalid base64 validation: PASSED")
        
        print("   ✅ Input validation tests: ALL PASSED")
    
    def test_different_fingers(self):
        """Test different finger types"""
        print("\\n5. 👆 Testing different finger types...")
        
        # Test with thumb_left (should find Maria Santos)
        template = "VGVzdCBiaW9tZXRyaWMgdGVtcGxhdGUgZGF0YSAy"  # "Test biometric template data 2"
        finger = "thumb_left"
        
        result = self.service.process_biometric_query(template, finger)
        
        print(f"   Template: {template}")
        print(f"   Finger: {finger}")
        print(f"   Access granted: {result['access_granted']}")
        
        if result['person']:
            person = result['person']
            print(f"   Person found: {person['name']} (Type: {person['type']})")
        
        assert result['access_granted'] == True, "Access should be granted for valid thumb_left"
        assert result['person']['name'] == 'Maria Santos', "Correct person should be found"
        assert result['person']['type'] == 'teacher', "Person type should be teacher"
        
        print("   ✅ Different finger types test: PASSED")
    
    def show_test_summary(self):
        """Show test summary and mock data"""
        print("\\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        # Show mock database contents
        mock_db = database.db_manager
        print(f"\\n📚 Mock Database Contents:")
        print(f"   Biometric records: {len(mock_db.mock_biometrics)}")
        print(f"   Unit records: {len(mock_db.mock_units)}")
        print(f"   Access logs created: {len(mock_db.access_logs)}")
        
        print(f"\\n👥 Mock People:")
        for bio in mock_db.mock_biometrics:
            print(f"   - {bio['full_name']} ({bio['person_type']}) - {bio['finger']}")
        
        print(f"\\n📝 Access Logs:")
        for log in mock_db.access_logs:
            print(f"   - Log {log['id']}: Person {log['person_id']}, Verified: {log['python_verified']}")


def main():
    """Main test function"""
    try:
        # Initialize test system
        test_system = TestBiometricSystem()
        
        # Run all tests
        test_system.run_all_tests()
        
        # Show summary
        test_system.show_test_summary()
        
        print("\\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
        
    except AssertionError as e:
        print(f"\\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\\n💥 UNEXPECTED ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

