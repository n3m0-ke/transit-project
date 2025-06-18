import { MapContainer, TileLayer } from "react-leaflet";
import Papa from "papaparse";
import { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";
import { Home, Route, Bookmark, Menu } from "lucide-react";
import AuthModal from "../components/AuthModal";

const MAP_CENTER = [-1.286389, 36.817223];
const MAP_ZOOM = 12;
const NAIROBI_BOUNDS = {
  minLat: -1.45, // Southern boundary
  maxLat: -1.15, // Northern boundary
  minLon: 36.65, // Western boundary
  maxLon: 37.05, // Eastern boundary
};

export default function SearchRoutes() {
  const [stops, setStops] = useState([]);
  const [authTab, setAuthTab] = useState("signin");
  const [isOpen, setIsOpen] = useState(false);
  const [activePanel, setActivePanel] = useState(null);

  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const [showModal, setShowModal] = useState(false);

  const [lat, setLat] = useState(null);
  const [lon, setLon] = useState(null);
  const [selectedCoords, setSelectedCoords] = useState(null);
  const [mapSelectionMode, setMapSelectionMode] = useState(false); // For map selection mode

  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    setIsAuthenticated(!!token);
  }, []);



  useEffect(() => {
    Papa.parse("/static/gtfs/stops.txt", {
      header: true,
      download: true,
      complete: (results) => {
        if (results.errors.length) {
          console.error("Failed to load stops:", results.errors);
          return;
        }
        const filtered = results.data.filter(
          (stop) => stop.stop_lat && stop.stop_lon
        );
        setStops(filtered);
      },
      error: (err) => console.error("Parsing error:", err),
    });
  }, []);

  const handleMapClick = (e) => {
    const { lat, lng } = e.latlng;

    if (
      lat >= NAIROBI_BOUNDS.minLat &&
      lat <= NAIROBI_BOUNDS.maxLat &&
      lng >= NAIROBI_BOUNDS.minLon &&
      lng <= NAIROBI_BOUNDS.maxLon
    ) {
      setSelectedCoords({ lat, lon: lng });
      setLat(lat);
      setLon(lng);
    } else {
      alert("Please select a location within Nairobi.");
    }
  };


  const handleDetectLocation = () => {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLat(pos.coords.latitude);
        setLon(pos.coords.longitude);
        setSelectedCoords({ lat: pos.coords.latitude, lon: pos.coords.longitude });
      },
      () => alert("Failed to detect location. Please enter manually.")
    );
  };

  const handleSearchStops = async () => {
    if (!lat || !lon) {
      alert("Please select a location first.");
      return;
    }

    try {
      const response = await fetch(
        `https://transit-project-backend.onrender.com/api/nearest_stops/?lat=${lat}&lon=${lon}&radius=0.3`
      );
      const data = await response.json();

      if (data.stops && data.stops.length > 0) {
        console.log("Nearby stops:", data.stops); // Replace with UI update logic
        setStops(data.stops); // Update UI with stops list
      } else {
        alert("No stops found nearby.");
      }
    } catch (err) {
      console.error("Error fetching stops:", err);
      alert("Failed to fetch nearby stops.");
    }
  };

  const panels = {
    home: <div className="p-4">
      <div className="p-4 space-y-4">
        <h2 className="text-xl font-bold text-gray-800">Find Nearest Stops</h2>
        <p className="text-sm text-gray-600">Select a location or let us detect yours.</p>

        {/* Auto-detect location */}
        <button
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 transition"
          onClick={handleDetectLocation}
        >
          Use My Location
        </button>

        {/* Click-on-map input */}
        <div className="relative">
          <button
            className="w-full bg-gray-200 py-2 rounded hover:bg-gray-300 transition"
            onClick={() => setMapSelectionMode(true)}
          >
            Click on Map to Select Location
          </button>
          {selectedCoords && (
            <p className="text-sm text-gray-600 mt-2">Selected: {selectedCoords.lat}, {selectedCoords.lon}</p>
          )}
        </div>

        {/* Manual input */}
        <div className="grid grid-cols-2 gap-2">
          <input
            type="text"
            placeholder="Latitude"
            className="p-2 border rounded text-black"
            value={lat}
            onChange={(e) => setLat(e.target.value)}
          />
          <input
            type="text"
            placeholder="Longitude"
            className="p-2 border rounded text-black"
            value={lon}
            onChange={(e) => setLon(e.target.value)}
          />
        </div>

        {/* Search Button */}
        <button
          className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 transition"
          onClick={handleSearchStops}
        >
          Search Stops
        </button>
      </div>
    </div>,
    routes: <div className="p-4">List of available routes here</div>,
    saved: <div className="p-4">Your saved stops & locations</div>,
  };

  const icons = {
    home: <Home size={20} />,
    routes: <Route size={20} />,
    saved: <Bookmark size={20} />,
  };

  return (
    <div className="relative h-screen">
      {/* Top Navbar */}
      <div className="absolute top-0 left-0 right-0 z-20 p-4 flex justify-between items-center bg-transparent shadow-sm">
        <div className="text-xl font-bold text-gray-800">GTFS Explorer</div>
        <div className="space-x-4">
          {isAuthenticated ? (
            <button
              onClick={() => {
                localStorage.clear();
                setUser(null);
                setIsAuthenticated(false);
                setActivePanel(null);
              }}
              className="text-red-600 font-semibold hover:underline"
            >
              Log Out
            </button>
          ) : (
            <>
              <button onClick={() => { setShowModal(true); setAuthTab("signin"); }} className="text-black font-medium hover:underline">Sign In</button>
              <button onClick={() => { setShowModal(true); setAuthTab("signup"); }} className="text-black font-medium hover:underline">Sign Up</button>
            </>
          )}
        </div>

      </div>

      <div className="flex h-full pt-16">
        {/* Sidebar */}
        <div className="w-16 bg-white text-gray-800 shadow-lg z-10">
          <div className="flex flex-col h-full items-center">
            <button
              className="p-4 hover:bg-gray-200"
              onClick={() => setIsOpen(!isOpen)}
            >
              <Menu size={20} />
            </button>

            <nav className="flex flex-col space-y-2 mt-2">
              {Object.keys(icons).map((panel) => (
                <button
                  key={panel}
                  onClick={() =>
                    setActivePanel((prev) => (prev === panel ? null : panel))
                  }
                  className={`$ {
                    activePanel === panel ? "bg-gray-200" : "hover:bg-gray-100"
                  } p-2 rounded flex items-center justify-center`}
                  title={panel.charAt(0).toUpperCase() + panel.slice(1)}
                >
                  {icons[panel]}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Sliding Panels */}
        {activePanel && (
          <div className="absolute top-16 left-16 z-10 w-80 bg-white h-[calc(100%-8rem)] shadow-lg border-r border-gray-200 animate-slideIn"
            style={{ animation: "slideIn 300ms ease-out forwards" }}>
            <div className="flex justify-between items-center p-4 border-b border-gray-200">
              <h2 className="font-semibold capitalize text-gray-800">
                {activePanel}
              </h2>
              <button
                className="text-gray-600 hover:text-gray-900"
                onClick={() => setActivePanel(null)}
              >
                ✕
              </button>
            </div>
            <div className="overflow-auto h-full">{panels[activePanel]}</div>
          </div>
        )}

        {/* Main Map */}
        <div className="flex-1 relative z-0">
          <MapContainer
            center={MAP_CENTER}
            zoom={MAP_ZOOM}
            style={{ height: "100%", width: "100%" }}
            onClick={handleMapClick}
          >
            <TileLayer
              attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
          </MapContainer>
        </div>
      </div>
      <AuthModal isOpen={showModal} onClose={() => setShowModal(false)} setUser={setUser} />
    </div>
  );
}
