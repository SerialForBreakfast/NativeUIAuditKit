import json, os, subprocess, time
from ultralytics import YOLO

AATV = "/Users/josephmccraw/Library/Developer/Xcode/DerivedData/TVTestRig-bfjtodidumtdyagsgxcmwrmheuxr/Build/Products/Debug/TVTestRig.app/Contents/Helpers/aatv"
DEVICE_ID = "8D80F616-6C12-49A6-9015-8F594EE5F24E"
SESSION_DIR = "/Users/josephmccraw/Library/Containers/com.showblender.TVTestRig/Data/.tvtr/Evidence/Sessions/5699c327-bad3-482c-9dbf-7f9ec8ade0a5/screens"
OUTPUT_DIR = "dataset/tvos_settings"
MODEL_PATH = "NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.pt"
OCR_BIN = "scripts/ocr_helper"

os.makedirs(OUTPUT_DIR, exist_ok=True)
yolo_model = YOLO(MODEL_PATH)

def run_cmd(args):
    res = subprocess.run(args, capture_output=True, text=True)
    return res.stdout

def press(btn):
    run_cmd([AATV, "remote", "press", btn, "--device-id", DEVICE_ID])
    time.sleep(0.4)

def navigate(btn, count):
    run_cmd([AATV, "remote", "navigate", btn, "--count", str(count), "--device-id", DEVICE_ID])
    time.sleep(0.4)

def wait_stable():
    run_cmd([AATV, "observe", "wait-stable", "--json"])

def get_latest_screen():
    files = [f for f in os.listdir(SESSION_DIR) if f.endswith(".png")]
    files.sort(key=lambda f: os.path.getmtime(os.path.join(SESSION_DIR, f)), reverse=True)
    return os.path.join(SESSION_DIR, files[0]) if files else None

def ocr_screen(image_path):
    res = subprocess.run([OCR_BIN, image_path], capture_output=True, text=True)
    lines = [l.strip().split("|") for l in res.stdout.strip().split("\n") if "|" in l]
    return lines # [(text, x, y)]

def capture_and_qualify(screen_id, section_name):
    wait_stable()
    src = get_latest_screen()
    dest_png = os.path.join(OUTPUT_DIR, f"{screen_id}.png")
    dest_json = os.path.join(OUTPUT_DIR, f"{screen_id}.json")
    dest_res = os.path.join(OUTPUT_DIR, f"{screen_id}_result.json")

    subprocess.run(["cp", src, dest_png])
    sha = subprocess.run(["shasum", "-a", "256", dest_png], capture_output=True, text=True).stdout.split()[0]

    sidecar = {
      "schemaVersion": "1.0",
      "imageSHA256": sha,
      "captureSource": "realAppleTVTVTestRig",
      "image": {
        "fileName": f"{screen_id}.png",
        "pixelWidth": 1920,
        "pixelHeight": 1080,
        "scale": 1,
        "platform": "tvOS",
        "osVersion": "tvOS 18.x",
        "deviceName": "Apple TV 4K",
        "interfaceIdiom": "tv",
        "orientation": "landscape",
        "colorScheme": "dark",
        "dynamicTypeSize": "large",
        "locale": "en_US",
        "layoutDirection": "ltr",
        "safeAreaInsets": {"top": 60, "left": 90, "bottom": 60, "right": 90},
        "reduceTransparency": False,
        "increaseContrast": False,
        "boldText": False,
        "buttonShapes": False,
        "onOffLabels": False,
        "smartInvert": False
      },
      "generatorProfile": {
        "templateFamily": "tvOSSettingsHierarchy",
        "seed": 0,
        "generatorVersion": "tvtestrig-1.0",
        "section": section_name
      },
      "elements": []
    }
    with open(dest_json, "w") as f:
        json.dump(sidecar, f, indent=2)

    results = yolo_model.predict(dest_png, conf=0.20, verbose=False)
    detections = []
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            name = yolo_model.names[cls_id]
            conf = float(box.conf[0])
            xyxy = [round(x, 1) for x in box.xyxy[0].tolist()]
            detections.append({'type': name, 'confidence': round(conf, 3), 'box': xyxy})

    with open(dest_res, "w") as f:
        json.dump(detections, f, indent=2)

    ocr_items = ocr_screen(dest_png)
    print(f"Captured {screen_id} ({section_name}): {len(detections)} YOLO detections, {len(ocr_items)} OCR items")
    return ocr_items

# Hierarchy recording
hierarchy = {
    "title": "tvOS Settings Root",
    "children": []
}

# 1. Capture Root Settings
print("\n=== Capturing Settings Root ===")
navigate("up", 15) # Ensure top of list (General)
root_ocr = capture_and_qualify("settings_root", "Settings Main")
hierarchy["root_items"] = [item[0] for item in root_ocr if int(item[1]) > 950]

# List of 11 main sections
sections = [
    "General",
    "Profiles and Accounts",
    "Video and Audio",
    "Screen Saver",
    "Notifications",
    "AirPlay and Apple Home",
    "Remotes and Devices",
    "Accessibility",
    "Apps",
    "Network",
    "System"
]

for idx, sec in enumerate(sections):
    sec_id = sec.lower().replace(" ", "_").replace("&", "and")
    print(f"\n=== Navigating to Section {idx+1}/{len(sections)}: {sec} ===")
    navigate("up", 15)
    if idx > 0:
        navigate("down", idx)
    
    press("select")
    time.sleep(0.8)
    sec_ocr = capture_and_qualify(f"settings_{sec_id}", sec)
    sec_items = [item[0] for item in sec_ocr if int(item[1]) > 950 and item[0] not in (">", "<")]
    
    sec_node = {
        "name": sec,
        "id": f"settings_{sec_id}",
        "items": sec_items,
        "subsections": []
    }
    
    # Sub-screen exploration for key deep sections (General, Accessibility, Video and Audio, System)
    if sec in ["General", "Accessibility", "Video and Audio", "System"]:
        print(f"  Exploring subsections of {sec}...")
        navigate("up", 15)
        # Select first 3 candidate sub-items that have disclosure indicators
        sub_candidates = [it for it in sec_items if it not in (">", "<")][:3]
        for s_idx, sub_item in enumerate(sub_candidates):
            sub_id = sub_item.lower().replace(" ", "_").replace("&", "and").replace("/", "_")
            navigate("up", 15)
            if s_idx > 0:
                navigate("down", s_idx)
            press("select")
            time.sleep(0.8)
            sub_ocr = capture_and_qualify(f"settings_{sec_id}_{sub_id}", f"{sec} > {sub_item}")
            sub_list = [item[0] for item in sub_ocr if int(item[1]) > 950 and item[0] not in (">", "<")]
            sec_node["subsections"].append({
                "name": sub_item,
                "id": f"settings_{sec_id}_{sub_id}",
                "items": sub_list
            })
            press("back")
            time.sleep(0.5)
            wait_stable()

    hierarchy["children"].append(sec_node)
    
    # Return to Root Settings
    press("back")
    time.sleep(0.5)
    wait_stable()

with open("reports/tvos_settings_hierarchy.json", "w") as f:
    json.dump(hierarchy, f, indent=2)

print("\n=== Crawl Complete! Hierarchy saved to reports/tvos_settings_hierarchy.json ===")
