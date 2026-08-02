import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAttendanceStats, getUsers, healthCheck } from "../api/client";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [usersTotal, setUsersTotal] = useState(0);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    getAttendanceStats()
      .then((r) => setStats(r.data))
      .catch(() => setStats(null));
    getUsers(1, 1)
      .then((r) => setUsersTotal(r.data.total))
      .catch(() => setUsersTotal(0));
    healthCheck()
      .then((r) => setHealth(r.data))
      .catch(() => setHealth(null));
  }, []);

  return (
    <section className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">Overview</p>
          <h1>Dashboard</h1>
          <p className="lede">Register faces, search, and mark attendance as present.</p>
        </div>
        <div className="actions">
          <Link className="btn primary" to="/search">
            Open Search / Attend
          </Link>
          <Link className="btn" to="/register">
            Register User
          </Link>
        </div>
      </header>

      <div className="stat-grid">
        <article>
          <p className="muted">Registered users</p>
          <h2>{usersTotal}</h2>
        </article>
        <article>
          <p className="muted">Present today</p>
          <h2>{stats?.present ?? "—"}</h2>
        </article>
        <article>
          <p className="muted">Face model</p>
          <h2>{health?.face_model_ready ? "Ready" : "Loading / Offline"}</h2>
        </article>
        <article>
          <p className="muted">API / DB</p>
          <h2>{health?.status ?? "—"}</h2>
        </article>
      </div>

      <div className="flow-note">
        <h3>Attendance flow</h3>
        <ol>
          <li>Capture face on Search page</li>
          <li>API generates embedding & searches pgvector</li>
          <li>If match found → attendance marked Present for today</li>
        </ol>
      </div>
    </section>
  );
}
