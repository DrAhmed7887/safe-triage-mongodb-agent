#!/usr/bin/env python3
"""
SAFE-Triage Demo Recording Script
Records a 90-second demo following demo_assets/DEMO_SCRIPT.md
Uses Playwright connected to the running Chrome instance via CDP.
Outputs: demo_assets/demo_video.mp4
"""

import os
import time
import subprocess
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

LIVE_URL = "https://safe-triage-mongodb-api-566848331149.us-central1.run.app"
FRAMES_DIR = Path("/tmp/demo_frames")
OUTPUT_DIR = Path("demo_assets")
OUTPUT_VIDEO = OUTPUT_DIR / "demo_video.mp4"
FFMPEG = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"

FPS_CAPTURE = 2   # capture at 2fps for live sections
FPS_OUTPUT  = 24  # output video framerate

frame_counter = 0


def take_frame(page, frames_dir):
    global frame_counter
    fpath = frames_dir / f"frame_{frame_counter:05d}.png"
    page.screenshot(path=str(fpath))
    frame_counter += 1
    return str(fpath)


def capture_live(page, frames_dir, duration_secs, fps=2):
    """Capture frames live for duration_secs at fps."""
    n = max(1, int(duration_secs * fps))
    interval = 1.0 / fps
    for _ in range(n):
        take_frame(page, frames_dir)
        time.sleep(interval)


def hold_last_frame(frames_dir, hold_secs, fps_out=24):
    """Duplicate last frame for hold_secs at output fps."""
    global frame_counter
    last = frames_dir / f"frame_{frame_counter - 1:05d}.png"
    n = int(hold_secs * fps_out)
    for _ in range(n):
        dst = frames_dir / f"frame_{frame_counter:05d}.png"
        shutil.copy(str(last), str(dst))
        frame_counter += 1


def click_scenario(page, idx: int):
    """Click the nth demo scenario seed button (0-indexed)."""
    page.evaluate(f"seedDemo({idx})")
    time.sleep(0.5)


def click_triage(page):
    """Click the submit / perform triage button."""
    page.click("#submitBtn")


def wait_for_result(page, timeout=20):
    """Wait until ESI result appears in the DOM."""
    try:
        # Wait for esi-badge or esiLabelAr to have content
        page.wait_for_function(
            """() => {
                const badge = document.querySelector('#esiLevelNum, #esiLabel, .esi-badge, [id*="esi"]');
                return badge && badge.textContent && badge.textContent.trim() !== '';
            }""",
            timeout=timeout * 1000
        )
    except:
        pass
    time.sleep(2)  # extra settle time


def scroll_to_history(page):
    """Smoothly scroll to history panel."""
    page.evaluate("""
        const hist = document.querySelector('.history-panel, [class*="history"], h3, h2, span');
        let target = null;
        document.querySelectorAll('*').forEach(el => {
            if (el.textContent && (el.textContent.toLowerCase().includes('recent triage') ||
                el.textContent.toLowerCase().includes('history') ||
                el.textContent.toLowerCase().includes('سجل'))) {
                if (!target && el.offsetParent !== null) target = el;
            }
        });
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        else window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    """)
    time.sleep(2)


def main():
    global frame_counter
    frame_counter = 0

    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    # Clean old frames
    for f in FRAMES_DIR.glob("*.png"):
        f.unlink()

    with sync_playwright() as p:
        print("🔌 Connecting to Chrome via CDP...")
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.set_viewport_size({"width": 1440, "height": 900})

        # ─────────────────────────────────────────────────────────────
        # SHOT 1: 0:00–0:15  |  Load console + show status badges
        # ─────────────────────────────────────────────────────────────
        print("🎬 Shot 1 (0:00-0:15): Loading live app...")
        page.goto(LIVE_URL, wait_until="networkidle", timeout=30000)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2)
        # Capture 15 seconds at 2fps
        capture_live(page, FRAMES_DIR, 15, fps=FPS_CAPTURE)
        print(f"   Frame count: {frame_counter}")

        # ─────────────────────────────────────────────────────────────
        # SHOT 2: 0:15–0:30  |  Seizure (GCS 6) → ESI 1 RED
        # ─────────────────────────────────────────────────────────────
        print("🎬 Shot 2 (0:15-0:30): Scenario 1 - Seizure ESI-1...")
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.3)
        click_scenario(page, 0)
        # Capture form being filled (2s)
        capture_live(page, FRAMES_DIR, 2, fps=FPS_CAPTURE)
        click_triage(page)
        wait_for_result(page)
        capture_live(page, FRAMES_DIR, 10, fps=FPS_CAPTURE)
        print(f"   Frame count: {frame_counter}")

        # ─────────────────────────────────────────────────────────────
        # SHOT 3: 0:30–0:45  |  Chest Pain (ACS) → ESI 2 ORANGE
        # ─────────────────────────────────────────────────────────────
        print("🎬 Shot 3 (0:30-0:45): Scenario 2 - Chest Pain ESI-2...")
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.3)
        click_scenario(page, 1)
        capture_live(page, FRAMES_DIR, 2, fps=FPS_CAPTURE)
        click_triage(page)
        wait_for_result(page)
        capture_live(page, FRAMES_DIR, 10, fps=FPS_CAPTURE)
        print(f"   Frame count: {frame_counter}")

        # ─────────────────────────────────────────────────────────────
        # SHOT 4: 0:45–1:00  |  Arabic Abdominal → ESI 2 (RTL)
        # ─────────────────────────────────────────────────────────────
        print("🎬 Shot 4 (0:45-1:00): Scenario 3 - Arabic Abdominal ESI-2...")
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.3)
        click_scenario(page, 2)
        capture_live(page, FRAMES_DIR, 2, fps=FPS_CAPTURE)
        click_triage(page)
        wait_for_result(page)
        capture_live(page, FRAMES_DIR, 10, fps=FPS_CAPTURE)
        print(f"   Frame count: {frame_counter}")

        # ─────────────────────────────────────────────────────────────
        # SHOT 5: 1:00–1:15  |  BP Refill → ESI 5 BLUE
        # ─────────────────────────────────────────────────────────────
        print("🎬 Shot 5 (1:00-1:15): Scenario 4 - BP Refill ESI-5...")
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.3)
        click_scenario(page, 3)
        capture_live(page, FRAMES_DIR, 2, fps=FPS_CAPTURE)
        click_triage(page)
        wait_for_result(page)
        capture_live(page, FRAMES_DIR, 10, fps=FPS_CAPTURE)
        print(f"   Frame count: {frame_counter}")

        # ─────────────────────────────────────────────────────────────
        # SHOT 6: 1:15–1:30  |  History logs panel + MCP badge
        # ─────────────────────────────────────────────────────────────
        print("🎬 Shot 6 (1:15-1:30): History logs & MCP badge...")
        scroll_to_history(page)
        time.sleep(1)
        capture_live(page, FRAMES_DIR, 14, fps=FPS_CAPTURE)
        print(f"   Frame count: {frame_counter}")

        browser.close()

    total_frames = frame_counter
    print(f"\n✅ Captured {total_frames} frames total")

    # ─────────────────────────────────────────────────────────────
    # Assemble video with ffmpeg
    # ─────────────────────────────────────────────────────────────
    print("🎬 Assembling MP4 video with ffmpeg...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ffmpeg_cmd = [
        FFMPEG, "-y",
        "-framerate", str(FPS_CAPTURE),   # input was captured at 2fps
        "-i", str(FRAMES_DIR / "frame_%05d.png"),
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-r", str(FPS_OUTPUT),            # output at 24fps
        "-vf", "scale=1440:900:flags=lanczos,format=yuv420p",
        str(OUTPUT_VIDEO)
    ]

    result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ FFmpeg error:\n{result.stderr[-2000:]}")
    else:
        size_mb = OUTPUT_VIDEO.stat().st_size / 1024 / 1024
        print(f"✅ Video saved: {OUTPUT_VIDEO} ({size_mb:.1f} MB)")
        # Get duration
        probe = subprocess.run(
            [FFMPEG, "-i", str(OUTPUT_VIDEO), "-f", "null", "-"],
            capture_output=True, text=True
        )
        for line in probe.stderr.split('\n'):
            if 'Duration' in line:
                print(f"   Duration: {line.strip()}")
                break


if __name__ == "__main__":
    main()
