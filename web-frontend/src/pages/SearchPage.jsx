import { MapContainer, TileLayer } from "react-leaflet";
import Papa from "papaparse";
import { useEffect, useState } from "react";
import "leaflet/dist/leaflet.css";
import { Home, Route, Bookmark, Menu } from "lucide-react";

const MAP_CENTER = [-1.286389, 36.817223];
const MAP_ZOOM = 12;

export default function SearchRoutes() {
  const [stops, setStops] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [activePanel, setActivePanel] = useState(null);

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

  const icons = {
    home: <Home size={20} />,
    routes: <Route size={20} />,
    saved: <Bookmark size={20} />,
  };

  return (
    <div className="relative h-screen">
      {/* Top Navbar */}
      <div className="absolute top-0 left-0 right-0 z-20 p-4 flex justify-between items-center bg-white/80 backdrop-blur-sm shadow-sm">
        <div className="text-xl font-bold text-gray-800">GTFS Explorer</div>
        <div className="space-x-4">
          <button className="text-blue-600 font-semibold hover:underline">Sign In</button>
          <button className="text-blue-600 font-semibold hover:underline">Sign Up</button>
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
          <div className="absolute top-16 left-16 z-10 w-80 bg-white h-[calc(100%-8rem)] shadow-lg border-r border-gray-200 animate-slideIn">
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
          >
            <TileLayer
              attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
          </MapContainer>
        </div>
      </div>
    </div>
  );
}
