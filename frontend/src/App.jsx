import React, { useState } from "react";
import ImageUploader from "./components/ImageUploader";
import OCRPreview from "./components/OCRPreview";
import PlainTextPanel from "./components/PlainTextPanel";

export default function App() {
  const [result, setResult] = useState(null);

  return (
    <div style={{ padding: 20 }}>
      <h1>Local Lens • OCR</h1>

      <ImageUploader onResult={setResult} />

      {result && (
        <div style={{ marginTop: 16 }}>
          <OCRPreview data={result} />
          <PlainTextPanel data={result} />
        </div>
      )}
    </div>
  );
}
