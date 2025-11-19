
'use client';
import { MapContainer, TileLayer,Marker,Popup, Tooltip } from 'react-leaflet'
import { GeoJSON } from 'react-leaflet/GeoJSON'
import 'leaflet/dist/leaflet.css'
import 'leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css'
import "leaflet-defaulticon-compatibility";
import GirawaGeojsonLayer from  '../../../data/geo_json_info/ethopia/Girawa.json'


const Map = () => {
  
  return (
    <MapContainer center={[40.8054,-74.0241]} zoom={14} scrollWheelZoom={false} style={{height: "100%", width: "100%"}}>
        <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; <a href=&quot;http://osm.org/copyright&quot;>OpenStreetMap</a> contributors"
        /> 

        <GeoJSON key='GirawaGeojsonLayer' data={GirawaGeojsonLayer} />

        <Marker 
            position={[40.8054,-74.0241]}
            draggable={true}
            animate={true}
         >
        <Popup>
          Hey ! you found me
        </Popup>
      </Marker>
    </MapContainer>
  )
}

export default Map