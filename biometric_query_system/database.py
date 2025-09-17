"""
database.py - Database connection and query manager for biometric system
# Purpose:
- Establish secure connection to PostgreSQL database
- Provide methods to query biometric data
- Handle database errors and connection pooling
Created by: Guilherme (Python adaptation)
Version: 1.0.0
Date: 2025-09-11
"""

import psycopg2
import psycopg2.extras
from typing import Optional, Dict, Any, List
import logging
from contextlib import contextmanager
from config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.logging.level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=config.logging.file if config.logging.file else None
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database manager for biometric queries
    Handles connection pooling and query execution
    """
    
    def __init__(self):
        self.connection_params = config.database.get_connection_params()
        self._connection = None
        logger.info("Database manager initialized")
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections
        Ensures proper connection cleanup
        """
        connection = None
        try:
            connection = psycopg2.connect(**self.connection_params)
            logger.debug("Database connection established")
            yield connection
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
                logger.debug("Database connection closed")
    
    def test_connection(self) -> bool:
        """
        Test database connectivity
        Returns True if connection is successful
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    logger.info("Database connection test successful")
                    return result[0] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def find_biometric_by_template(self, template_data: bytes, finger: str) -> Optional[Dict[str, Any]]:
        """
        Search for biometric data by template and finger
        
        Args:
            template_data (bytes): Binary template data from sensor
            finger (str): Finger type (e.g., 'index_right', 'thumb_left')
        
        Returns:
            Dict with person information if found, None otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    # Query to find matching biometric and associated person
                    query = """
                    SELECT 
                        p.id as person_id,
                        p.full_name,
                        p.cpf,
                        p.type as person_type,
                        b.id as biometric_id,
                        b.finger,
                        b.registration_date,
                        u.name as unit_name,
                        u.unit_code
                    FROM "Biometric" b
                    INNER JOIN "PeopleBiometrics" pb ON b.id = pb.biometric_id
                    INNER JOIN "Person" p ON pb.person_id = p.id
                    INNER JOIN "Unit" u ON b.registration_unit_id = u.id
                    WHERE b.template = %s AND b.finger = %s
                    LIMIT 1
                    """
                    
                    cursor.execute(query, (template_data, finger))
                    result = cursor.fetchone()
                    
                    if result:
                        logger.info(f"Biometric match found for person: {result['full_name']} (CPF: {result['cpf']})")
                        return dict(result)
                    else:
                        logger.info(f"No biometric match found for finger: {finger}")
                        return None
                        
        except psycopg2.Error as e:
            logger.error(f"Database query error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during biometric search: {e}")
            raise
    
    def log_access_attempt(self, person_id: Optional[int], unit_id: int, 
                          biometric_device: str = "R307", 
                          python_verified: bool = False) -> int:
        """
        Log access attempt to the database
        
        Args:
            person_id (Optional[int]): Person ID if biometric was found
            unit_id (int): Unit where access was attempted
            biometric_device (str): Device used for biometric reading
            python_verified (bool): Whether the biometric was verified by Python system
        
        Returns:
            int: Access log ID
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                    INSERT INTO "AccessLog" 
                    (person_id, unit_id, biometric_device, python_verified, access_time)
                    VALUES (%s, %s, %s, %s, NOW())
                    RETURNING id
                    """
                    
                    cursor.execute(query, (person_id, unit_id, biometric_device, python_verified))
                    access_log_id = cursor.fetchone()[0]
                    conn.commit()
                    
                    logger.info(f"Access attempt logged with ID: {access_log_id}")
                    return access_log_id
                    
        except psycopg2.Error as e:
            logger.error(f"Error logging access attempt: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error logging access attempt: {e}")
            raise
    
    def get_unit_by_code(self, unit_code: str) -> Optional[Dict[str, Any]]:
        """
        Get unit information by unit code
        
        Args:
            unit_code (str): Unit code to search for
        
        Returns:
            Dict with unit information if found, None otherwise
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    query = """
                    SELECT id, name, unit_type, unit_code, address, phone
                    FROM "Unit"
                    WHERE unit_code = %s
                    """
                    
                    cursor.execute(query, (unit_code,))
                    result = cursor.fetchone()
                    
                    if result:
                        logger.debug(f"Unit found: {result['name']} ({result['unit_code']})")
                        return dict(result)
                    else:
                        logger.warning(f"Unit not found for code: {unit_code}")
                        return None
                        
        except psycopg2.Error as e:
            logger.error(f"Database query error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during unit search: {e}")
            raise


# Global database manager instance
db_manager = DatabaseManager()

