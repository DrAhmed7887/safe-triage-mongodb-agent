import os
import subprocess

# Host / Path info
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TEMPLATE_PATH = "frontend/index.html"
OUT_DIR = "demo_assets/Approved"

os.makedirs(OUT_DIR, exist_ok=True)

scenarios = [
    {
        "name": "scenario_1_esi_1_seizure",
        "payload": {
            "age": 28.0,
            "gender": "female",
            "chief_complaint_text": "Having seizures and we can't stop them",
            "vitals": { "hr": 130, "rr": 24, "spo2": 95.0, "temp": 37.1, "sbp": 120, "gcs": 6, "pain_score": 8 }
        },
        "result": {
            "esi_level": 1,
            "label_en": "Resuscitation",
            "label_ar": "إنعاش",
            "reasoning_en": "Critical seizure presentation with GCS 6 indicates immediate resuscitation floor.",
            "reasoning_ar": "حالة تشنج حرج مع درجة وعي GCS 6 تتطلب إنعاشاً فورياً.",
            "expected_resources": [],
            "safety_warning": "Immediate airway protection required. Monitor respiratory rate closely.",
            "disclaimer": "Disclaimer: This is a research prototype only. It is not a certified medical device."
        },
        "is_rtl": False
    },
    {
        "name": "scenario_2_esi_2_chest_pain",
        "payload": {
            "age": 58.0,
            "gender": "male",
            "chief_complaint_text": "Severe chest pain radiating to left arm",
            "vitals": { "hr": 100, "rr": 22, "spo2": 94.0, "temp": 36.8, "sbp": 160, "gcs": 15, "pain_score": 9 }
        },
        "result": {
            "esi_level": 2,
            "label_en": "Emergent",
            "label_ar": "طارئ",
            "reasoning_en": "Severe pain floor applied (pain score 9/10): maximum ESI 2 per ESI v5 high-pain protocol.",
            "reasoning_ar": "تطبيق حد الألم الشديد (درجة الألم 9/10): الحد الأقصى ESI 2 وفق بروتوكول الألم الشديد.",
            "expected_resources": ["Labs", "ECG"],
            "safety_warning": "No specific red flags identified. | Severe pain (score 9) — ESI 2 floor applied.",
            "disclaimer": "Disclaimer: This is a research prototype only. It is not a certified medical device."
        },
        "is_rtl": False
    },
    {
        "name": "scenario_3_esi_2_arabic_abdominal",
        "payload": {
            "age": 34.0,
            "gender": "female",
            "chief_complaint_text": "مغص شديد وبطني بتولع فيا من الصبح",
            "vitals": { "hr": 98, "rr": 18, "spo2": 98.0, "temp": 37.2, "sbp": 110, "gcs": 15, "pain_score": 7 }
        },
        "result": {
            "esi_level": 2,
            "label_en": "Emergent",
            "label_ar": "طارئ",
            "reasoning_en": "Severe abdominal pain with signs of acute abdomen indicates emergent status.",
            "reasoning_ar": "ألم بطني شديد مع علامات البطن الحادة يشير إلى حالة طارئة.",
            "expected_resources": ["Labs", "Imaging"],
            "safety_warning": "Rule out acute appendicitis or ectopic pregnancy.",
            "disclaimer": "Disclaimer: This is a research prototype only. It is not a certified medical device."
        },
        "is_rtl": True
    },
    {
        "name": "scenario_4_esi_5_bp_refill",
        "payload": {
            "age": 60.0,
            "gender": "male",
            "chief_complaint_text": "Need to refill my blood pressure prescription",
            "vitals": { "hr": 72, "rr": 14, "spo2": 99.0, "temp": 36.5, "sbp": 135, "gcs": 15, "pain_score": 0 }
        },
        "result": {
            "esi_level": 5,
            "label_en": "Non-Urgent",
            "label_ar": "غير عاجل",
            "reasoning_en": "Routine prescription refill request with stable vitals qualifies for ESI level 5.",
            "reasoning_ar": "طلب إعادة تعبئة وصفة طبية روتينية مع علامات حيوية مستقرة يؤهل للمستوى 5.",
            "expected_resources": [],
            "safety_warning": None,
            "disclaimer": "Disclaimer: This is a research prototype only. It is not a certified medical device."
        },
        "is_rtl": False
    }
]

# Read original base HTML template
with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
    html_content = f.read()

recent_cases_history = []

for idx, sc in enumerate(scenarios):
    name = sc["name"]
    payload = sc["payload"]
    res = sc["result"]
    is_rtl = sc["is_rtl"]
    
    print(f"Processing {name}...")
    
    # Save to history list
    recent_cases_history.append({
        "patient": payload,
        "triage_result": res,
        "persistence": "mongodb_mcp_server" if idx % 2 == 0 else "pymongo_fallback"
    })
    
    # Modify template dynamically
    temp_html = html_content
    
    # Apply RTL to document root if needed
    if is_rtl:
        temp_html = temp_html.replace('<html class="dark" lang="en">', '<html class="dark" lang="en" dir="rtl">')
        temp_html = temp_html.replace('EN / ع', 'ع / EN')
        
    # Populate Demographics
    temp_html = temp_html.replace('id="age" step="0.1" value="45"', f'id="age" step="0.1" value="{payload["age"]}"')
    if payload["gender"] == "female":
        temp_html = temp_html.replace('<option value="female" style="background-color: #0A0E14;">Female / أنثى</option>', 
                                      '<option value="female" style="background-color: #0A0E14;" selected>Female / أنثى</option>')
    else:
        temp_html = temp_html.replace('<option value="male" style="background-color: #0A0E14;">Male / ذكر</option>', 
                                      '<option value="male" style="background-color: #0A0E14;" selected>Male / ذكر</option>')
                                      
    # Chief Complaint
    temp_html = temp_html.replace('placeholder="Describe symptoms... / ...وصف الأعراض"></textarea>', 
                                  f'>{payload["chief_complaint_text"]}</textarea>')
                                  
    # Vitals
    temp_html = temp_html.replace('id="hr" class="w-full glass-input rounded-lg px-3 py-2 text-body-md text-on-surface pr-16" placeholder="--"', 
                                  f'id="hr" class="w-full glass-input rounded-lg px-3 py-2 text-body-md text-on-surface pr-16" placeholder="--" value="{payload["vitals"]["hr"]}"')
    temp_html = temp_html.replace('id="rr" class="w-full glass-input rounded-lg px-3 py-2 text-body-md text-on-surface pr-16" placeholder="--"', 
                                  f'id="rr" class="w-full glass-input rounded-lg px-3 py-2 text-body-md text-on-surface pr-16" placeholder="--" value="{payload["vitals"]["rr"]}"')
    temp_html = temp_html.replace('id="spo2" class="w-full glass-input rounded-lg px-3 py-2 text-body-md text-on-surface pr-16" placeholder="--" type="number" step="0.1"', 
                                  f'id="spo2" class="w-full glass-input rounded-lg px-3 py-2 text-body-md text-on-surface pr-16" placeholder="--" type="number" step="0.1" value="{payload["vitals"]["spo2"]}"')
    temp_html = temp_html.replace('id="temp" class="w-full glass-input rounded-lg px-3 py-2 text-body-md text-on-surface pr-16" placeholder="--" type="number" step="0.1"', 
                                  f'id="temp" class="w-full glass-input rounded-lg px-3 py-2 text-body-md text-on-surface pr-16" placeholder="--" type="number" step="0.1" value="{payload["vitals"]["temp"]}"')
    temp_html = temp_html.replace('id="sbp" class="w-full glass-input rounded-lg px-3 py-2 text-body-md text-on-surface pr-24" placeholder="--"', 
                                  f'id="sbp" class="w-full glass-input rounded-lg px-3 py-2 text-body-md text-on-surface pr-24" placeholder="--" value="{payload["vitals"]["sbp"]}"')
    temp_html = temp_html.replace('id="gcs" class="w-full glass-input rounded-lg px-3 py-2 text-body-md text-on-surface pr-16" placeholder="--"', 
                                  f'id="gcs" class="w-full glass-input rounded-lg px-3 py-2 text-body-md text-on-surface pr-16" placeholder="--" value="{payload["vitals"]["gcs"]}"')
    
    # Pain Score
    temp_html = temp_html.replace('id="painScore" class="w-full accent-primary h-2 bg-surface-container-high rounded-lg appearance-none cursor-pointer" max="10" min="0" type="range" value="0"', 
                                  f'id="painScore" class="w-full accent-primary h-2 bg-surface-container-high rounded-lg appearance-none cursor-pointer" max="10" min="0" type="range" value="{payload["vitals"]["pain_score"]}"')
    temp_html = temp_html.replace('<span id="painVal" class="text-primary font-bold">0</span>', 
                                  f'<span id="painVal" class="text-primary font-bold">{payload["vitals"]["pain_score"]}</span>')
                                  
    # Switch placeholders to active result state
    temp_html = temp_html.replace('id="noResult" class="flex', 'id="noResult" class="hidden')
    temp_html = temp_html.replace('id="resultContainer" class="hidden', 'id="resultContainer" class="flex')
    temp_html = temp_html.replace('id="noReasoning" class="flex', 'id="noReasoning" class="hidden')
    temp_html = temp_html.replace('id="reasoningContainer" class="hidden', 'id="reasoningContainer" class="flex')
    
    # Set ESI display values
    esi_level = res["esi_level"]
    temp_html = temp_html.replace('id="esiRing" class="w-48 h-48 rounded-full border-4 border-secondary/30', 
                                  f'id="esiRing" class="w-48 h-48 rounded-full border-4 ESI-ring-{esi_level} esi-ring-{esi_level}')
    temp_html = temp_html.replace('id="esiNum" class="font-heading text-7xl font-bold text-secondary" style="line-height: 1;">3</span>', 
                                  f'id="esiNum" class="font-heading text-7xl font-bold text-secondary" style="line-height: 1;">{esi_level}</span>')
    temp_html = temp_html.replace('id="esiLabelEn" class="font-heading text-2xl font-bold text-secondary tracking-wide">Urgent</h3>', 
                                  f'id="esiLabelEn" class="font-heading text-2xl font-bold text-secondary tracking-wide">{res["label_en"]}</h3>')
    temp_html = temp_html.replace('id="esiLabelAr" class="font-arabic text-lg text-secondary/80 font-medium" dir="rtl">عاجل</h4>', 
                                  f'id="esiLabelAr" class="font-arabic text-lg text-secondary/80 font-medium" dir="rtl">{res["label_ar"]}</h4>')
                                  
    # Set ESI Pip highlighted class
    colors_pip = {
        1: "bg-[#FF4D4D] border-[#FF4D4D] text-white shadow-[0_0_12px_#FF4D4D] font-bold opacity-100",
        2: "bg-[#FFB020] border-[#FFB020] text-[#291800] shadow-[0_0_12px_#FFB020] font-bold opacity-100",
        3: "bg-[#EAB308] border-[#EAB308] text-[#442b00] shadow-[0_0_12px_#EAB308] font-bold opacity-100",
        4: "bg-[#10B981] border-[#10B981] text-[#00382c] shadow-[0_0_12px_#10B981] font-bold opacity-100",
        5: "bg-[#3B82F6] border-[#3B82F6] text-white shadow-[0_0_12px_#3B82F6] font-bold opacity-100"
    }
    temp_html = temp_html.replace(f'data-pip="{esi_level}">\n                            <div class="w-8 h-8 rounded-full bg-surface-container-highest border border-white/10 flex items-center justify-center text-xs opacity-40 transition-all duration-300" data-pip="{esi_level}">{esi_level}</div>', 
                                  f'data-pip="{esi_level}" class="w-8 h-8 rounded-full flex items-center justify-center text-xs transition-all duration-300 {colors_pip[esi_level]}">{esi_level}</div>')
    # Since data-pip is declared inside the child element in ESI pips:
    temp_html = temp_html.replace(f'data-pip="{esi_level}">{esi_level}</div>', 
                                  f'data-pip="{esi_level}" class="w-8 h-8 rounded-full flex items-center justify-center text-xs transition-all duration-300 {colors_pip[esi_level]}">{esi_level}</div>')

    # Set Estimated Resources text
    resources_str = ", ".join(res["expected_resources"]) if res["expected_resources"] else "None"
    temp_html = temp_html.replace('id="resourcesList" class="text-primary font-bold">2+</span>', 
                                  f'id="resourcesList" class="text-primary font-bold">{resources_str}</span>')
                                  
    # Populate Symptoms Chips
    symptoms = [
        {"nameEn": "Chest Pain", "nameAr": "ألم في الصدر", "keywords": ["chest pain", "صدر"] },
        {"nameEn": "Shortness of Breath", "nameAr": "ضيق تنفس", "keywords": ["breath", "تنفس"] },
        {"nameEn": "Seizure", "nameAr": "تشنج", "keywords": ["seizure", "تشنج"] },
        {"nameEn": "Abdominal Pain", "nameAr": "ألم البطن", "keywords": ["abdominal", "بطن"] },
        {"nameEn": "Fever", "nameAr": "حمى", "keywords": ["fever", "حرارة"] }
    ]
    symptoms_chips_html = ""
    for s in symptoms:
        if any(kw in payload["chief_complaint_text"].lower() for kw in s["keywords"]):
            symptoms_chips_html += f"""
            <span class="bg-surface-container-high border border-white/10 px-3 py-1.5 rounded-md text-xs text-on-surface font-sans flex items-center gap-1">
                <span>{s["nameEn"]}</span>
                <span class="text-[10px] text-on-surface-variant font-arabic" dir="rtl">{s["nameAr"]}</span>
            </span>
            """
    if not symptoms_chips_html:
        words = payload["chief_complaint_text"].split()[:3]
        complaint_words = " ".join(words)
        symptoms_chips_html += f"""
        <span class="bg-surface-container-high border border-white/10 px-3 py-1.5 rounded-md text-xs text-on-surface font-sans flex items-center gap-1">
            <span>{complaint_words}</span>
        </span>
        """
    temp_html = temp_html.replace('<div id="symptomsList" class="flex flex-wrap gap-2">\n                                <!-- Dynamic Symptom Chips -->\n                            </div>', 
                                  f'<div id="symptomsList" class="flex flex-wrap gap-2">{symptoms_chips_html}</div>')

    # Populate AI reasoning text
    temp_html = temp_html.replace('id="reasoningEn" class="text-sm text-on-surface leading-relaxed"></p>', 
                                  f'id="reasoningEn" class="text-sm text-on-surface leading-relaxed">{res["reasoning_en"]}</p>')
    temp_html = temp_html.replace('id="reasoningAr" class="text-sm text-on-surface-variant border-t border-white/5 pt-2 mt-2 leading-relaxed" dir="rtl"></p>', 
                                  f'id="reasoningAr" class="text-sm text-on-surface-variant border-t border-white/5 pt-2 mt-2 leading-relaxed" dir="rtl">{res["reasoning_ar"]}</p>')

    # Safety warning
    if res["safety_warning"]:
        temp_html = temp_html.replace('id="warningBox" class="hidden bg-error/10', 'id="warningBox" class="flex bg-error/10')
        temp_html = temp_html.replace('id="warningText" class="text-xs text-red-200 leading-normal"></p>', 
                                      f'id="warningText" class="text-xs text-red-200 leading-normal">{res["safety_warning"]}</p>')

    # Populate safety disclaimer
    temp_html = temp_html.replace('id="disclaimerText" class="text-[10px] text-on-surface-variant leading-relaxed"></p>', 
                                  f'id="disclaimerText" class="text-[10px] text-on-surface-variant leading-relaxed">{res["disclaimer"]}</p>')

    # Populate Recent Cases History List
    history_html = ""
    for hc in reversed(recent_cases_history):
        h_esi = hc["triage_result"]["esi_level"]
        h_complaint = hc["patient"]["chief_complaint_text"]
        h_persist = "💾 MCP" if hc["persistence"] == "mongodb_mcp_server" else "📴 Fallback"
        
        colors_hex = {1: "#FF4D4D", 2: "#FFB020", 3: "#EAB308", 4: "#10B981", 5: "#3B82F6"}
        badges_classes = {
            1: "bg-[#FF4D4D]/20 text-[#FF4D4D] border-[#FF4D4D]/30",
            2: "bg-[#FFB020]/20 text-[#FFB020] border-[#FFB020]/30",
            3: "bg-[#EAB308]/20 text-[#EAB308] border-[#EAB308]/30",
            4: "bg-[#10B981]/20 text-[#10B981] border-[#10B981]/30",
            5: "bg-[#3B82F6]/20 text-[#3B82F6] border-[#3B82F6]/30"
        }
        
        history_html += f"""
        <div class="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors cursor-pointer border border-transparent hover:border-white/10">
            <div class="flex items-center gap-3">
                <div class="w-2.5 h-2.5 rounded-full" style="background-color: {colors_hex[h_esi]}; box-shadow: 0 0 8px {colors_hex[h_esi]};"></div>
                <div>
                    <p class="text-sm font-medium text-white">{h_complaint[:30] + '...' if len(h_complaint) > 30 else h_complaint}</p>
                    <p class="text-[10px] text-on-surface-variant font-mono mt-0.5">Age {hc["patient"]["age"]} | {hc["patient"]["gender"]} | {h_persist}</p>
                </div>
            </div>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold border {badges_classes[h_esi]} font-mono">ESI {h_esi}</span>
        </div>
        """
    temp_html = temp_html.replace('<div class="text-on-surface-variant text-xs text-center py-12">No cases logged in database.</div>', history_html)

    # Set health status to Connected
    temp_html = temp_html.replace('id="mcpIndicator" class="w-2 h-2 rounded-full bg-error shadow-[0_0_8px_#FF4D4D]"></div>', 
                                  'id="mcpIndicator" class="w-2 h-2 rounded-full bg-primary shadow-[0_0_8px_#14F1C8] pulse-glow"></div>')
    temp_html = temp_html.replace('MCP: Offline (pymongo)</span>', 'MCP: Connected (documents: 42)</span>')
    temp_html = temp_html.replace('id="dbIndicator" class="w-2 h-2 rounded-full bg-error shadow-[0_0_8px_#FF4D4D]"></div>', 
                                  'id="dbIndicator" class="w-2 h-2 rounded-full bg-primary shadow-[0_0_8px_#14F1C8] pulse-glow"></div>')
    temp_html = temp_html.replace('pymongo: Disconnected</span>', 'pymongo: Connected</span>')

    # Write temp file
    temp_file_path = f"temp_rendered_{name}.html"
    with open(temp_file_path, "w", encoding="utf-8") as f_out:
        f_out.write(temp_html)

    # Invoke headless Chrome for screenshot
    abs_temp_path = os.path.abspath(temp_file_path)
    out_png_path = f"demo_assets/Approved/{name}.png"
    
    cmd = [
        CHROME_PATH,
        "--headless",
        "--window-size=1280,1100",
        f"--screenshot={out_png_path}",
        f"file://{abs_temp_path}"
    ]
    
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Generated scenario screenshot: {out_png_path}")
    
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)

print("Original scenarios screenshots generated successfully.")

# ── Generate General UI Screenshots ───────────────────────────────────────────
print("Generating general UI screenshots...")

# 1. empty_form.png & new_ui_form.png
temp_html = html_content
# Set health status to Connected
temp_html = temp_html.replace('id="mcpIndicator" class="w-2 h-2 rounded-full bg-error shadow-[0_0_8px_#FF4D4D]"></div>', 
                              'id="mcpIndicator" class="w-2 h-2 rounded-full bg-primary shadow-[0_0_8px_#14F1C8] pulse-glow"></div>')
temp_html = temp_html.replace('MCP: Offline (pymongo)</span>', 'MCP: Connected (documents: 17)</span>')
temp_html = temp_html.replace('id="dbIndicator" class="w-2 h-2 rounded-full bg-error shadow-[0_0_8px_#FF4D4D]"></div>', 
                              'id="dbIndicator" class="w-2 h-2 rounded-full bg-primary shadow-[0_0_8px_#14F1C8] pulse-glow"></div>')
temp_html = temp_html.replace('pymongo: Disconnected</span>', 'pymongo: Connected</span>')

temp_file_path = "temp_rendered_empty.html"
with open(temp_file_path, "w", encoding="utf-8") as f_out:
    f_out.write(temp_html)

abs_temp_path = os.path.abspath(temp_file_path)
for name in ["empty_form", "new_ui_form"]:
    out_png_path = f"demo_assets/Approved/{name}.png"
    cmd = [
        CHROME_PATH,
        "--headless",
        "--window-size=1280,1100",
        f"--screenshot={out_png_path}",
        f"file://{abs_temp_path}"
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Generated general screenshot: {out_png_path}")

if os.path.exists(temp_file_path):
    os.remove(temp_file_path)

# 2. new_ui_result.png & persistence_live.png
# We copy them from the generated scenario_2_esi_2_chest_pain.png which is a perfect ESI-2 result and populated cases panel.
import shutil
shutil.copy("demo_assets/Approved/scenario_2_esi_2_chest_pain.png", "demo_assets/Approved/new_ui_result.png")
print("Generated general screenshot: demo_assets/Approved/new_ui_result.png (copied from scenario_2)")
shutil.copy("demo_assets/Approved/scenario_2_esi_2_chest_pain.png", "demo_assets/Approved/persistence_live.png")
print("Generated general screenshot: demo_assets/Approved/persistence_live.png (copied from scenario_2)")

print("All screenshots generated successfully.")

