import os
import subprocess

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def generate_diagram():
    html_canvas = """<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            background-color: #070a13;
            color: #f9fafb;
            font-family: 'system-ui', -apple-system, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            padding: 0;
        }
        .canvas {
            width: 1000px;
            height: 600px;
            background: radial-gradient(circle at 50% 50%, #0e1628 0%, #070a13 100%);
            border: 2px solid #1f2937;
            border-radius: 24px;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            padding: 2rem;
            box-sizing: border-box;
            position: relative;
        }
        h2 {
            margin: 0 0 0.5rem 0;
            font-weight: 800;
            background: linear-gradient(135deg, #a5b4fc 0%, #6366f1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.8rem;
            letter-spacing: -0.01em;
        }
        p {
            margin: 0 0 2rem 0;
            color: #9ca3af;
            font-size: 0.95rem;
        }
    </style>
</head>
<body>
    <div class="canvas">
        <h2>SAFE-Triage Agent Architecture Pipeline</h2>
        <p>MongoDB Track — Real-time Emergency Ingestion, Classification & Persistence Flows</p>
        
        <svg width="936" height="420" viewBox="0 0 936 420" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- Definitions for Gradients -->
            <defs>
                <linearGradient id="grad-input" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#3b82f6" />
                    <stop offset="100%" stop-color="#1d4ed8" />
                </linearGradient>
                <linearGradient id="grad-fastapi" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#8b5cf6" />
                    <stop offset="100%" stop-color="#6d28d9" />
                </linearGradient>
                <linearGradient id="grad-gemini" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#ec4899" />
                    <stop offset="100%" stop-color="#be185d" />
                </linearGradient>
                <linearGradient id="grad-engine" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#f97316" />
                    <stop offset="100%" stop-color="#c2410c" />
                </linearGradient>
                <linearGradient id="grad-mcp" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#10b981" />
                    <stop offset="100%" stop-color="#047857" />
                </linearGradient>
                <linearGradient id="grad-atlas" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#059669" />
                    <stop offset="100%" stop-color="#064e3b" />
                </linearGradient>
                <linearGradient id="grad-fallback" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#ef4444" />
                    <stop offset="100%" stop-color="#b91c1c" />
                </linearGradient>
                
                <!-- Glow Filters -->
                <filter id="glow-mcp" x="-10%" y="-10%" width="120%" height="120%">
                    <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#10b981" flood-opacity="0.3"/>
                </filter>
            </defs>

            <!-- Grid lines background -->
            <path d="M 0 50 L 936 50 M 0 150 L 936 150 M 0 250 L 936 250 M 0 350 L 936 350" stroke="#111827" stroke-width="1"/>
            <path d="M 150 0 L 150 420 M 350 0 L 350 420 M 550 0 L 550 420 M 750 0 L 750 420" stroke="#111827" stroke-width="1"/>

            <!-- Node 1: Patient Input -->
            <rect x="10" y="140" width="160" height="90" rx="16" fill="url(#grad-input)" stroke="#3b82f6" stroke-width="2"/>
            <text x="90" y="180" fill="#ffffff" font-size="14" font-weight="700" text-anchor="middle">Patient Ingestion</text>
            <text x="90" y="200" fill="#bfdbfe" font-size="11" font-weight="500" text-anchor="middle">Chief Complaint (EN/AR)</text>
            <text x="90" y="215" fill="#bfdbfe" font-size="11" font-weight="500" text-anchor="middle">+ Vitals &amp; Pain Scale</text>

            <!-- Connector 1 -> 2 -->
            <path d="M 170 185 L 210 185" stroke="#3b82f6" stroke-width="3" marker-end="url(#arrow)"/>
            
            <!-- Node 2: FastAPI Agent -->
            <rect x="210" y="140" width="160" height="90" rx="16" fill="url(#grad-fastapi)" stroke="#8b5cf6" stroke-width="2"/>
            <text x="290" y="180" fill="#ffffff" font-size="14" font-weight="700" text-anchor="middle">FastAPI Agent</text>
            <text x="290" y="200" fill="#ddd6fe" font-size="11" font-weight="500" text-anchor="middle">Orchestrates workflow</text>
            <text x="290" y="215" fill="#ddd6fe" font-size="11" font-weight="500" text-anchor="middle">Bilingual Routing</text>

            <!-- Connector 2 -> 3 -->
            <path d="M 370 170 L 410 120" stroke="#a78bfa" stroke-width="2" stroke-dasharray="4" marker-end="url(#arrow)"/>
            <text x="382" y="132" fill="#c084fc" font-size="10" font-weight="600" text-anchor="middle">API</text>

            <!-- Node 3: Gemini 2.0 Flash -->
            <rect x="410" y="60" width="180" height="85" rx="16" fill="url(#grad-gemini)" stroke="#ec4899" stroke-width="2"/>
            <text x="500" y="95" fill="#ffffff" font-size="14" font-weight="700" text-anchor="middle">Gemini 2.0 Flash</text>
            <text x="500" y="115" fill="#fbcfe8" font-size="11" font-weight="500" text-anchor="middle">Vertex AI Extractions</text>
            <text x="500" y="130" fill="#fbcfe8" font-size="9" font-style="italic" text-anchor="middle">Bilingual Reasoning Drafts</text>

            <!-- Connector 3 -> 4 -->
            <path d="M 500 145 L 500 175" stroke="#f472b6" stroke-width="2" marker-end="url(#arrow)"/>

            <!-- Connector 2 -> 4 -->
            <path d="M 370 195 L 410 195" stroke="#8b5cf6" stroke-width="3" marker-end="url(#arrow)"/>
            <text x="390" y="210" fill="#a78bfa" font-size="10" font-weight="600" text-anchor="middle">Direct</text>

            <!-- Node 4: Deterministic ESI Engine -->
            <rect x="410" y="180" width="180" height="110" rx="16" fill="url(#grad-engine)" stroke="#f97316" stroke-width="2"/>
            <text x="500" y="210" fill="#ffffff" font-size="14" font-weight="700" text-anchor="middle">Deterministic Engine</text>
            <text x="500" y="230" fill="#ffedd5" font-size="11" font-weight="600" text-anchor="middle">RULES WIN OVER AI</text>
            <text x="500" y="250" fill="#fed7aa" font-size="10" font-style="italic" text-anchor="middle">Clinical Vital Floors (ESI 1/2)</text>
            <text x="500" y="265" fill="#fed7aa" font-size="10" font-style="italic" text-anchor="middle">Red-flag / Pain Protocols</text>

            <!-- Connector 4 -> 5 (Primary Path) -->
            <path d="M 590 220 L 630 185" stroke="#34d399" stroke-width="3" marker-end="url(#arrow)"/>
            <text x="612" y="195" fill="#34d399" font-size="10" font-weight="700" text-anchor="middle">MCP</text>

            <!-- Connector 4 -> 6 (Fallback Path) -->
            <path d="M 590 250 L 630 285" stroke="#f87171" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arrow)"/>
            <text x="612" y="280" fill="#f87171" font-size="10" font-weight="700" text-anchor="middle">Fallback</text>

            <!-- Node 5: MongoDB MCP Server -->
            <rect x="630" y="125" width="160" height="90" rx="16" fill="url(#grad-mcp)" stroke="#10b981" stroke-width="2" filter="url(#glow-mcp)"/>
            <text x="710" y="165" fill="#ffffff" font-size="13" font-weight="700" text-anchor="middle">MongoDB MCP Server</text>
            <text x="710" y="185" fill="#a7f3d0" font-size="11" font-weight="500" text-anchor="middle">mcp SDK Client (stdio)</text>
            <text x="710" y="200" fill="#a7f3d0" font-size="10" font-style="italic" text-anchor="middle">insert-many / find / count</text>

            <!-- Node 6: PyMongo Fallback -->
            <rect x="630" y="255" width="160" height="90" rx="16" fill="url(#grad-fallback)" stroke="#ef4444" stroke-width="2"/>
            <text x="710" y="295" fill="#ffffff" font-size="13" font-weight="700" text-anchor="middle">pymongo Fallback</text>
            <text x="710" y="315" fill="#fecaca" font-size="11" font-weight="500" text-anchor="middle">Direct DB Driver</text>
            <text x="710" y="330" fill="#fecaca" font-size="10" font-style="italic" text-anchor="middle">Native standard query</text>

            <!-- Node 7: MongoDB Atlas -->
            <rect x="830" y="190" width="95" height="95" rx="47.5" fill="url(#grad-atlas)" stroke="#34d399" stroke-width="2"/>
            <text x="877" y="240" fill="#ffffff" font-size="13" font-weight="800" text-anchor="middle">MongoDB</text>
            <text x="877" y="255" fill="#a7f3d0" font-size="11" font-weight="700" text-anchor="middle">Atlas DB</text>

            <!-- Connectors to Atlas -->
            <path d="M 790 170 L 838 210" stroke="#34d399" stroke-width="3" marker-end="url(#arrow)"/>
            <path d="M 790 300 L 838 260" stroke="#ef4444" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arrow)"/>

            <!-- Arrow marker definition -->
            <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#e5e7eb" />
            </marker>
        </svg>
    </div>
</body>
</html>
"""
    
    # Save the HTML canvas
    temp_html_path = "temp_diagram.html"
    with open(temp_html_path, "w", encoding="utf-8") as f:
        f.write(html_canvas)
        
    out_png_path = "demo_assets/Approved/architecture.png"
    
    # Invoke headless Chrome to screenshot
    cmd = [
        CHROME_PATH,
        "--headless",
        "--window-size=1040,650",
        f"--screenshot={out_png_path}",
        f"file://{os.path.abspath(temp_html_path)}"
    ]
    
    print(f"Generating diagram screenshot: {out_png_path}")
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Clean up
    if os.path.exists(temp_html_path):
        os.remove(temp_html_path)
        
    print("Architecture diagram generated successfully.")

if __name__ == "__main__":
    generate_diagram()
