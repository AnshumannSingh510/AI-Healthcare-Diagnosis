from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(32), nullable=True)
    medical_history = Column(Text, nullable=True)
    assigned_doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)

    user = relationship("User", back_populates="patient_profile", foreign_keys=[patient_id])


class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    specialization = Column(String(255), nullable=True)
    license_number = Column(String(128), nullable=True)

    user = relationship("User", back_populates="doctor_profile", foreign_keys=[doctor_id])
