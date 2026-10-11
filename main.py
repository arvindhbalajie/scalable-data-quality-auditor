import time
from src.schema_validator import StructuralSchemaAuditor
from src.semantic_auditor import SemanticIntegrityAuditor
from src.pipeline_logger import PipelineTelemetryLogger

def run_live_pipeline_simulation():
    print("====================================================")
    print("INITIALISING CLINICAL INTEGRITY PIPELINE SIMULATION")
    print("====================================================")
    
    # Initialize all three tiers we built
    tier1_structure = StructuralSchemaAuditor()
    tier2_semantics = SemanticIntegrityAuditor()
    tier3_logger = PipelineTelemetryLogger()
    
    # Simulating a live medical device data stream sending data packet by packet
    simulated_stream = [
        # Packet 1: Perfectly normal, healthy patient data
        {"patient_id": "PT-101", "timestamp": "2026-10-12T01:15:00Z", "heart_rate": 72.0, "systolic_bp": 120, "diastolic_bp": 80, "ingestion_node_id": 1},
        
        # Packet 2: Broken structure (Diastolic blood pressure is completely missing!)
        {"patient_id": "PT-102", "timestamp": "2026-10-12T01:15:05Z", "heart_rate": 68.5, "systolic_bp": 118, "ingestion_node_id": 1},
        
        # Packet 3: Biological impossibility (Diastolic pressure is higher than systolic!)
        {"patient_id": "PT-101", "timestamp": "2026-10-12T01:15:10Z", "heart_rate": 74.0, "systolic_bp": 90, "diastolic_bp": 115, "ingestion_node_id": 1},
        
        # Packet 4: Faulty hardware sensor artifact (Heart rate spikes impossibly high)
        {"patient_id": "PT-101", "timestamp": "2026-10-12T01:15:15Z", "heart_rate": 220.0, "systolic_bp": 121, "diastolic_bp": 79, "ingestion_node_id": 1}
    ]
    
    print("Starting Stream Processing Evaluation Loop...")
    print("====================================================")
    
    for idx, raw_packet in enumerate(simulated_stream, 1):
        print(f"\n[Processing Packet {idx} for Patient: {raw_packet.get('patient_id')}]")
        
        # Step 1: Run through structural check (Tier 1)
        t1_result = tier1_structure.validate_packet(raw_packet)
        
        if t1_result["status"] == "QUARANTINED":
            # If it fails structure, log it directly to quarantine (Tier 3)
            tier3_logger.isolate_and_log(t1_result)
            continue
            
        # Step 2: If it passes structure, check the semantic values inside (Tier 2)
        t2_result = tier2_semantics.audit_metrics(t1_result)
        
        # Step 3: Route to final database vault or quarantine folder based on the audit (Tier 3)
        tier3_logger.isolate_and_log(t2_result)
        
        time.sleep(0.5) # Simulate real-world stream delay

if __name__ == "__main__":
    run_live_pipeline_simulation()
