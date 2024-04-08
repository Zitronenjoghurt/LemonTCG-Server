from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from src.models.e2ee_models import E2EEPublicKey, E2EEEncryptedPrivateKey

class E2EE(BaseModel):
    public: Optional[str] = None
    private: Optional[str] = None
    salt_hex: Optional[str] = None
    activated_stamp: Optional[datetime] = None

    def is_ready(self) -> bool:
        return isinstance(self.public, str) and isinstance(self.private, str)

    def set_up(self, public_key: str, private_key: str, salt_hex: str) -> tuple[bool, str]:
        if self.is_ready():
            return False, "E2EE already enabled."
        self.public = public_key
        self.private = private_key
        self.salt_hex = salt_hex
        self.activated_stamp = datetime.now()
        return True, ""
    
    def get_public_key(self) -> Optional[E2EEPublicKey]:
        if not isinstance(self.public, str):
            return None
        return E2EEPublicKey(key=self.public)
    
    def get_encrypted_private_key(self) -> Optional[E2EEEncryptedPrivateKey]:
        if not isinstance(self.private, str) or not isinstance(self.salt_hex, str):
            return None
        return E2EEEncryptedPrivateKey(key=self.private, salt_hex=self.salt_hex)