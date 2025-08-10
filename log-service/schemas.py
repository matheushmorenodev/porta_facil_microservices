# -----------------------------------------------------------------------------
# ARQUIVO: schemas.py
# DESCRIÇÃO: Modelos Pydantic para validação de dados da API.
# -----------------------------------------------------------------------------
from pydantic import BaseModel
from datetime import datetime

class LogCreate(BaseModel):
    service_name: str
    user_id: int | None = None
    level: str = "INFO"
    message: str

class LogResponse(LogCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True # Antigo orm_mode