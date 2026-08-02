import { useState } from "react";
import { registerUser } from "../api/client";

export default function Register() {
  const [form, setForm] = useState({
    name: "",
    phone: "",
    address: "",
    occupation: "",
    role: "viewer",
  });
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onChange = (e) => setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const onFile = (e) => {
    const file = e.target.files?.[0];
    setImage(file || null);
    setPreview(file ? URL.createObjectURL(file) : "");
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!image) {
      setError("Face image is required");
      return;
    }
    setLoading(true);
    setError("");
    setMsg("");
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => fd.append(k, v));
      fd.append("image", image);
      const { data } = await registerUser(fd);
      setMsg(`Registered successfully: ${data.user_id}`);
      setForm({ name: "", phone: "", address: "", occupation: "", role: "viewer" });
      setImage(null);
      setPreview("");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="page">
      <header className="page-head">
        <div>
          <p className="eyebrow">Enroll</p>
          <h1>Register User</h1>
          <p className="lede">Detect face → embedding → Cloudinary → PostgreSQL + pgvector.</p>
        </div>
      </header>

      <form className="form-grid" onSubmit={onSubmit}>
        <label>
          Name
          <input name="name" value={form.name} onChange={onChange} required />
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
          Face image
          <input type="file" accept="image/*" onChange={onFile} />
        </label>
        {preview ? <img src={preview} alt="preview" className="preview" /> : null}
        {error ? <p className="error full">{error}</p> : null}
        {msg ? <p className="success full">{msg}</p> : null}
        <button className="btn primary full" disabled={loading}>
          {loading ? "Registering..." : "Register"}
        </button>
      </form>
    </section>
  );
}
