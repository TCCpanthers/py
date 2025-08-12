import time
from hardware.sensor_interface import BiometricSensor
from hardware.gate_controller import GateController
from biometric.matcher import BiometricMatcher
from database.db_connector import DatabaseConnector

class BiometricAccessSystem:
    def __init__(self):
        self.sensor = BiometricSensor()
        self.gate = GateController()
        self.matcher = BiometricMatcher()
        self.db = DatabaseConnector()
    
    def run(self):
        print("Sistema de Controle de Acesso Biométrico Iniciado")
        try:
            while True:
                user_id, template = self.sensor.read_biometric_data()
                if user_id and template:
                    print(f"Template recebido para o usuário: {user_id}")
                    
                    # Verifica correspondência biométrica
                    access_granted = self.matcher.compare_templates(template, user_id)
                    
                    if access_granted:
                        print("Acesso concedido")
                        self.gate.open_gate()
                    else:
                        print("Acesso negado")
                    
                    # Registra o acesso no banco de dados
                    self.db.log_access(user_id, access_granted)
                
                time.sleep(0.1)  # Pequena pausa para evitar uso excessivo da CPU
        
        except KeyboardInterrupt:
            print("\nEncerrando sistema...")
        finally:
            self.shutdown()
    
    def shutdown(self):
        self.sensor.close()
        self.gate.cleanup()
        self.db.close()

if __name__ == "__main__":
    system = BiometricAccessSystem()
    system.run()