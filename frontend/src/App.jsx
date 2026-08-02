import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import { useAuth } from "./hooks/useAuth";
import Attendance from "./pages/Attendance";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Search from "./pages/Search";
import UserDetails from "./pages/UserDetails";
import UsersList from "./pages/UsersList";

function PrivateRoute({ children }) {
  const { auth } = useAuth();
  if (!auth) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="register" element={<Register />} />
        <Route path="search" element={<Search />} />
        <Route path="users" element={<UsersList />} />
        <Route path="users/:id" element={<UserDetails />} />
        <Route path="attendance" element={<Attendance />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
