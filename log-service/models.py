# -----------------------------------------------------------------------------
# ARQUIVO: log-service/models.py
# -----------------------------------------------------------------------------
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

# MUDANÇA: Importação relativa alterada para absoluta.
from database import Base

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    service_name = Column(String(50), index=True) # Ex: 'auth-service', 'command-service'
    user_id = Column(Integer, nullable=True)
    level = Column(String(20), default="INFO") # Ex: INFO, ERROR, WARNING
    message = Column(String(512))