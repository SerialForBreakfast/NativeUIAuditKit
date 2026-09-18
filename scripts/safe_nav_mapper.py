import json, os, subprocess, time

AATV = "/Users/josephmccraw/Library/Developer/Xcode/DerivedData/TVTestRig-bfjtodidumtdyagsgxcmwrmheuxr/Build/Products/Debug/TVTestRig.app/Contents/Helpers/aatv"
DEVICE_ID = "8D80F616-6C12-49A6-9015-8F594EE5F24E"
SESSION_DIR = "/Users/josephmccraw/Library/Containers/com.showblender.TVTestRig/Data/.tvtr/Evidence/Sessions/5699c327-bad3-482c-9dbf-7f9ec8ade0a5/screens"
OUTPUT_DIR = "dataset/tvos_settings_safe"
OCR_BIN = "scripts/ocr_helper"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_cmd(args):
    res = subprocess.run(args, capture_output=True, text=True)
    return res.stdout

def press(btn):
    run_cmd([AATV, "remote", "press", btn, "--device-id", DEVICE_ID])
    time.sleep(0.35)

def navigate(btn, count):
    run_cmd([AATV, "remote", "navigate", btn, "--count", str(count), "--device-id", DEVICE_ID])
    time.sleep(0.35)

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

def capture_screen(node_id, title):
    wait_stable()
    src = get_latest_screen()
    dest = os.path.join(OUTPUT_DIR, f"{node_id}.png")
    subprocess.run(["cp", src, dest])
    ocr_items = ocr_screen(dest)
    return dest, ocr_items

# Get all 13 top-level items by scanning down
print("Mapping Root Settings items...")
navigate("up", 20)
_, top_ocr = capture_screen("root_top", "Settings Root Top")
navigate("down", 10)
_, bot_ocr = capture_screen("root_bottom", "Settings Root Bottom")
navigate("up", 20)

print("Root mapped.")

def extract_rows(ocr_items):
    rows = []
    for text, x_s, y_s in ocr_items:
        x, y = int(x_s), int(y_s)
        if x > 950 and y > 150:
            if text not in (">", "<", "passing downtown los angeles"):
                rows.append((text, y))
    rows.sort(key=lambda r: r[1])
    # Deduplicate within 20px
    dedup = []
    for r in rows:
        if not dedup or abs(r[1] - dedup[-1][1]) > 20:
            dedup.append(r)
    return [r[0] for r in dedup]

# 1. Root items:
# Index 0: General
# Index 1: Profiles and Accounts
# Index 2: Video and Audio
# Index 3: Screen Saver
# Index 4: Notifications
# Index 5: AirPlay and Apple Home
# Index 6: Remotes and Devices
# Index 7: Accessibility
# Index 8: Apps
# Index 9: Network
# Index 10: System
# Index 11: Developer

# Safe subviews that have sub-navigation (disclosure arrow) and are safe to click:
safe_subviews = {
    "General": [
        ("About", 0),
        ("Appearance", 1),
        ("Sleep After", 2),
        ("Restrictions", 3),
        ("Privacy & Security", 4),
        ("Legal & Regulatory", 5)
    ],
    "Video and Audio": [
        ("Resolution", 0),
        ("HDMI Output", 1),
        ("Match Content", 2),
        ("Audio Output", 4),
        ("Audio Format", 5)
    ],
    "Screen Saver": [
        ("Current Selection", 0),
        ("Start After", 1)
    ],
    "AirPlay and Apple Home": [
        ("Conference Room Display", 2),
        ("AirPlay Display Underscan", 3),
        ("Room", 5)
    ],
    "Remotes and Devices": [
        ("Touch Surface Tracking", 1),
        ("Bluetooth", 3),
        ("Remote App and Devices", 4)
    ],
    "Accessibility": [
        ("VoiceOver", 0),
        ("Zoom", 1),
        ("Hover Text", 2),
        ("Display", 3),
        ("Motion", 4),
        ("Audio Descriptions", 5)
    ],
    "Apps": [
        ("TV", 4),
        ("Music", 5),
        ("Computers", 6),
        ("Fitness", 7),
        ("Podcasts", 8),
        ("Photos", 9)
    ],
    "Network": [
        ("Status", 0)
    ],
    "System": [
        ("Software Updates", 2),
        ("What's New", 1)
    ]
}

tree = {
    "name": "⚙️ Apple TV Settings (tvOS 26.6 / 18.x)",
    "sections": []
}

root_indices = [
    ("General", 0),
    ("Profiles and Accounts", 1),
    ("Video and Audio", 2),
    ("Screen Saver", 3),
    ("Notifications", 4),
    ("AirPlay and Apple Home", 5),
    ("Remotes and Devices", 6),
    ("Accessibility", 7),
    ("Apps", 8),
    ("Network", 9),
    ("System", 10),
    ("Developer", 11)
]

for sec_name, sec_idx in root_indices:
    print(f"\nScanning Category: {sec_name} (idx {sec_idx})")
    navigate("up", 20)
    if sec_idx > 0:
        navigate("down", sec_idx)
    
    press("select")
    time.sleep(0.7)
    sec_slug = sec_name.lower().replace(" ", "_").replace("&", "and")
    _, sec_ocr = capture_screen(f"sec_{sec_slug}", sec_name)
    sec_rows = extract_rows(sec_ocr)
    
    sec_entry = {
        "name": sec_name,
        "items": sec_rows,
        "subviews": []
    }
    
    # Check if this category has safe subviews to navigate into
    if sec_name in safe_subviews:
        for sub_name, sub_idx in safe_subviews[sec_name]:
            print(f"   Navigating into Subview: {sub_name} (idx {sub_idx})")
            navigate("up", 20)
            if sub_idx > 0:
                navigate("down", sub_idx)
            press("select")
            time.sleep(0.6)
            sub_slug = sub_name.lower().replace(" ", "_").replace("&", "and")
            _, sub_ocr = capture_screen(f"sub_{sec_slug}_{sub_slug}", f"{sec_name} > {sub_name}")
            sub_rows = extract_rows(sub_ocr)
            sec_entry["subviews"].append({
                "name": sub_name,
                "items": sub_rows
            })
            # Safe return to category
            press("back")
            time.sleep(0.4)
            wait_stable()
            
    tree["sections"].append(sec_entry)
    
    # Return to Root
    press("back")
    time.sleep(0.4)
    wait_stable()

with open("reports/tvos_settings_complete_tree.json", "w") as f:
    json.dump(tree, f, indent=2)

print("\nSAFE TREE MAPPING COMPLETE! Saved to reports/tvos_settings_complete_tree.json")
