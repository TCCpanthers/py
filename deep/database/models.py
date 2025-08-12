from datetime import datetime
from enum import Enum

class AccessStatus(Enum):
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    ERROR = "ERROR"

class BiometricTemplate:
    def __init__(self, user_id: str, encrypted_template: bytes, is_active: bool = True):
        self.user_id = user_id
        self.encrypted_template = encrypted_template
        self.is_active = is_active
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

class AccessLog:
    def __init__(self, user_id: str, access_time: datetime, access_granted: bool):
        self.user_id = user_id
        self.access_time = access_time
        self.access_granted = access_granted