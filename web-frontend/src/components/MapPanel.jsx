import React from "react";
import { useAuth } from "../context/AuthContext"; // 🔁 Import auth context

export default function MapPanel({
  activePanel,
  setShowModal,
  setAuthTab,
  lat,
  lon,
  setLat,
  setLon,
  selectedCoords,
  handleDetectLocation,
  handleSearchStops,
  loadingLocation,
  searching,
  setActivePanel,
}) {
  const { isAuthenticated } = useAuth(); // 🔁 Use context instead of props

  const renderHomePanel = () => (
    <div className="p-4 space-y-4">
      <h2 className="text-xl font-bold text-gray-800">Find Nearest Stops</h2>
      <p className="text-sm text-gray-600">
        Select a location or let us detect yours.
      </p>

      <button
        disabled={loadingLocation}
        className={`w-full py-2 rounded transition text-white ${
          loadingLocation ? "bg-blue-400" : "bg-blue-600 hover:bg-blue-700"
        }`}
        onClick={handleDetectLocation}
      >
        {loadingLocation ? "Detecting..." : "Use My Location"}
      </button>

      <div className="relative">
        <button
          className="w-full bg-gray-200 py-2 rounded hover:bg-gray-300 transition"
          onClick={() => alert("Click on the map to pick a point")}
        >
          Click on Map to Select Location
        </button>
        {selectedCoords && (
          <p className="text-sm text-gray-600 mt-2">
            Selected: {selectedCoords.lat.toFixed(5)}, {selectedCoords.lon.toFixed(5)}
          </p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-2">
        <input
          type="text"
          placeholder="Latitude"
          className="p-2 border rounded text-black"
          value={lat || ""}
          onChange={(e) => setLat(parseFloat(e.target.value))}
        />
        <input
          type="text"
          placeholder="Longitude"
          className="p-2 border rounded text-black"
          value={lon || ""}
          onChange={(e) => setLon(parseFloat(e.target.value))}
        />
      </div>

      <button
        disabled={searching}
        className={`w-full py-2 rounded text-white transition ${
          searching ? "bg-green-400" : "bg-green-600 hover:bg-green-700"
        }`}
        onClick={handleSearchStops}
      >
        {searching ? "Searching..." : "Search Stops"}
      </button>
    </div>
  );

  const renderRoutesPanel = () =>
    isAuthenticated ? (
      <div className="p-4">List of available routes (to be implemented)</div>
    ) : (
      <div className="p-4 text-gray-600">
        <p>🚫 Please sign in to view route information.</p>
        <button
          className="text-blue-600 hover:underline mt-2"
          onClick={() => {
            setShowModal(true);
            setAuthTab("signin");
          }}
        >
          Sign In
        </button>
      </div>
    );

  const renderSavedPanel = () =>
    isAuthenticated ? (
      <div className="p-4">Your saved stops & locations</div>
    ) : (
      <div className="p-4 text-gray-600">
        <p>🔒 Sign in to view bookmarks.</p>
        <button
          className="text-blue-600 hover:underline mt-2"
          onClick={() => {
            setShowModal(true);
            setAuthTab("signin");
          }}
        >
          Sign In
        </button>
      </div>
    );

  const panelContent = {
    home: renderHomePanel(),
    routes: renderRoutesPanel(),
    saved: renderSavedPanel(),
  };

  return (
    <div
      className="absolute top-16 left-16 z-10 w-80 bg-white h-[calc(100%-8rem)] shadow-lg border-r border-gray-200 animate-slideIn"
      style={{ animation: "slideIn 300ms ease-out forwards" }}
    >
      <div className="flex justify-between items-center p-4 border-b border-gray-200">
        <h2 className="font-semibold capitalize text-gray-800">{activePanel}</h2>
        <button
          className="text-gray-600 hover:text-gray-900"
          onClick={() => setActivePanel(null)}
        >
          ✕
        </button>
      </div>
      <div className="overflow-auto h-full">{panelContent[activePanel]}</div>
    </div>
  );
}
