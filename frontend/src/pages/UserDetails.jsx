import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { deleteUser, getUser, updateUser } from "../api/client";
import { useAuth } from "../hooks/useAuth";

export default function UserDetails() {
  const { id } = useParams();
  const { auth } = useAuth();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [form, setForm] = useState({});
  const [image, setImage] = useState(null);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getUser(id)
      .then((r) => {
        setUser(r.data);
        setForm({
          name: r.data.name || "",
          phone: r.data.phone || "",
          address: r.data.address || "",
          occupation: r.data.occupation || "",
          role: r.data.role || "viewer",
        });
      })
      .catch((err) => setError(err.response?.data?.detail || "Not found"));
  }, [id]);

  const onChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const onSave = async (e) => {
    e.preventDefault();
    setMsg("");
    setError("");
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => fd.append(k, v));
      if (image) fd.append("image", image);
      const { data } = await updateUser(id, fd);
      setUser(data);
      setMsg("Updated");
    } catch (err) {
      setError(err.response?.data?.detail || "Update failed");
    }
  };

  const onDelete = async () => {
    if (!window.confirm("Delete user, embedding, and Cloudinary image?")) return;
    try {
      await deleteUser(id);
      navigate("/users");
    } catch (err) {
      setError(err.response?.data?.detail || "Delete failed");
    }
  };

  if (!user && !error) return <p className="page">Loading...</p>;

  return (
    <section className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">Profile</p>
          <h1>{user?.name || id}</h1>
          <p className="lede">{user?.user_id}</p>
        </div>
        <Link className="btn" to="/users">
          Back
        </Link>
      </header>

      {user ? (
        <div className="split">
          <div>
            {user.photo_url ? <img src={user.photo_url} alt={user.name} className="preview large" /> : null}
          </div>
          <form className="form-grid" onSubmit={onSave}>
            <label>
              Name
              <input name="name" value={form.name} onChange={onChange} />
            </label>
            <label>
              Phone
              <input name="phone" value={form.phone} onChange={onChange} />
            </label>
            <label>
              Occupation
              <input name="occupation" value={form.occupation} onChange={onChange} />
            </label>
            <label>
              Role
              <select name="role" value={form.role} onChange={onChange}>
                <option value="viewer">Viewer</option>
                <option value="officer">Officer</option>
                <option value="admin">Admin</option>
              </select>
            </label>
            <label className="full">
              Address
              <textarea name="address" value={form.address} onChange={onChange} rows={3} />
            </label>
            <label className="full">
              Replace face image (regenerates embedding)
              <input type="file" accept="image/*" onChange={(e) => setImage(e.target.files?.[0] || null)} />
            </label>
            {msg ? <p className="success full">{msg}</p> : null}
            {error ? <p className="error full">{error}</p> : null}
            <button className="btn primary" type="submit">
              Save
            </button>
            {auth?.role === "admin" ? (
              <button className="btn danger" type="button" onClick={onDelete}>
                Delete
              </button>
            ) : null}
          </form>
        </div>
      ) : (
        <p className="error">{error}</p>
      )}
    </section>
  );
}
