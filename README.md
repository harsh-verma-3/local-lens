📘 Local Lens — Offline OCR Tool

A fully offline, privacy-focused OCR tool using FastAPI + EasyOCR + React (Vite).
Supports screenshots, scanned documents, and images.
Extracts text locally, draws bounding boxes, lets you edit lines, copy text, and download .txt.

📁 Project Structure
local-lens/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── ocr/
│   │   │   ├── preprocess.py
│   │   │   └── easyocr_engine.py
│   ├── ... (env, requirements if needed)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── components/
│   │       ├── ImageUploader.jsx
│   │       ├── OCRPreview.jsx
│   │       └── PlainTextPanel.jsx
│   └── vite.config.js
│
├── data/
│   └── processed/
│       ├── preview_<timestamp>.png
│       ├── ocr_<timestamp>.json
│       └── ocr_<timestamp>.txt
│
└── README.md  ← (You are here)


Everything runs locally — no cloud uploads, no online APIs.

🖥️ Requirements
Backend

Python 3.11 (via Miniconda)

FastAPI

Uvicorn

EasyOCR

PyTorch (GPU optional, uses CPU fallback)

Frontend

Node.js 20.19+ (recommended via nvm-windows)

npm

Vite + React

🚀 Getting Started

🛠️ Backend Setup (FastAPI)
1. Activate Conda Environment
conda activate ocr-env


Ensure correct python:

python --version
# Python 3.11.x

2. Start the backend

From inside:

local-lens/backend/


Run:

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000


You should see:

Uvicorn running on http://127.0.0.1:8000

3. Test in Swagger UI

Open your browser:

👉 http://127.0.0.1:8000/docs

Try using:

POST /api/ocr

GET /api/download/{filename}

GET /api/export/txt/{ts}

🎨 Frontend Setup (React + Vite)

Inside:

local-lens/frontend/

1. Install dependencies
npm install

2. Start dev server
npm run dev


The frontend runs at:

👉 http://localhost:5173

The Vite proxy automatically forwards all /api/... calls to:

http://127.0.0.1:8000

🔍 How to Use Local Lens

Open the frontend:
http://localhost:5173

Click Choose File
Upload a screenshot/photo/document.

Backend processes image →

Crops/cleans image

Runs EasyOCR

Saves preview in /data/processed

Saves JSON in /data/processed

Frontend shows:

Image + bounding boxes

Extracted text

Buttons:
✔ Copy
✔ Download TXT
✔ Editable OCR boxes

Your entire workflow is offline.

💾 Saving of Results

All results are stored locally in:

data/processed/


Files created:

preview_<timestamp>.png – processed preview

ocr_<timestamp>.json – raw OCR + bounding boxes

ocr_<timestamp>.txt – extracted plain text

🧩 API Overview
POST /api/ocr

Uploads an image → returns:

{
  "preview_image": "preview_1764010336.png",
  "preview_path": ".../data/processed/preview_1764010336.png",
  "ocr": [...],
  "plain_text": "line1\nline2\nline3",
  "cleaned": null
}

GET /api/download/{filename}

Download preview PNG.

GET /api/export/txt/{ts}

Download .txt version of OCR text.

🐛 Troubleshooting
❗ “npm.ps1 cannot be loaded because running scripts is disabled”

Open PowerShell as admin:

Set-ExecutionPolicy RemoteSigned -Scope CurrentUser


OR use CMD instead of PowerShell.

❗ Vite crypto.hash error → Node is too old

You need Node 20.19 or higher:

nvm install 20.19.0
nvm use 20.19.0

❗ Preview image not found

Add absolute path in backend response:

"preview_path": preview_path


Or search in Windows:

dir /s /b preview_*.png

❗ GPU not used

Check PyTorch:

python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"

📦 Building for Production
Frontend
npm run build


Outputs:

frontend/dist/

Backend

Run uvicorn normally or package with PyInstaller (optional):

pyinstaller --onefile app/main.py

🎉 Future Enhancements

Add LLM cleanup via Ollama

Add searchable PDF export

Add multi-language OCR

Add desktop app mode (Tauri or Electron)
