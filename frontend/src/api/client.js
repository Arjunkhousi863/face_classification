import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "/api";

const client = axios.create({
  baseURL: API_BASE,
});

client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default client;

export const login = (username, password) =>
  client.post("/auth/login", { username, password });

export const registerUser = (formData) =>
  client.post("/users/register", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

export const searchFace = (formData) =>
  client.post("/users/search", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

export const getUsers = (page = 1, limit = 20) =>
  client.get("/users", { params: { page, limit } });

export const getUser = (id) => client.get(`/users/${id}`);

export const updateUser = (id, formData) =>
  client.put(`/users/${id}`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });

export const deleteUser = (id) => client.delete(`/users/${id}`);

export const getAttendance = (params = {}) =>
  client.get("/attendance", { params });

export const getAttendanceStats = (attendance_date) =>
  client.get("/attendance/stats", { params: { attendance_date } });

export const healthCheck = () => client.get("/health");
