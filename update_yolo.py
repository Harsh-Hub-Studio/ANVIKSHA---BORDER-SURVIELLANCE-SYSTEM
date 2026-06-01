import re
import os

with open('yolo.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add ultralytics import
code = code.replace('import os', 'import os\ntry:\n    from ultralytics import YOLO\nexcept ImportError:\n    YOLO = None\n')

# 2. Add weapon states
state_code = '''
_weapon_model  = None
weapon_loaded  = False
WEAPON_WEIGHTS = 'runs/detect/runs/detect/weapons3/weights/best.pt'
WEAPON_CLASSES = {
    0: {'color': (0, 0, 255), 'label': 'WEAPON-AUTO-RIFLE'},
    1: {'color': (0, 0, 255), 'label': 'WEAPON-BAZOOKA'},
    2: {'color': (0, 0, 255), 'label': 'WEAPON-GRENADE'},
    3: {'color': (0, 0, 255), 'label': 'WEAPON-HANDGUN'},
    4: {'color': (0, 0, 200), 'label': 'WEAPON-KNIFE'},
    5: {'color': (0, 0, 255), 'label': 'WEAPON-SMG'},
    6: {'color': (0, 0, 255), 'label': 'WEAPON-SHOTGUN'},
    7: {'color': (0, 0, 255), 'label': 'WEAPON-SNIPER'},
    8: {'color': (0, 0, 200), 'label': 'WEAPON-SWORD'},
}
'''
code = code.replace('yolo_loaded    = False', 'yolo_loaded    = False' + state_code)

# 3. Change SKIP_FRAMES to 5
code = code.replace('SKIP_FRAMES    = 0', 'SKIP_FRAMES    = 5')

# 4. Modify load_yolo to load weapons
load_yolo_original = '''    yolo_loaded = True
    print(f"[YOLO] Model loaded — {len(_classes)} classes, {len(_output_layers)} output layers.")
    return True'''

load_yolo_new = '''    yolo_loaded = True
    print(f"[YOLO] Model loaded — {len(_classes)} classes, {len(_output_layers)} output layers.")
    
    global _weapon_model, weapon_loaded
    if YOLO is not None and os.path.exists(WEAPON_WEIGHTS):
        print(f"[YOLO] Loading Weapon Model YOLOv8...")
        _weapon_model = YOLO(WEAPON_WEIGHTS)
        weapon_loaded = True
        print(f"[YOLO] Weapon Model loaded!")
    else:
        print(f"[YOLO] YOLOv8 Weapon model not found or ultralytics not installed.")
        
    return True'''
code = code.replace(load_yolo_original, load_yolo_new)

# 5. Modify detect_objects to redraw cache
detect_skip = '''    if _frame_counter % (SKIP_FRAMES + 1) != 0:
        # Reuse last detection result — redraw boxes on current frame
        _, last_labels = _last_result
        return frame, last_labels'''

detect_skip_new = '''    if _frame_counter % (SKIP_FRAMES + 1) != 0:
        boxes_to_draw, last_labels = _last_result
        for (x, y, bw, bh, color, tag) in boxes_to_draw:
            cv2.rectangle(frame, (x, y), (x + bw, y + bh), color, 2)
            (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
            cv2.rectangle(frame, (x, y - th - 10), (x + tw + 6, y), color, cv2.FILLED)
            cv2.putText(frame, tag, (x + 3, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        return frame, last_labels
        
    boxes_to_draw = []
'''
code = code.replace(detect_skip, detect_skip_new)
code = code.replace('_last_result   = (None, [])', '_last_result   = ([], [])')

# 6. Change saving logic in detect_objects for COCO
coco_draw_orig = '''        # ── STEP 5: DRAW BOUNDING BOX ────────────────────────
        cv2.rectangle(frame, (x, y), (x + bw, y + bh), color, 2)

        # Label background pill
        tag = f"{label_text} {conf:.0%}"
        (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        cv2.rectangle(frame, (x, y - th - 10), (x + tw + 6, y), color, cv2.FILLED)
        cv2.putText(frame, tag, (x + 3, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)'''

coco_draw_new = '''        tag = f"{label_text} {conf:.0%}"
        boxes_to_draw.append((x, y, bw, bh, color, tag))
        
        cv2.rectangle(frame, (x, y), (x + bw, y + bh), color, 2)
        (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        cv2.rectangle(frame, (x, y - th - 10), (x + tw + 6, y), color, cv2.FILLED)
        cv2.putText(frame, tag, (x + 3, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)'''
code = code.replace(coco_draw_orig, coco_draw_new)

# 7. Add YOLOv8 weapon detection
weapon_infer = '''
    # ── YOLOv8 WEAPON DETECTION ─────────────────────────────
    if weapon_loaded and _weapon_model is not None:
        results = _weapon_model(frame, verbose=False)
        for r in results:
            for box in r.boxes:
                if box.conf[0].item() < CONFIDENCE_THRESHOLD:
                    continue
                cls_id = int(box.cls[0].item())
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]
                conf = box.conf[0].item()
                
                info = WEAPON_CLASSES.get(cls_id, {'color': (0,0,255), 'label': f'WEAPON-{cls_id}'})
                label_text = info['label']
                color = info['color']
                detected_labels.append("weapon")
                
                bw, bh = x2 - x1, y2 - y1
                tag = f"{label_text} {conf:.0%}"
                boxes_to_draw.append((x1, y1, bw, bh, color, tag))
                
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                (tw, th), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
                cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 6, y1), color, cv2.FILLED)
                cv2.putText(frame, tag, (x1 + 3, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
                
    _last_result = (boxes_to_draw, detected_labels)
    return frame, detected_labels
'''
code = code.replace('    _last_result = (frame, detected_labels)\n    return frame, detected_labels', weapon_infer)

with open('yolo.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Updated yolo.py successfully.")
