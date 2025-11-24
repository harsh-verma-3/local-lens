import React, { useRef, useState } from "react";
import axios from "axios";

export default function ImageUploader({ onResult }) {
  const fileRef = useRef();
  const [loading, setLoading] = useState(false);

  async function handleFile(e) {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);

    try {
      const fd = new FormData();
      fd.append("file", file);
      // for now: no LLM, assume screenshot true
      const resp = await axios.post(`/api/ocr?use_llm=false&for_screenshot=true`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 120000
      });
      if (onResult) onResult(resp.data);
    } catch (err) {
      console.error(err);
      alert("Upload failed: " + (err?.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
      // reset input so same file can be reselected
      if (fileRef.current) fileRef.current.value = "";
    }
  }

  return (
    <div>
      <input ref={fileRef} type="file" accept="image/*" onChange={handleFile} />
      {loading && <div>Processing...</div>}
    </div>
  );
}
