import { useEffect, useState, useRef } from "react";
import Papa from "papaparse";
import { MapContainer, TileLayer } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import MapPanel from "../components/MapPanel";
import StopMarker from "../components/StopMarker";
import AuthModal from "../components/AuthModal";
import { haversineDistance, NAIROBI_BOUNDS } from "../utils/haversine";
import { Home, Route, Bookmark } from "lucide-react";

const MAP_CENTER = [-1.286389, 36.817223];
const MAP_ZOOM = 12;

export default function SearchRoutes() {
  const [stops, setStops] = useState([]);
  const [allStops, setAllStops] = useState([]);
  const [authTab, setAuthTab] = useState("signin");
  const [showModal, setShowModal] = useState(false);
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [activePanel, setActivePanel] = useState(null);
  const [lat, setLat] = useState(null);
  const [lon, setLon] = useState(null);
  const [selectedCoords, setSelectedCoords] = useState(null);
  const [loadingLocation, setLoadingLocation] = useState(false);
  const [searching, setSearching] = useState(false);
  const mapRef = useRef(null);

  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) setUser(JSON.parse(savedUser));
    setIsAuthenticated(!!localStorage.getItem("accessToken"));
  }, []);

  useEffect(() => {
    Papa.parse("/static/gtfs/stops.txt", {
      header: true,
      download: true,
      skipEmptyLines: true,
      complete: (results) => {
        if (results.errors.length) {
          console.error("Failed to load stops:", results.errors);
          return;
        }

        const parsed = results.data
          .map((s) => {
            const lat = parseFloat(s.stop_lat);
            const lon = parseFloat(s.stop_lon);
            return lat && lon
              ? {
                  ...s,
                  stop_lat: lat,
                  stop_lon: lon,
                }
              : null;
          })
          .filter((s) => s !== null);

        setAllStops(parsed);
        setStops([]);
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
      setLat(lat);
      setLon(lng);
      setSelectedCoords({ lat, lon: lng });
    } else {
      alert("Please select a location within Nairobi.");
    }
  };

  const handleDetectLocation = () => {
    setLoadingLocation(true);
    setLat(null);
    setLon(null);

    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        setLat(coords.latitude);
        setLon(coords.longitude);
        setSelectedCoords({ lat: coords.latitude, lon: coords.longitude });
        setLoadingLocation(false);
      },
      () => {
        alert("Failed to detect location.");
        setLoadingLocation(false);
      }
    );
  };

  const handleSearchStops = () => {
    if (!lat || !lon) {
      alert("Please select a location first.");
      return;
    }

    setSearching(true);

    const radiusKm = 0.5;
    const nearby = allStops.filter((stop) => {
      const d = haversineDistance(lat, lon, stop.stop_lat, stop.stop_lon);
      return d <= radiusKm;
    });

    setTimeout(() => {
      if (nearby.length > 0) {
        setStops(nearby);

        if (mapRef.current) {
          mapRef.current.setView([lat, lon], 15);
        }
      } else {
        alert("No stops found nearby.");
        setStops([]);
      }
      setSearching(false);
    }, 300);
  };

  return (
    <div className="relative h-screen">
      <Navbar
        setShowModal={setShowModal}
        setAuthTab={setAuthTab}
        setActivePanel={setActivePanel}
      />

      <div className="flex h-full pt-16">
        <Sidebar
          icons={{ home: <Home size={20} />, routes: <Route size={20} />, saved: <Bookmark size={20} /> }}
          activePanel={activePanel}
          setActivePanel={setActivePanel}
          isOpen={isOpen}
          setIsOpen={setIsOpen}
        />

        {activePanel && (
          <MapPanel
            activePanel={activePanel}
            isAuthenticated={isAuthenticated}
            setShowModal={setShowModal}
            setAuthTab={setAuthTab}
            lat={lat}
            lon={lon}
            setLat={setLat}
            setLon={setLon}
            selectedCoords={selectedCoords}
            handleDetectLocation={handleDetectLocation}
            handleSearchStops={handleSearchStops}
            loadingLocation={loadingLocation}
            searching={searching}
            setActivePanel={setActivePanel}
            allStops={allStops}
          />
        )}

        <div className="flex-1 relative z-0">
          <MapContainer
            center={MAP_CENTER}
            zoom={MAP_ZOOM}
            style={{ height: "100%", width: "100%" }}
            whenCreated={(map) => {
              map.on("click", handleMapClick);
              mapRef.current = map;
            }}
          >
            <TileLayer
              attribution='&copy; <a href="https://osm.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {stops.map((stop, i) => (
              <StopMarker key={i} stop={stop} />
            ))}
          </MapContainer>
        </div>
      </div>

      <AuthModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        tab={authTab}
      />
    </div>
  );
}
