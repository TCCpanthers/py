import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .encryption import BiometricEncryptor
from database.db_connector import DatabaseConnector

class BiometricMatcher:
    def __init__(self):
        self.db = DatabaseConnector()
        self.encryptor = BiometricEncryptor()
        self.threshold = 0.85  # Limiar de similaridade
    
    def _deserialize_template(self, template_str: str) -> np.ndarray:
        """Converte a string do template em um vetor numpy"""
        return np.array([float(x) for x in template_str.split(',')])
    
    def compare_templates(self, sensor_template: str, user_id: str) -> bool:
        """Compara o template do sensor com o template armazenado"""
        try:
            # Recupera template armazenado
            encrypted_template = self.db.get_biometric_template(user_id)
            if not encrypted_template:
                return False
            
            # Descriptografa template
            stored_template_str = self.encryptor.decrypt_template(encrypted_template)
            stored_template = self._deserialize_template(stored_template_str)
            
            # Converte template do sensor
            sensor_template_vec = self._deserialize_template(sensor_template)
            
            # Calcula similaridade
            similarity = cosine_similarity(
                [stored_template],
                [sensor_template_vec]
            )[0][0]
            
            return similarity >= self.threshold
        except Exception as e:
            print(f"Erro na comparação de templates: {e}")
            return False