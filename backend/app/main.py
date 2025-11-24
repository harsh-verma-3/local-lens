# backend/app/main.py

import os
import time
import json
from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.ocr import preprocess, easyocr_engine

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data", "processed")
DATA_DIR = os.path.abspath(DATA_DIR)
os.makedirs(DATA_DIR, exist_ok=True)

app = FastAPI(title="Local Lens - OCR Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Helper to convert numpy objects into JSON-safe Python types
# -------------------------------------------------------------------
def sanitize_for_json(obj):
    """
    Recursively convert numpy types (np.int32, np.bool_, np.float32, ndarray)
    into Python-native types so json.dump works without errors.
    """
    import numpy as _np

    # dictionaries
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}

    # lists / tuples
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]

    # NumPy scalar types
    if isinstance(obj, _np.integer):
        return int(obj)
    if isinstance(obj, _np.floating):
        return float(obj)
    if isinstance(obj, _np.bool_):
        return bool(obj)

    # NumPy arrays → lists
    if isinstance(obj, _np.ndarray):
        return sanitize_for_json(obj.tolist())

    # Already JSON-safe (str, int, float, bool, None)
    return obj


# -------------------------------------------------------------------
# OCR API Endpoint
# -------------------------------------------------------------------
@app.post("/api/ocr")
async def api_ocr(
    file: UploadFile = File(...),
    use_llm: bool = Query(False),
    for_screenshot: bool = Query(True)
):
    # Read bytes
    contents = await file.read()

    # Preprocessing (OpenCV)
    pre = preprocess.preprocess_image_bytes(contents, for_screenshot=for_screenshot)

    # Save preview
    ts = int(time.time())
    preview_fname = f"preview_{ts}.png"
    preview_path = os.path.join(DATA_DIR, preview_fname)

    import cv2
    cv2.imwrite(preview_path, pre)

    # Run OCR
    ocr_results = easyocr_engine.ocr_image_numpy(pre, lang_list=['en'], gpu=True)

    # Prepare plain text (join recognized lines)
    plain_lines = [str(r.get("text", "")).strip() for r in ocr_results if str(r.get("text", "")).strip() != ""]
    plain_text = "\n".join(plain_lines)

    response_obj = {
        "preview_image": preview_fname,
        "preview_path": preview_path,
        "ocr": ocr_results,
        "plain_text": plain_text,
        "cleaned": None  # LLM support added later
    }

    # 🔥 Convert everything to JSON-safe types
    sanitized = sanitize_for_json(response_obj)

    # Save JSON result to disk
    out_json_path = os.path.join(DATA_DIR, f"ocr_{ts}.json")
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(sanitized, f, ensure_ascii=False, indent=2)

    # Return JSON response
    return JSONResponse(content=sanitized)


# -------------------------------------------------------------------
# File Download API (preview image)
# -------------------------------------------------------------------
@app.get("/api/download/{fname}")
async def download_file(fname: str):
    path = os.path.join(DATA_DIR, fname)
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse(status_code=404, content={"error": "File not found"})


# -------------------------------------------------------------------
# Export plain text as .txt (by timestamp)
# -------------------------------------------------------------------
@app.get("/api/export/txt/{ts}")
async def export_txt(ts: int):
    # load saved JSON created earlier
    json_path = os.path.join(DATA_DIR, f"ocr_{ts}.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            text = data.get("plain_text") or "\n".join([r.get("text", "") for r in data.get("ocr", [])])
    else:
        return JSONResponse(status_code=404, content={"error": "not found"})

    # write a txt file next to JSON
    txt_name = f"ocr_{ts}.txt"
    txt_path = os.path.join(DATA_DIR, txt_name)
    with open(txt_path, "w", encoding="utf-8") as tf:
        tf.write(text)

    return FileResponse(txt_path, media_type="text/plain", filename=txt_name)
