from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

# MUDANÇA: Importações relativas alteradas para absolutas.
# Isso torna o código mais robusto e evita o ImportError.
import models
import schemas
import database

# Cria as tabelas no banco de dados se não existirem
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Log Service")

# Dependência para obter a sessão do banco de dados
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/log/", response_model=schemas.LogResponse, status_code=201)
def create_log(log: schemas.LogCreate, db: Session = Depends(get_db)):
    """
    Recebe um evento de log e o salva no banco de dados.
    """
    db_log = models.Log(
        service_name=log.service_name,
        user_id=log.user_id,
        level=log.level,
        message=log.message
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    print(f"Log salvo: {db_log.service_name} - {db_log.message}")
    return db_log

@app.get("/")
def read_root():
    return {"service": "Log Service", "status": "online"}