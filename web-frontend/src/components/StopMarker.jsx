import { Marker, Popup } from "react-leaflet";
import L from "leaflet";

const stopIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export default function StopMarker({ stop }) {
  return (
    <Marker
      position={[stop.stop_lat, stop.stop_lon]}
      icon={stopIcon}
    >
      <Popup>
        <strong>{stop.stop_name || "Unnamed Stop"}</strong>
        <br />
        ID: {stop.stop_id}
      </Popup>
    </Marker>
  );
}
