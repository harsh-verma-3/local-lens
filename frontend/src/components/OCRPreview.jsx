import React, { useEffect, useRef, useState } from "react";

export default function OCRPreview({ data }) {
  const { preview_image, ocr } = data;
  const canvasRef = useRef();
  const imgRef = useRef();
  const [selected, setSelected] = useState(null);
  const [lines, setLines] = useState([]);

  useEffect(() => {
    setLines(ocr.map((r, i) => ({ ...r, id: i })));
    const img = new Image();
    imgRef.current = img;
    img.src = `/api/download/${preview_image}`; // proxy to backend
    img.onload = () => draw(img, ocr);
    img.onerror = (e) => console.error("Image load error", e);
    return () => { imgRef.current = null; };
  }, [data]);

  function draw(img, boxes) {
    const canvas = canvasRef.current;
    canvas.width = img.width;
    canvas.height = img.height;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img, 0, 0);

    ctx.font = "12px sans-serif";
    boxes.forEach((b, idx) => {
      ctx.strokeStyle = b.low_confidence ? "orange" : "lime";
      ctx.lineWidth = 2;
      ctx.beginPath();
      const pts = b.bbox;
      ctx.moveTo(pts[0][0], pts[0][1]);
      for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
      ctx.closePath();
      ctx.stroke();

      // label
      const x = pts[0][0], y = Math.max(pts[0][1] - 14, 10);
      const text = b.text || "";
      const w = Math.min(300, ctx.measureText(text).width + 8);
      ctx.fillStyle = "rgba(0,0,0,0.6)";
      ctx.fillRect(x, y - 12, w, 14);
      ctx.fillStyle = "white";
      ctx.fillText(text.slice(0, 60), x + 2, y - 2);
    });
  }

  function onCanvasClick(e) {
    const canvas = canvasRef.current;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * scaleY;

    for (const l of lines) {
      if (pointInPoly([x, y], l.bbox)) {
        setSelected({ ...l });
        return;
      }
    }
    setSelected(null);
  }

  function pointInPoly(pt, poly) {
    let x = pt[0], y = pt[1], inside = false;
    for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
      const xi = poly[i][0], yi = poly[i][1];
      const xj = poly[j][0], yj = poly[j][1];
      const intersect = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
      if (intersect) inside = !inside;
    }
    return inside;
  }

  function saveEdit() {
    setLines(lines.map(l => l.id === selected.id ? selected : l));
    setSelected(null);
    if (imgRef.current) draw(imgRef.current, lines.map(l => l.id === selected?.id ? selected : l));
  }

  return (
    <div>
      <div style={{ maxWidth: "100%", overflow: "auto" }}>
        <canvas ref={canvasRef} style={{ maxWidth: "100%" }} onClick={onCanvasClick} />
      </div>

      {selected && (
        <div style={{ marginTop: 8 }}>
          <h4>Edit</h4>
          <textarea value={selected.text} onChange={e => setSelected({ ...selected, text: e.target.value })} rows={3} cols={60} />
          <div style={{ marginTop: 8 }}>
            <button onClick={saveEdit}>Save</button>
            <button onClick={() => setSelected(null)} style={{ marginLeft: 8 }}>Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
}
