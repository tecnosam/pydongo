import uuid
from typing import Optional, List

from pydantic import BaseModel, Field

from pydongo import as_collection, as_document
from pydongo.drivers.sync_mongo import PyMongoDriver


# =========================
# Models
# =========================

class Prescription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    drug_name: str
    dosage: str
    frequency: str
    duration_days: int


class Patient(BaseModel):
    patient_id: str
    name: str
    age: int

    prescriptions: List[Prescription] = Field(default_factory=list)


# =========================
# Database setup
# =========================

driver = PyMongoDriver("mongodb://localhost:27017", "medtech_app")
driver.connect()

patients = as_collection(Patient, driver)


# =========================
# CRUD-style operations
# =========================

def create_patient(patient_id: str, name: str, age: int) -> Patient:
    """
    Create and persist a new patient record.
    """
    patient = Patient(
        patient_id=patient_id,
        name=name,
        age=age,
    )

    doc = as_document(patient, driver)
    doc.save()
    return doc


def add_prescription(
    patient_id: str,
    drug_name: str,
    dosage: str,
    frequency: str,
    duration_days: int,
) -> Optional[Prescription]:
    """
    Add a prescription to an existing patient.
    """
    patient = patients.find_one(patients.patient_id == patient_id)
    if not patient:
        return None

    prescription = Prescription(
        drug_name=drug_name,
        dosage=dosage,
        frequency=frequency,
        duration_days=duration_days,
    )

    patient.prescriptions.append(prescription)
    patient.save()

    return prescription


def get_prescriptions(patient_id: str) -> List[Prescription]:
    """
    Retrieve all prescriptions for a given patient.
    """
    patient = patients.find_one(patients.patient_id == patient_id)
    return patient.prescriptions if patient else []


def get_all_patients() -> List[Patient]:
    """
    Retrieve all patient records.
    """
    return patients.find().all()


# =========================
# Demo flow
# =========================

if __name__ == "__main__":
    # Create patient
    jane = create_patient(
        patient_id="PT001",
        name="Jane Doe",
        age=42,
    )
    print("Created patient:", jane.name)

    # Add prescription
    rx = add_prescription(
        patient_id="PT001",
        drug_name="Amoxicillin",
        dosage="500mg",
        frequency="3x daily",
        duration_days=7,
    )
    print("Added prescription:", rx.drug_name)

    # Retrieve prescriptions
    print("\nPrescriptions for PT001:")
    for p in get_prescriptions("PT001"):
        print(f"- {p.drug_name}: {p.dosage}, {p.frequency} for {p.duration_days} days")

    # List all patients
    print("\nAll patients:")
    for patient in get_all_patients():
        print(f"- {patient.patient_id}: {patient.name} ({patient.age} years old)")

    driver.close()
