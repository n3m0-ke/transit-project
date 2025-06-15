import { MapContainer, TileLayer } from "react-leaflet";
import Papa from "papaparse";
import { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";

const MAP_CENTER = [-1.286389, 36.817223];
const MAP_ZOOM = 12;

export default function SearchRoutes() {
  const [stops, setStops] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [activePanel, setActivePanel] = useState("home");

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

  const panels = {
    home: <div className="p-4">Welcome to the GTFS Planner</div>,
    routes: <div className="p-4">List of available routes here</div>,
    saved: <div className="p-4">Your saved stops & locations</div>,
  };

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <div
        className={`transition-all duration-300 ${
          isOpen ? "w-64" : "w-16"
        } bg-gray-800 text-white shadow-lg`}
      >
        <div className="flex flex-col h-full">
          <button
            className="p-4 hover:bg-gray-700"
            onClick={() => setIsOpen(!isOpen)}
          >
            ☰
          </button>

          <nav className="flex flex-col space-y-2 mt-2">
            {["home", "routes", "saved"].map((panel) => (
              <button
                key={panel}
                onClick={() => setActivePanel(panel)}
                className={`$${
                  activePanel === panel ? "bg-gray-700" : "hover:bg-gray-600"
                } p-2 text-left`}
              >
                {isOpen
                  ? panel.charAt(0).toUpperCase() + panel.slice(1)
                  : panel[0].toUpperCase()}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 relative">
        {panels[activePanel]}
        <MapContainer
          center={MAP_CENTER}
          zoom={MAP_ZOOM}
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer
            attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
        </MapContainer>
      </div>
    </div>
  );
}
