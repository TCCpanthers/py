import serial
import json
from config import Config

class BiometricSensor:
    def __init__(self):
        self.serial_conn = None
        self.connect()
    
    def connect(self):
        try:
            self.serial_conn = serial.Serial(
                port=Config.SENSOR_PORT,
                baudrate=Config.SENSOR_BAUDRATE,
                timeout=1
            )
            print(f"Conexão com sensor estabelecida em {Config.SENSOR_PORT}")
        except Exception as e:
            print(f"Erro ao conectar ao sensor: {e}")
            raise
    
    def read_biometric_data(self):
        """Lê dados do sensor e retorna o user_id e template"""
        try:
            if self.serial_conn.in_waiting > 0:
                line = self.serial_conn.readline().decode('utf-8').strip()
                try:
                    data = json.loads(line)
                    return data.get('user_id'), data.get('template')
                except json.JSONDecodeError:
                    print("Dados inválidos recebidos do sensor")
                    return None, None
            return None, None
        except Exception as e:
            print(f"Erro ao ler dados do sensor: {e}")
            return None, None
    
    def close(self):
        if self.serial_conn:
            self.serial_conn.close()