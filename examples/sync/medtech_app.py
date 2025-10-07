import uuid
from typing import Union
from pydantic import BaseModel
from pydantic import Field

from pydongo import as_collection
from pydongo import as_document
from pydongo.drivers.sync_mongo import DefaultMongoDBDriver

# === MODELS ===


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
    prescriptions: list[Prescription] = []


# === DB SETUP ===

driver = DefaultMongoDBDriver("mongodb://localhost:27017", "medtech_app")
driver.connect()
patients = as_collection(Patient, driver)


# === OPERATIONS ===


def create_patient(patient_id: str, name: str, age: int) -> Patient:
    patient = Patient(patient_id=patient_id, name=name, age=age)
    doc = as_document(patient, driver)
    doc.save()
    return doc


def add_prescription(
    patient_id: str, drug_name: str, dosage: str, frequency: str, duration_days: int
) -> Union[Prescription, None]:
    patient_doc = patients.find_one(patients.patient_id == patient_id)
    if not patient_doc:
        return None

    prescription = Prescription(
        drug_name=drug_name,
        dosage=dosage,
        frequency=frequency,
        duration_days=duration_days,
    )
    patient_doc.prescriptions.append(prescription)
    patient_doc.save()
    return prescription


def get_prescriptions(patient_id: str) -> list[Prescription]:
    patient_doc = patients.find_one(patients.patient_id == patient_id)
    return patient_doc.prescriptions if patient_doc else []


# === DEMO ===

if __name__ == "__main__":
    # Create a new patient
    pat = create_patient("PT001", "Jane Doe", 42)
    print("New patient:", pat.name)

    # Add a prescription
    rx = add_prescription("PT001", "Amoxicillin", "500mg", "3x daily", 7)
    print("Added prescription:", rx.drug_name)

    # Retrieve prescriptions
    print("Prescriptions for PT001:")
    for p in get_prescriptions("PT001"):
        print("-", p.drug_name, p.dosage, f"{p.frequency} for {p.duration_days} days")

    driver.close()
