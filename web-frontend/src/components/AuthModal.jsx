import { useState } from "react";
import axios from "axios";
import API from '../api';

export default function AuthModal({ isOpen, onClose, setUser }) {
    const [tab, setTab] = useState("signin");
    const [form, setForm] = useState({ username: "", email: "", password: "", cpassword: "" });
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    if (!isOpen) return null;

    const handleChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const isStrongPassword = (pwd) =>
        pwd.length >= 8 && /[A-Z]/.test(pwd) && /[a-z]/.test(pwd) && /[0-9]/.test(pwd);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            if (tab === "signin") {
                const res = await API.post("dj-rest-auth/login/", {
                    email: form.email,
                    password: form.password,
                });
                setUser(res.data.user);
                localStorage.setItem("accessToken", res.data.access);
                localStorage.setItem("refreshToken", res.data.refresh);
                localStorage.setItem("user", JSON.stringify(res.data.user));
                onClose();
            } else {
                if (!isStrongPassword(form.password)) {
                    setError("Password must be at least 8 characters and contain uppercase, lowercase, and number.");
                    setLoading(false);
                    return;
                }
                if (form.password !== form.cpassword) {
                    setError("Passwords do not match.");
                    setLoading(false);
                    return;
                }

                const res = await API.post("dj-rest-auth/registration/", {
                    username: form.username,
                    email: form.email,
                    password1: form.password,
                    password2: form.cpassword,
                });
                setUser(res.data.user);
                localStorage.setItem("accessToken", res.data.access);
                localStorage.setItem("refreshToken", res.data.refresh);
                localStorage.setItem("user", JSON.stringify(res.data.user));
                onClose();
            }
        } catch (err) {
            //   setError(err.response?.data?.detail || "Something went wrong.");
            const data = err.response?.data;
            console.log(err.response?.data);
            if (data) {
                if (data.email) setError(`Email: ${data.email.join(" ")}`);
                else if (data.password1) setError(`Password: ${data.password1.join(" ")}`);
                else if (data.non_field_errors) setError(data.non_field_errors.join(" "));
                else if (data.detail) setError(data.detail);
                else setError("An unexpected error occurred.");
            } else {
                setError("Network error. Please try again.");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
            <div className="bg-white w-full max-w-md rounded-lg shadow-lg overflow-hidden">
                <div className="flex justify-between items-center px-6 py-4 border-b">
                    <h2 className="text-xl font-semibold text-gray-800">
                        {tab === "signin" ? "Sign In" : "Sign Up"}
                    </h2>
                    <button onClick={onClose} className="text-gray-500 hover:text-black">✕</button>
                </div>

                <div className="flex border-b">
                    {["signin", "signup"].map((t) => (
                        <button
                            key={t}
                            onClick={() => { setTab(t); setError(""); }}
                            className={`flex-1 py-2 text-sm font-medium ${tab === t ? "text-blue-600 border-b-2 border-blue-600" : "text-gray-500"}`}
                        >
                            {t === "signin" ? "Sign In" : "Register"}
                        </button>
                    ))}
                </div>

                <div className="p-6">
                    {error && <p className="text-red-500 text-sm mb-3">{error}</p>}
                    <form className="space-y-4" onSubmit={handleSubmit}>
                        {tab === "signup" && (
                            <input type="text" name="username" placeholder="Username" value={form.username} onChange={handleChange} className="w-full p-2 border rounded text-black" />
                        )}
                        <input type="email" name="email" placeholder="Email" value={form.email} onChange={handleChange} className="w-full p-2 border rounded text-black" />
                        <input type="password" name="password" placeholder="Password" value={form.password} onChange={handleChange} className="w-full p-2 border rounded text-black" />
                        {tab === "signup" && (
                            <input type="password" name="cpassword" placeholder="Confirm Password" value={form.cpassword} onChange={handleChange} className="w-full p-2 border rounded text-black" />
                        )}
                        <button type="submit" disabled={loading} className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700">
                            {loading ? "Processing..." : tab === "signin" ? "Sign In" : "Sign Up"}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}
