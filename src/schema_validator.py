from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError

# Tier 1 Structural Blueprints: Defining what a clean patient record must look like
class ClinicalRecordSchema(BaseModel):
    patient_id: str = Field(..., description="Unique alphanumeric identifier for the patient")
    timestamp: datetime = Field(..., description="ISO 8601 formatted ingestion timestamp")
    heart_rate: float = Field(..., ge=30.0, le=250.0, description="Patient heart rate in bpm")
    systolic_bp: int = Field(..., ge=50, le=250, description="Systolic blood pressure")
    diastolic_bp: int = Field(..., ge=30, le=150, description="Diastolic blood pressure")
    oximeter_sp_o2: Optional[float] = Field(None, ge=50.0, le=100.0, description="Oxygen saturation percentage")
    ingestion_node_id: int = Field(..., description="ID of the routing edge server")

class StructuralSchemaAuditor:
    """
    Tier 1 Data Integrity Layer. 
    Intercepts incoming raw data streams and screens for syntactic errors or missing fields.
    """
    def __init__(self):
        self.passed_count = 0
        self.quarantined_count = 0

    def validate_packet(self, raw_json_data: dict) -> dict:
        """
        Validates a single data packet against the structural blueprint.
        Diverts corrupt files to an isolated dictionary layer if validation fails.
        """
        try:
            # Attempt to force validate the incoming packet against our blueprint rules
            validated_record = ClinicalRecordSchema(**raw_json_data)
            self.passed_count += 1
            return {
                "status": "PASSED",
                "data": validated_record.model_dump(),
                "error": None
            }
        except ValidationError as e:
            self.quarantined_count += 1
            # Capture the exact structural path where the schema mutation occurred
            return {
                "status": "QUARANTINED",
                "data": raw_json_data,
                "error": e.errors()
            }

# Demonstration Execution for Academic Validation
if __name__ == "__main__":
    auditor = StructuralSchemaAuditor()
    print("=== Initializing Ingestion Layer Verification Suite ===")
    
    # 1. Simulating a Perfectly Structured Packet
    clean_sample = {
        "patient_id": "PT-94821",
        "timestamp": "2026-10-12T01:00:00Z",
        "heart_rate": 72.5,
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "oximeter_sp_o2": 98.2,
        "ingestion_node_id": 4
    }
    
    # 2. Simulating a Corrupted Packet (Missing diastolic pressure and heart rate is out of realistic physical bounds)
    corrupted_sample = {
        "patient_id": "PT-00341",
        "timestamp": "2026-10-12T01:01:00Z",
        "heart_rate": -5.0, # Fatal structural boundary failure
        "systolic_bp": 115,
        # "diastolic_bp" is missing entirely
        "ingestion_node_id": 2
    }
    
    # Execution Test Run
    print("\n[Testing Clean Packet Ingestion]:")
    print(auditor.validate_packet(clean_sample)["status"])
    
    print("\n[Testing Corrupted Schema Drift Packet Ingestion]:")
    result = auditor.validate_packet(corrupted_sample)
    print(f"Status: {result['status']}")
    print(f"Flagged Anomalies: {result['error']}")

