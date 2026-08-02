import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getUsers } from "../api/client";

export default function UsersList() {
  const [data, setData] = useState({ items: [], page: 1, pages: 1, total: 0 });
  const [page, setPage] = useState(1);
  const [error, setError] = useState("");

  useEffect(() => {
    getUsers(page, 12)
      .then((r) => setData(r.data))
      .catch((err) => setError(err.response?.data?.detail || "Failed to load users"));
  }, [page]);

  return (
    <section className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">Directory</p>
          <h1>Users</h1>
          <p className="lede">Total {data.total} registered faces.</p>
        </div>
      </header>
      {error ? <p className="error">{error}</p> : null}
      <div className="user-grid">
        {data.items.map((u) => (
          <Link key={u.user_id} to={`/users/${u.user_id}`} className="user-tile">
            {u.photo_url ? <img src={u.photo_url} alt={u.name} /> : <div className="ph" />}
            <div>
              <h3>{u.name}</h3>
              <p>{u.user_id}</p>
              <p className="muted">{u.occupation || u.role}</p>
            </div>
          </Link>
        ))}
      </div>
      <div className="pager">
        <button type="button" className="btn" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
          Prev
        </button>
        <span>
          Page {data.page} / {data.pages}
        </span>
        <button
          type="button"
          className="btn"
          disabled={page >= data.pages}
          onClick={() => setPage((p) => p + 1)}
        >
          Next
        </button>
      </div>
    </section>
  );
}
