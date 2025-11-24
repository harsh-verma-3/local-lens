import React from "react";

export default function PlainTextPanel({ data }) {
  const { plain_text, preview_image } = data;

  async function copyAll() {
    if (!plain_text) return;
    await navigator.clipboard.writeText(plain_text);
    alert("Copied to clipboard");
  }

  function downloadTxt() {
    const tsMatch = preview_image && preview_image.match(/preview_(\d+)\.png/);
    const ts = tsMatch ? tsMatch[1] : null;
    if (!ts) {
      // fallback: download from client
      const blob = new Blob([plain_text || ""], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = "ocr_text.txt";
      document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
      return;
    }
    // call backend endpoint that streams the txt
    window.open(`/api/export/txt/${ts}`, "_blank");
  }

  return (
    <div style={{ marginTop: 12 }}>
      <h3>Extracted text</h3>
      <textarea readOnly value={plain_text || ""} rows={8} style={{ width: "100%" }} />
      <div style={{ marginTop: 8 }}>
        <button onClick={copyAll}>Copy</button>
        <button onClick={downloadTxt} style={{ marginLeft: 8 }}>Download TXT</button>
      </div>
    </div>
  );
}
