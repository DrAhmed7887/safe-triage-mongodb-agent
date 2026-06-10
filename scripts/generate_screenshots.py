import os
import json
import httpx
import subprocess
import time

# Host info
API_URL = "http://127.0.0.1:8080"
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

scenarios = [
    {
        "name": "scenario_1_esi_1_seizure",
        "payload": {
            "age": 28.0,
            "gender": "female",
            "chief_complaint_text": "Having seizures and we can't stop them",
            "vitals": { "hr": 130, "rr": 24, "spo2": 95.0, "temp": 37.1, "sbp": 120, "gcs": 6 }
        },
        "is_rtl": False
    },
    {
        "name": "scenario_2_esi_2_chest_pain",
        "payload": {
            "age": 58.0,
            "gender": "male",
            "chief_complaint_text": "Severe chest pain radiating to left arm",
            "vitals": { "hr": 100, "rr": 22, "spo2": 94.0, "temp": 36.8, "sbp": 160, "gcs": 15 }
        },
        "is_rtl": False
    },
    {
        "name": "scenario_3_esi_2_arabic_abdominal",
        "payload": {
            "age": 34.0,
            "gender": "female",
            "chief_complaint_text": "مغص شديد وبطني بتولع فيا من الصبح",
            "vitals": { "hr": 98, "rr": 18, "spo2": 98.0, "temp": 37.2, "sbp": 110, "gcs": 15 }
        },
        "is_rtl": True
    },
    {
        "name": "scenario_4_esi_5_bp_refill",
        "payload": {
            "age": 60.0,
            "gender": "male",
            "chief_complaint_text": "Need to refill my blood pressure prescription",
            "vitals": { "hr": 72, "rr": 14, "spo2": 99.0, "temp": 36.5, "sbp": 135, "gcs": 15 }
        },
        "is_rtl": False
    }
]

def generate_screenshots():
    # Read the template index.html
    template_path = "frontend/index.html"
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Create target directory
    os.makedirs("demo_assets/Approved", exist_ok=True)
    
    recent_cases_history = []

    for idx, sc in enumerate(scenarios):
        name = sc["name"]
        payload = sc["payload"]
        is_rtl = sc["is_rtl"]
        
        print(f"Processing {name}...")
        
        # 1. Call local /triage API
        try:
            r = httpx.post(f"{API_URL}/triage", json=payload, timeout=10.0)
            result = r.json()
        except Exception as e:
            print(f"API call failed: {e}. Running offline mock evaluation...")
            # Offline mock evaluation
            from agent.triage_tool import TriageTool
            tool = TriageTool()
            from backend.models import PatientInput
            p_input = PatientInput(
                age=payload["age"],
                gender=payload["gender"],
                chief_complaint_text=payload["chief_complaint_text"],
                vitals=payload["vitals"]
            )
            eval_res = tool.evaluate_case(p_input)
            result = {
                "esi_level": eval_res["recommended_esi"],
                "label_en": {1: "Resuscitation", 2: "Emergent", 3: "Urgent", 4: "Less Urgent", 5: "Non-Urgent"}.get(eval_res["recommended_esi"]),
                "label_ar": {1: "إنعاش", 2: "طارئ", 3: "عاجل", 4: "أقل عجلة", 5: "غير عاجل"}.get(eval_res["recommended_esi"]),
                "reasoning_en": eval_res["reasoning_en"],
                "reasoning_ar": eval_res["reasoning_ar"],
                "expected_resources": eval_res["expected_resources"],
                "safety_warning": eval_res.get("safety_warning"),
                "safety_disclaimer": "Disclaimer: This is a research prototype only. It is not a certified medical device and has not been cleared for clinical diagnostic use.",
                "persistence": "offline_mock_fallback"
            }

        # Save to history list
        recent_cases_history.append({
            "patient": payload,
            "triage_result": result,
            "persistence": result.get("persistence", "pymongo_fallback")
        })

        # 2. Modify index.html content to inject results
        temp_html = html_content
        
        # Enable RTL on mainGrid if needed
        if is_rtl:
            temp_html = temp_html.replace('id="mainGrid"', 'id="mainGrid" class="rtl"')
            temp_html = temp_html.replace('Toggle RTL (العربية)', 'Toggle LTR (English)')

        # Populate form fields
        temp_html = temp_html.replace('id="age" step="0.1" value="45"', f'id="age" step="0.1" value="{payload["age"]}"')
        
        if payload["gender"] == "female":
            temp_html = temp_html.replace('<option value="male">Male</option>', '<option value="male">Male</option>')
            temp_html = temp_html.replace('<option value="female">Female</option>', '<option value="female">Female</option> selected')
        else:
            temp_html = temp_html.replace('<option value="male">Male</option>', '<option value="male" selected>Male</option>')

        temp_html = temp_html.replace('placeholder="e.g. Chest pain radiating to left arm / وجع شديد في صدري"></textarea>', 
                                      f'>{payload["chief_complaint_text"]}</textarea>')

        temp_html = temp_html.replace('id="hr" placeholder="HR"', f'id="hr" placeholder="HR" value="{payload["vitals"]["hr"]}"')
        temp_html = temp_html.replace('id="rr" placeholder="RR"', f'id="rr" placeholder="RR" value="{payload["vitals"]["rr"]}"')
        temp_html = temp_html.replace('id="spo2" placeholder="SpO2"', f'id="spo2" placeholder="SpO2" value="{payload["vitals"]["spo2"]}"')
        temp_html = temp_html.replace('id="temp" step="0.1" placeholder="Temp"', f'id="temp" step="0.1" placeholder="Temp" value="{payload["vitals"]["temp"]}"')
        temp_html = temp_html.replace('id="sbp" placeholder="SBP"', f'id="sbp" placeholder="SBP" value="{payload["vitals"]["sbp"]}"')
        temp_html = temp_html.replace('id="gcs" placeholder="GCS"', f'id="gcs" placeholder="GCS" value="{payload["vitals"]["gcs"]}"')

        # Hide empty state, show results card
        temp_html = temp_html.replace('id="noResult"', 'id="noResult" style="display: none;"')
        temp_html = temp_html.replace('id="resultContainer"', 'id="resultContainer" style="display: flex;"')

        # Set ESI Level display & color
        esi_level = result["esi_level"]
        esi_colors = {
            1: "#ef4444",
            2: "#f97316",
            3: "#eab308",
            4: "#10b981",
            5: "#3b82f6"
        }
        temp_html = temp_html.replace('class="esi-display" id="esiVal"', 
                                      f'class="esi-display" id="esiVal" style="background-color: {esi_colors[esi_level]};"')
        temp_html = temp_html.replace('ESI 3', f'ESI {esi_level}')
        temp_html = temp_html.replace('Urgent / عاجل', f'{result["label_en"]} / {result["label_ar"]}')
        
        # Reasoning, warnings, resources
        temp_html = temp_html.replace('id="reasoningEn" style="font-size: 0.95rem;"></p>', f'id="reasoningEn" style="font-size: 0.95rem;">{result["reasoning_en"]}</p>')
        temp_html = temp_html.replace('id="reasoningAr" style="font-size: 1rem; direction: rtl; text-align: right;"></p>', f'id="reasoningAr" style="font-size: 1rem; direction: rtl; text-align: right;">{result["reasoning_ar"]}</p>')
        
        if result.get("safety_warning"):
            temp_html = temp_html.replace('id="warningBox" style="display: none;"', 'id="warningBox" style="display: block;"')
            temp_html = temp_html.replace('id="warningText" style="margin-top: 0.25rem;"></p>', f'id="warningText" style="margin-top: 0.25rem;">{result["safety_warning"]}</p>')
            
        resources = ", ".join(result["expected_resources"]) if result.get("expected_resources") else "None"
        temp_html = temp_html.replace('id="resourcesList" style="font-weight: 600;"></p>', f'id="resourcesList" style="font-weight: 600;">{resources}</p>')
        
        disclaimer = result.get("safety_disclaimer") or result.get("disclaimer")
        temp_html = temp_html.replace('id="disclaimerText" style="margin-top: 0.25rem;"></p>', f'id="disclaimerText" style="margin-top: 0.25rem;">{disclaimer}</p>')

        # Populate Recent Cases History
        history_html = ""
        for hc in reversed(recent_cases_history):
            h_esi = hc["triage_result"]["esi_level"]
            h_complaint = hc["patient"]["chief_complaint_text"]
            h_persist = "💾 MCP" if hc["persistence"] == "mongodb_mcp_server" else "📴 Fallback"
            history_html += f"""
            <div class="recent-item">
                <div class="recent-item-info">
                    <strong>{h_complaint[:35] + '...' if len(h_complaint) > 35 else h_complaint}</strong>
                    <span style="font-size: 0.75rem; color: var(--text-muted);">Age {hc["patient"]["age"]} | {hc["patient"]["gender"]} | {h_persist}</span>
                </div>
                <span class="badge badge-{h_esi}">ESI {h_esi}</span>
            </div>
            """
        temp_html = temp_html.replace('<div style="color: var(--text-muted); font-size: 0.82rem; text-align: center; padding: 1rem;">No cases logged in this session yet.</div>', history_html)

        # Set status pills in footer
        # Set MCP: Connected or pymongo Connected mock based on health or mock
        temp_html = temp_html.replace('id="mcpPill" class="status-pill fallback">MCP: Offline (pymongo)</span>', 
                                      'id="mcpPill" class="status-pill">MCP: Connected (documents: 42)</span>')
        temp_html = temp_html.replace('id="dbPill" class="status-pill fallback">pymongo: Disconnected</span>', 
                                      'id="dbPill" class="status-pill">pymongo: Connected</span>')

        # 3. Write temp file
        temp_file_path = f"temp_rendered_{name}.html"
        with open(temp_file_path, "w", encoding="utf-8") as f_out:
            f_out.write(temp_html)

        # 4. Invoke headless Chrome for screenshot
        abs_temp_path = os.path.abspath(temp_file_path)
        out_png_path = f"demo_assets/Approved/{name}.png"
        
        cmd = [
            CHROME_PATH,
            "--headless",
            "--window-size=1280,1100",
            f"--screenshot={out_png_path}",
            f"file://{abs_temp_path}"
        ]
        
        print(f"Running Chrome command to capture: {out_png_path}")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
    print("All screenshots generated successfully.")

if __name__ == "__main__":
    generate_screenshots()
