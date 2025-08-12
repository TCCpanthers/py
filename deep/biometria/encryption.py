from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
from config import Config

class BiometricEncryptor:
    def __init__(self):
        self.key = self._generate_encryption_key()
    
    def _generate_encryption_key(self):
        """Gera a chave de criptografia a partir da senha e salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=Config.ENCRYPTION_SALT.encode(),
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(Config.ENCRYPTION_KEY.encode()))
        return key
    
    def encrypt_template(self, template_data: str) -> bytes:
        """Criptografa o template biométrico"""
        f = Fernet(self.key)
        encrypted_data = f.encrypt(template_data.encode())
        return encrypted_data
    
    def decrypt_template(self, encrypted_data: bytes) -> str:
        """Descriptografa o template biométrico"""
        f = Fernet(self.key)
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data.decode()