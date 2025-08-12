import RPi.GPIO as GPIO
import time
from config import Config
from enum import Enum

class GateState(Enum):
    OPEN = 1
    CLOSED = 0

class GateController:
    def __init__(self):
        self.gpio_pin = Config.GATE_GPIO_PIN
        self.setup_gpio()
    
    def setup_gpio(self):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gpio_pin, GPIO.OUT)
            self.close_gate()  # Inicia com a catraca fechada
        except Exception as e:
            print(f"Erro ao configurar GPIO: {e}")
            raise
    
    def open_gate(self):
        """Abre a catraca/porta"""
        try:
            GPIO.output(self.gpio_pin, GPIO.HIGH)
            time.sleep(Config.GATE_OPEN_TIME)
            self.close_gate()
        except Exception as e:
            print(f"Erro ao abrir catraca: {e}")
    
    def close_gate(self):
        """Fecha a catraca/porta"""
        try:
            GPIO.output(self.gpio_pin, GPIO.LOW)
        except Exception as e:
            print(f"Erro ao fechar catraca: {e}")
    
    def cleanup(self):
        GPIO.cleanup()