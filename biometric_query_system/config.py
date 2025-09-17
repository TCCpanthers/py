"""
config.py - Configuration manager for the biometric query system
# Purpose:
- Load environment variables and database configuration
- Provide centralized configuration management
Created by: Guilherme (Python adaptation)
Version: 1.0.0
Date: 2025-09-11
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig:
    """Database configuration settings"""
    
    def __init__(self):
        self.url: str = os.getenv('DATABASE_URL', '')
        if not self.url:
            raise ValueError("DATABASE_URL environment variable is required")
    
    def get_connection_params(self) -> dict:
        """
        Parse DATABASE_URL and return connection parameters
        Format: postgresql://username:password@host:port/database
        """
        if not self.url.startswith('postgresql://'):
            raise ValueError("Invalid DATABASE_URL format. Must start with 'postgresql://'")
        
        # Remove protocol prefix
        url_without_protocol = self.url.replace('postgresql://', '')
        
        # Split user info and host info
        if '@' not in url_without_protocol:
            raise ValueError("Invalid DATABASE_URL format. Missing user credentials")
        
        user_info, host_info = url_without_protocol.split('@', 1)
        
        # Parse user credentials
        if ':' not in user_info:
            raise ValueError("Invalid DATABASE_URL format. Missing password")
        
        username, password = user_info.split(':', 1)
        
        # Parse host and database
        if '/' not in host_info:
            raise ValueError("Invalid DATABASE_URL format. Missing database name")
        
        host_port, database = host_info.split('/', 1)
        
        # Parse host and port
        if ':' in host_port:
            host, port = host_port.split(':', 1)
            port = int(port)
        else:
            host = host_port
            port = 5432  # Default PostgreSQL port
        
        return {
            'host': host,
            'port': port,
            'database': database,
            'user': username,
            'password': password
        }


class SensorConfig:
    """Sensor configuration settings"""
    
    def __init__(self):
        self.device: str = os.getenv('SENSOR_DEVICE', 'R307')
        self.port: str = os.getenv('SENSOR_PORT', '/dev/ttyUSB0')
        self.baudrate: int = int(os.getenv('SENSOR_BAUDRATE', '57600'))


class LoggingConfig:
    """Logging configuration settings"""
    
    def __init__(self):
        self.level: str = os.getenv('LOG_LEVEL', 'INFO')
        self.file: Optional[str] = os.getenv('LOG_FILE')


class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.database = DatabaseConfig()
        self.sensor = SensorConfig()
        self.logging = LoggingConfig()


# Global configuration instance
config = Config()

