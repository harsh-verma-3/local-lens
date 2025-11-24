# backend/app/ocr/easyocr_engine.py
import easyocr
import threading

_reader = None
_reader_lock = threading.Lock()

def get_reader(lang_list=['en'], gpu=True):
    global _reader
    with _reader_lock:
        if _reader is None:
            _reader = easyocr.Reader(lang_list, gpu=gpu)
        return _reader

def ocr_image_numpy(img_np, lang_list=['en'], gpu=True, min_conf=0.3):
    reader = get_reader(lang_list, gpu=gpu)
    results = reader.readtext(img_np)
    out = []
    for bbox, text, conf in results:
        out.append({'bbox': bbox, 'text': text, 'conf': float(conf), 'low_confidence': conf < min_conf})
    return out
