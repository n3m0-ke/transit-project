import { useState, useEffect } from "react";
import AuthModal from "../components/AuthModal";
import { FaUserCircle } from "react-icons/fa";

export default function LandingPage() {
  const [showModal, setShowModal] = useState(false);
  const [authTab, setAuthTab] = useState("signin");
  const [user, setUser] = useState(null);
  const [dropdown, setDropdown] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    setUser(null);
    setDropdown(false);
    setMessage("You’ve been logged out.");
    setTimeout(() => setMessage(""), 3000);
  };

  return (
    <div className="relative h-screen bg-gradient-to-br from-blue-900 to-sky-400 text-white">
      {message && (
        <div className="absolute top-0 left-1/2 transform -translate-x-1/2 mt-2 px-4 py-2 bg-green-600 text-white rounded shadow-md z-50">
          {message}
        </div>
      )}
      <nav className="absolute top-0 left-0 w-full flex items-center justify-between px-8 py-4 bg-transparent z-10">
        <img src="/static/logo.png" alt="GTFS Explorer" className="h-10 w-auto" />
        {user ? (
          <div className="relative">
            <button onClick={() => setDropdown((prev) => !prev)} className="flex items-center space-x-2">
              <FaUserCircle className="text-2xl" />
              <span className="hidden md:inline">{user.email}</span>
            </button>
            {dropdown && (
              <div className="absolute right-0 mt-2 w-48 bg-white text-gray-800 rounded shadow-md z-50">
                <a href="/profile" className="block px-4 py-2 hover:bg-gray-100">Profile Settings</a>
                <button onClick={handleLogout} className="w-full text-left px-4 py-2 hover:bg-gray-100">Logout</button>
              </div>
            )}
          </div>
        ) : (
          <div className="flex space-x-4">
            <button onClick={() => { setShowModal(true); setAuthTab("signin"); }} className="text-white font-medium hover:underline">Sign In</button>
            <button onClick={() => { setShowModal(true); setAuthTab("signup"); }} className="text-white font-medium hover:underline">Sign Up</button>
          </div>
        )}
      </nav>

      <div className="flex items-center justify-center h-full">
        <div className="text-center px-6">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">Welcome to GTFS Explorer</h1>
          <p className="text-lg md:text-xl mb-6">Find routes, explore stops, and plan your trips seamlessly within Nairobi.</p>
          <div className="space-x-4">
            <a href="/search" className="bg-white text-blue-800 font-semibold px-5 py-2 rounded shadow hover:bg-gray-100 transition">
              Search Routes
            </a>
            <a href="/nearby" className="bg-white text-blue-800 font-semibold px-5 py-2 rounded shadow hover:bg-gray-100 transition">
              Nearby Stops
            </a>
          </div>
        </div>
      </div>

      <AuthModal isOpen={showModal} onClose={() => setShowModal(false)} setUser={setUser} />
    </div>
  );
}
