import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

const links = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/register", label: "Register" },
  { to: "/search", label: "Search / Attend" },
  { to: "/users", label: "Users" },
  { to: "/attendance", label: "Attendance" },
];

export default function Layout() {
  const { auth, logout } = useAuth();

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">FA</span>
          <div>
            <p className="brand-name">FaceAttend</p>
            <p className="brand-sub">Recognition + Presence</p>
          </div>
        </div>
        <nav>
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} end={l.end} className={({ isActive }) => (isActive ? "nav active" : "nav")}>
              {l.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-foot">
          <p>{auth?.name}</p>
          <p className="muted">{auth?.role}</p>
          <button type="button" className="btn ghost" onClick={logout}>
            Logout
          </button>
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
