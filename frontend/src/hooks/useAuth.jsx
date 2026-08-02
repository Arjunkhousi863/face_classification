import { createContext, useContext, useMemo, useState } from "react";
import { login as apiLogin } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => {
    const raw = localStorage.getItem("auth");
    return raw ? JSON.parse(raw) : null;
  });

  const value = useMemo(
    () => ({
      auth,
      async login(username, password) {
        const { data } = await apiLogin(username, password);
        const next = {
          token: data.access_token,
          role: data.role,
          name: data.name,
          username: data.username,
        };
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("auth", JSON.stringify(next));
        setAuth(next);
        return next;
      },
      logout() {
        localStorage.removeItem("token");
        localStorage.removeItem("auth");
        setAuth(null);
      },
    }),
    [auth]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
