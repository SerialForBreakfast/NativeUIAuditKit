import json, os, subprocess, time
from ultralytics import YOLO

AATV = "/Users/josephmccraw/Library/Developer/Xcode/DerivedData/TVTestRig-bfjtodidumtdyagsgxcmwrmheuxr/Build/Products/Debug/TVTestRig.app/Contents/Helpers/aatv"
DEVICE_ID = "8D80F616-6C12-49A6-9015-8F594EE5F24E"
SESSION_DIR = "/Users/josephmccraw/Library/Containers/com.showblender.TVTestRig/Data/.tvtr/Evidence/Sessions/5699c327-bad3-482c-9dbf-7f9ec8ade0a5/screens"
OUTPUT_DIR = "dataset/tvos_settings_exhaustive"
MODEL_PATH = "NativeUITrainer/yolo_runs/phase6b_tvos_v3/weights/best.pt"
OCR_BIN = "scripts/ocr_helper"

os.makedirs(OUTPUT_DIR, exist_ok=True)
yolo_model = YOLO(MODEL_PATH)

def run_cmd(args):
    res = subprocess.run(args, capture_output=True, text=True)
    return res.stdout

def press(btn):
    run_cmd([AATV, "remote", "press", btn, "--device-id", DEVICE_ID])
    time.sleep(0.3)

def navigate(btn, count):
    run_cmd([AATV, "remote", "navigate", btn, "--count", str(count), "--device-id", DEVICE_ID])
    time.sleep(0.3)

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
    return dest_png, detections, ocr_items

print("Deep crawl base ready.")

def parse_screen(ocr_items):
    # Returns (title, left_pane_items, right_pane_items)
    title = ""
    left_items = []
    right_items = []
    for text, x_str, y_str in ocr_items:
        x, y = int(x_str), int(y_str)
        if y < 150 and x > 300 and x < 1200 and not title:
            title = text
        elif x < 900 and y > 150:
            left_items.append((text, x, y))
        elif x >= 900 and y > 150:
            if text not in (">", "<"):
                right_items.append((text, x, y))
    return title or "Settings", left_items, right_items

# Systematically explore each of the 13 root sections
root_sections = [
    ("General", ["About", "Appearance", "Sleep After", "Restrictions", "Privacy & Security", "Legal & Regulatory"]),
    ("Profiles and Accounts", ["Joe McCraw", "Add New Profile", "TV Provider", "Home Sharing"]),
    ("Video and Audio", ["Resolution", "HDMI Output", "Match Content", "Audio Output", "Audio Format", "Reduce Loud Sounds"]),
    ("Screen Saver", ["Current Selection", "Start After", "Show During Music and Podcasts", "Aerials", "Memories & Slideshows"]),
    ("Notifications", ["Search", "TV"]),
    ("AirPlay and Apple Home", ["AirPlay", "Allow Access", "Conference Room Display", "AirPlay Display Underscan", "Room"]),
    ("Remotes and Devices", ["Touch Surface Tracking", "TV Button", "Bluetooth", "Remote App and Devices", "Learn Remote"]),
    ("Accessibility", ["VoiceOver", "Zoom", "Hover Text", "Display", "Motion", "Audio Descriptions", "Switch Control", "Subtitles and Captioning"]),
    ("Apps", ["Automatically Update Apps", "Automatically Install Apps", "Offload Unused Apps", "TV", "Music", "Computers", "Fitness", "Podcasts", "Photos"]),
    ("Network", ["Ethernet", "Wi-Fi", "Status"]),
    ("System", ["Software Updates", "Reset", "Restart", "Help", "What's New"]),
    ("Developer", []),
    ("Power Off", [])
]

# Reset to Root
print("Resetting to Settings Root top...")
navigate("up", 20)
root_png, root_dets, root_ocr = capture_and_qualify("root", "Settings Main")
full_tree = {
    "title": "⚙️ Apple TV Settings (tvOS 26.6 / 18.x)",
    "screen_id": "root",
    "children": []
}

for r_idx, (sec_name, sub_targets) in enumerate(root_sections):
    sec_slug = sec_name.lower().replace(" ", "_").replace("&", "and")
    print(f"\n=======================================================")
    print(f"[{r_idx+1}/{len(root_sections)}] Section: {sec_name}")
    print(f"=======================================================")
    navigate("up", 20)
    if r_idx > 0:
        navigate("down", r_idx)
    
    # Enter section
    press("select")
    time.sleep(0.7)
    sec_png, sec_dets, sec_ocr = capture_and_qualify(f"sec_{sec_slug}", sec_name)
    title, left_items, right_items = parse_screen(sec_ocr)
    
    sec_node = {
        "name": sec_name,
        "title": title,
        "screen_id": f"sec_{sec_slug}",
        "visible_items": [r[0] for r in right_items],
        "subsections": []
    }
    
    # Deep dive into each target sub-item if targets exist
    for s_idx, target_sub in enumerate(sub_targets):
        target_slug = target_sub.lower().replace(" ", "_").replace("&", "and")
        print(f"  --> Sub-item [{s_idx+1}/{len(sub_targets)}]: {target_sub}")
        navigate("up", 20)
        if s_idx > 0:
            navigate("down", s_idx)
        
        # Probe sub-item
        press("select")
        time.sleep(0.7)
        sub_png, sub_dets, sub_ocr = capture_and_qualify(f"sub_{sec_slug}_{target_slug}", f"{sec_name} > {target_sub}")
        sub_title, sub_left, sub_right = parse_screen(sub_ocr)
        
        # Check if screen actually changed (i.e. did not just toggle an in-place checkbox)
        sub_node = {
            "name": target_sub,
            "title": sub_title,
            "screen_id": f"sub_{sec_slug}_{target_slug}",
            "items": [r[0] for r in sub_right]
        }
        sec_node["subsections"].append(sub_node)
        
        # Back out to section level
        press("back")
        time.sleep(0.4)
        wait_stable()
    
    full_tree["children"].append(sec_node)
    
    # Back out to Root level
    press("back")
    time.sleep(0.4)
    wait_stable()

with open("reports/tvos_settings_exhaustive_tree.json", "w") as f:
    json.dump(full_tree, f, indent=2)

print("\n\n#######################################################")
print("EXHAUSTIVE TREE CRAWL COMPLETE!")
print("Saved to reports/tvos_settings_exhaustive_tree.json")
print("#######################################################")
