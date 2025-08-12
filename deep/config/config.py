import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configurações do banco de dados
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'biometric_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASS = os.getenv('DB_PASS', 'password')
    
    # Configurações de criptografia
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'default-encryption-key-123')
    ENCRYPTION_SALT = os.getenv('ENCRYPTION_SALT', 'default-salt-123')
    
    # Configurações do sensor
    SENSOR_PORT = os.getenv('SENSOR_PORT', '/dev/ttyUSB0')
    SENSOR_BAUDRATE = int(os.getenv('SENSOR_BAUDRATE', 9600))
    
    # Configurações da catraca
    GATE_GPIO_PIN = int(os.getenv('GATE_GPIO_PIN', 17))
    GATE_OPEN_TIME = int(os.getenv('GATE_OPEN_TIME', 5))  # segundos