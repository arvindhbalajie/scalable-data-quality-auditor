import numpy as np
from typing import Dict, List

class SemanticIntegrityAuditor:
    """
    Tier 2 Data Integrity Layer.
    Audits the statistical validity of incoming streaming metrics to identify
    unrealistic spikes, sensor dropouts, or contextual operational anomalies.
    """
    def __init__(self, heart_rate_window_size: int = 5):
        # Keeps an in-memory window of recent records to evaluate statistical trends
        self.heart_rate_history: List[float] = []
        self.window_size = heart_rate_window_size
        self.flagged_anomalies_count = 0

    def audit_metrics(self, validated_packet: dict) -> dict:
        """
        Evaluates value-level integrity. If the record passes structural criteria
        but contains statistical impossibility, it is flagged semantically.
        """
        data = validated_packet.get("data", {})
        hr = data.get("heart_rate")
        sys_bp = data.get("systolic_bp")
        dia_bp = data.get("diastolic_bp")
        
        flags = []

        # 1. Semantic Check: Systolic pressure must inherently be higher than Diastolic pressure
        if sys_bp is not None and dia_bp is not None:
            if sys_bp <= dia_bp:
                flags.append(f"Physiological Paradox: Systolic BP ({sys_bp}) must exceed Diastolic BP ({dia_bp}).")

        # 2. Statistical Anomaly Check: Rapid physiological acceleration (Sensor Spike tracking)
        if hr is not None:
            if len(self.heart_rate_history) >= self.window_size:
                historical_mean = np.mean(self.heart_rate_history)
                historical_std = np.std(self.heart_rate_history)
                
                # If standard deviation is trivial, provide a default baseline variance barrier
                threshold_std = max(historical_std, 5.0)
                
                # Flag if the new reading is more than 3 standard deviations away from current patient baseline
                if abs(hr - historical_mean) > (3 * threshold_std):
                    flags.append(f"Statistical Outlier: Pulse rate jumped from baseline mean of {historical_mean:.1f} to {hr}.")
            
            # Maintain the moving window size limit
            self.heart_rate_history.append(hr)
            if len(self.heart_rate_history) > self.window_size:
                self.heart_rate_history.pop(0)

        # 3. Compile Tier 2 Integrity Decision Matrix
        if flags:
            self.flagged_anomalies_count += 1
            return {
                "status": "SEMANTIC_ANOMALY",
                "data": data,
                "violations": flags
            }
        
        return {
            "status": "CLEAN",
            "data": data,
            "violations": []
        }

# Execution Verification Suite
if __name__ == "__main__":
    auditor = SemanticIntegrityAuditor()
    print("=== Initializing Tier 2 Semantic Integrity Validation Matrix ===")

    # Seed the rolling patient history window with stable resting heart rate entries (approx 70-75 bpm)
    stable_stream = [70.0, 72.0, 71.5, 73.0, 74.0]
    for hr_value in stable_stream:
        auditor.audit_metrics({"data": {"heart_rate": hr_value, "systolic_bp": 120, "diastolic_bp": 80}})
        
    print(f"\n[Baseline Stream Setup Completed]: Current Window Mean: {np.mean(auditor.heart_rate_history):.2f} bpm")

    # Test Case A: Biological Paradox (Diastolic exceeds Systolic)
    paradox_packet = {
        "data": {
            "patient_id": "PT-94821",
            "heart_rate": 72.0,
            "systolic_bp": 90, 
            "diastolic_bp": 110 # Impossible: Diastolic cannot be higher than systolic
        }
    }
    
    # Test Case B: Hardware Artifact Spikes (Extreme sensor jump)
    sensor_spike_packet = {
        "data": {
            "patient_id": "PT-94821",
            "heart_rate": 185.0, # Massive, immediate jump from a baseline of ~72 bpm
            "systolic_bp": 122,
            "diastolic_bp": 81
        }
    }

    print("\n[Running Audit on Physiological Paradox]:")
    print(auditor.audit_metrics(paradox_packet))

    print("\n[Running Audit on Telemetry Sensor Artifact Jump]:")
    print(auditor.audit_metrics(sensor_spike_packet))

