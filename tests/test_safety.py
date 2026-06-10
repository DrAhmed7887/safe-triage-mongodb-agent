import os
import json

from agent.triage_tool import TriageTool
from backend.models import PatientInput

def load_demo_cases():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "demo_cases.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)

def test_zero_critical_under_triage():
    """
    Asserts that the ESI engine guarantees 0% critical under-triage.
    Expected ESI 1 or 2 must NEVER be assigned a less urgent triage level (3, 4, 5).
    """
    cases = load_demo_cases()
    tool = TriageTool()
    
    under_triage_count = 0
    total_cases = len(cases)
    
    print("\n--- CLINICAL SAFETY FLOOR ASSESSMENT LOG ---")
    for case in cases:
        # Construct PatientInput
        vitals_data = case.get("vitals", {})
        patient_input = PatientInput(
            age=case["age"],
            gender=case["sex"],
            chief_complaint_text=case.get("chief_complaint_ar") if "ar" in case.get("chief_complaint", "").lower() else case["chief_complaint"],
            vitals=vitals_data,
            pain_scale=vitals_data.get("pain_score")
        )
        
        # Evaluate offline
        evaluation = tool.evaluate_case(patient_input)
        assigned_level = evaluation["recommended_esi"]
        expected_level = case["expected_level"]
        
        print(f"Case {case['case_id']}: Expected ESI {expected_level} | Assigned ESI {assigned_level} | Complaint: {case['chief_complaint'][:40]}")
        
        # Verify Critical Under-Triage:
        # Expected ESI 1 or 2 must not be assigned > expected_level
        if expected_level in [1, 2] and assigned_level > expected_level:
            under_triage_count += 1
            print(f"  [FAIL] Under-triage detected for Case {case['case_id']}!")
            
    print(f"Total under-triage cases: {under_triage_count}/{total_cases}")
    assert under_triage_count == 0, f"Critical under-triage violation! Count: {under_triage_count}"
    print("--------------------------------------------")

if __name__ == "__main__":
    test_zero_critical_under_triage()
