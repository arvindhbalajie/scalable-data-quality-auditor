import json
import logging
from datetime import datetime
from pathlib import Path

class PipelineTelemetryLogger:
    """
    Tier 3 Monitoring & Quarantine Isolation Layer.
    Intercepts anomalous data packets and saves them to a secure isolation zone 
    while generating real-time audit logs for systemic reliability tracking.
    """
    def __init__(self, base_dir: str = "."):
        self.base_path = Path(base_dir)
        self.quarantine_path = self.base_path / "data" / "quarantine"
        self.processed_path = self.base_path / "data" / "processed"
        
        # Ensure system data sub-directories exist dynamically
        self.quarantine_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize internal logger configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] Telemetry Core: %(message)s',
            handlers=[logging.StreamHandler()]
        )
        self.logger = logging.getLogger("PipelineTelemetryMatrix")

    def isolate_and_log(self, audit_result: dict) -> str:
        """
        Processes the structural and semantic audit result payloads.
        Routes clean packets to processed storage and corrupt blocks to quarantine.
        """
        status = audit_result.get("status", "UNKNOWN")
        record_data = audit_result.get("data", {})
        patient_id = record_data.get("patient_id", "UNKNOWN_PT")
        timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
        
        # Unique identifier token for generating physical files
        filename = f"{patient_id}_{timestamp_str}.json"

        if status in ["QUARANTINED", "SEMANTIC_ANOMALY"]:
            target_file = self.quarantine_path / filename
            self.logger.warning(
                f"ALERT: Malformed/Anomalous Data Intercepted! "
                f"Patient: {patient_id} | Pipeline Action: Diverting packet to Quarantine Box."
            )
            
            # Persist raw corrupted payload to the isolated disk layer for deep root-cause auditing
            with open(target_file, "w") as f:
                json.dump(audit_result, f, indent=4)
            return f"QUARANTINED -> {target_file}"
            
        elif status in ["PASSED", "CLEAN"]:
            target_file = self.processed_path / filename
            self.logger.info(f"SUCCESS: System integrity verified for Patient: {patient_id}. Writing to Staging Vault.")
            
            with open(target_file, "w") as f:
                json.dump(record_data, f, indent=4)
            return f"PROCESSED -> {target_file}"
        
        else:
            self.logger.error(f"CRITICAL: Unrecognized ingestion state token: {status}")
            return "ERROR_UNKNOWN_STATE"

# Local Sandbox Unit Execution Test
if __name__ == "__main__":
    print("=== Initializing Tier 3 Pipeline Isolation Router Engine ===")
    pipeline_manager = PipelineTelemetryLogger()

    # Case A: Simulating the execution callback output of a Tier 1 validation error
    sample_structural_fail = {
        "status": "QUARANTINED",
        "data": {"patient_id": "PT-ERR-01", "heart_rate": -99.0, "systolic_bp": 120},
        "error": [{"loc": ["heart_rate"], "msg": "Input score below physical structural boundary criteria."}]
    }

    # Case B: Simulating the execution callback output of a successful validation track
    sample_clean_pass = {
        "status": "CLEAN",
        "data": {"patient_id": "PT-GOOD-99", "heart_rate": 72.0, "systolic_bp": 120, "diastolic_bp": 80}
    }

    print("\n[Executing Routing Logic on Failed Ingestion Stream Block]:")
    pipeline_manager.isolate_and_log(sample_structural_fail)

    print("\n[Executing Routing Logic on Clean Ingestion Stream Block]:")
    pipeline_manager.isolate_and_log(sample_clean_pass)

