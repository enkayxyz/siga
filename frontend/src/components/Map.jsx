import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icon
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

const Map = ({ data }) => {
    const center = data?.hq_location?.coordinates || [20, 0]; // Default to world view
    const zoom = 2;

    return (
        <div className="h-full w-full rounded-xl overflow-hidden border border-white/10 shadow-lg">
            <MapContainer center={center} zoom={zoom} scrollWheelZoom={true} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />
                {data?.hq_location?.coordinates && (
                    <Marker position={data.hq_location.coordinates}>
                        <Popup>
                            <div className="text-black">
                                <strong>{data.name} (HQ)</strong><br />
                                {data.hq_location.city}, {data.hq_location.country}
                            </div>
                        </Popup>
                    </Marker>
                )}
                {data?.subsidiaries?.map((sub, idx) => (
                    sub.location?.coordinates && (
                        <Marker key={idx} position={sub.location.coordinates}>
                            <Popup>
                                <div className="text-black">
                                    <strong>{sub.name}</strong><br />
                                    {sub.location.city}, {sub.location.country}<br />
                                    Type: {sub.type}
                                </div>
                            </Popup>
                        </Marker>
                    )
                ))}
            </MapContainer>
        </div>
    );
};

export default Map;
