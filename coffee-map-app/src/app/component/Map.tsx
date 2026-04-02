
'use client';
import { MapContainer, TileLayer,Marker,Popup, Tooltip } from 'react-leaflet'
import { GeoJSON } from 'react-leaflet/GeoJSON'
import 'leaflet/dist/leaflet.css'
import 'leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css'
import "leaflet-defaulticon-compatibility";



const Map = (  {GeoJsonLayerData}  ) => {


  return (
    <MapContainer center={[9.1450, 40.4897]} zoom={14} scrollWheelZoom={false} style={{height: "100%", width: "100%"}}>
        <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; <a href=&quot;http://osm.org/copyright&quot;>OpenStreetMap</a> contributors"
        /> 

        {Object.keys(GeoJsonLayerData).map((country) => {
          console.log(GeoJsonLayerData[country])
          return <GeoJSON key={`${country}`} data={GeoJsonLayerData[country]} />
        })}
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