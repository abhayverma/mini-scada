from sqlalchemy import Column, Integer, String, DateTime, Text, text
from app.db.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=text('NOW()'))
    username = Column(String(50), nullable=False)
    action = Column(String(255), nullable=False)
    details = Column(Text)