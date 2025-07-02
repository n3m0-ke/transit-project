import { useAuth } from "../context/AuthContext";

export default function Navbar({setShowModal, setAuthTab, setActivePanel }) {
  const {isAuthenticated, logout} = useAuth()
  return (
    <div className="absolute top-0 left-0 right-0 z-20 p-4 flex justify-between items-center bg-white shadow-sm">
      <div className="text-xl font-bold text-gray-800 cursor-pointer" onClick={() => setActivePanel(null)}>
        GTFS Explorer
      </div>
      <div className="space-x-4">
        {isAuthenticated ? (
          <button onClick={() => {
            logout();
            setActivePanel(null);
          }}>
            Log Out
          </button>
        ) : (
          <>
            <button onClick={() => { setShowModal(true); setAuthTab("signin"); }} className="text-black font-medium hover:underline">
              Sign In
            </button>
            <button onClick={() => { setShowModal(true); setAuthTab("signup"); }} className="text-black font-medium hover:underline">
              Sign Up
            </button>
          </>
        )}
      </div>
    </div>
  );
}
