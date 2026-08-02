import { useState } from "react";
import { Link } from "react-router-dom";
import { searchFace } from "../api/client";
import CameraCapture from "../components/CameraCapture";

export default function Search() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState("");
  const [markAttendance, setMarkAttendance] = useState(true);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const setBlob = (blob) => {
    setFile(blob);
    setPreview(URL.createObjectURL(blob));
    setResult(null);
  };

  const onFile = (e) => {
    const f = e.target.files?.[0];
    if (!f) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
  };

  const onSearch = async () => {
    if (!file) {
      setError("Capture or upload a face image first");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const fd = new FormData();
      fd.append("image", file, "capture.jpg");
      fd.append("mark_attendance", markAttendance ? "true" : "false");
      const { data } = await searchFace(fd);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Search failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">Identify</p>
          <h1>Search Face & Mark Attendance</h1>
          <p className="lede">
            On match, attendance is marked <strong>Present</strong> for today (toggle below).
          </p>
        </div>
      </header>

      <div className="split">
        <div>
          <CameraCapture onCapture={setBlob} />
          <label className="file-alt">
            Or upload image
            <input type="file" accept="image/*" onChange={onFile} />
          </label>
          <label className="check">
            <input
              type="checkbox"
              checked={markAttendance}
              onChange={(e) => setMarkAttendance(e.target.checked)}
            />
            Mark attendance as Present if face found
          </label>
          <button type="button" className="btn primary" onClick={onSearch} disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </button>
          {error ? <p className="error">{error}</p> : null}
        </div>

        <div className="result-panel">
          {preview ? <img src={preview} alt="query" className="preview" /> : <p className="muted">No capture yet</p>}
          {result ? (
            result.found ? (
              <div className="match">
                <p className="success">Match found</p>
                <p>Similarity: {(result.similarity * 100).toFixed(1)}%</p>
                {result.attendance_marked ? (
                  <p className="success">{result.attendance_message || "Attendance marked Present"}</p>
                ) : (
                  <p className="muted">Attendance not marked (toggle was off)</p>
                )}
                <div className="user-card-inline">
                  {result.user?.photo_url ? (
                    <img src={result.user.photo_url} alt={result.user.name} />
                  ) : null}
                  <div>
                    <h3>{result.user?.name}</h3>
                    <p>{result.user?.user_id}</p>
                    <p>{result.user?.phone}</p>
                    <p>{result.user?.occupation}</p>
                    <Link to={`/users/${result.user?.user_id}`}>View details</Link>
                  </div>
                </div>
              </div>
            ) : (
              <p className="error">{result.message || "Face not found"}</p>
            )
          ) : null}
        </div>
      </div>
    </section>
  );
}
