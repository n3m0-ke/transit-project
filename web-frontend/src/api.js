import axios from "axios";

const API = axios.create({
  baseURL: "https://transit-project-backend.onrender.com/api/",
  headers: {
    "Content-Type": "application/json",
  },
});

// Automatically attach token to requests if available
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("accessToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => Promise.reject(error));

export default API;