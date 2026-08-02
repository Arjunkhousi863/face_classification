import { useEffect, useState } from "react";
import { getAttendance, getAttendanceStats } from "../api/client";

export default function Attendance() {
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [items, setItems] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getAttendance({ attendance_date: date, page: 1, limit: 50 })
      .then((r) => setItems(r.data.items))
      .catch((err) => setError(err.response?.data?.detail || "Failed to load"));
    getAttendanceStats(date)
      .then((r) => setStats(r.data))
      .catch(() => setStats(null));
  }, [date]);

  return (
    <section className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">Presence</p>
          <h1>Attendance</h1>
          <p className="lede">
            Present today: {stats?.present ?? 0} / {stats?.total_users ?? 0}
          </p>
        </div>
        <label>
          Date
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </label>
      </header>

      {error ? <p className="error">{error}</p> : null}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Photo</th>
              <th>Name</th>
              <th>User ID</th>
              <th>Status</th>
              <th>Similarity</th>
              <th>Marked via</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan={7}>No attendance for this date</td>
              </tr>
            ) : (
              items.map((row) => (
                <tr key={row.id}>
                  <td>
                    {row.photo_url ? <img src={row.photo_url} alt="" className="thumb" /> : "—"}
                  </td>
                  <td>{row.name}</td>
                  <td>{row.user_id}</td>
                  <td>
                    <span className="badge present">{row.status}</span>
                  </td>
                  <td>{row.similarity != null ? `${(row.similarity * 100).toFixed(1)}%` : "—"}</td>
                  <td>{row.marked_via}</td>
                  <td>{new Date(row.marked_at).toLocaleString()}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
