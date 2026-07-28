
'use client';
import { MapContainer, TileLayer,Popup, Tooltip, Marker } from 'react-leaflet'
import { GeoJSON } from 'react-leaflet/GeoJSON'
import 'leaflet/dist/leaflet.css'
import 'leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css'
import "leaflet-defaulticon-compatibility";

import Legend from "./Legend"
import OtherLinks from './OtherLinks'

// type CountryInformation = {
//     name: string,
//     coordinantes: Array<number>,
//     zoomLevel: number
//     color: string
// }





const Map = (  {GeoJsonLayerData}  ) => {
  
  const TempCountryList = [
    {
      "name": "Ethopia",
      "coordinates": [9.1450, 40.4897],
      "zoomLevel" :  7,
      "color" : "red"
    },
    {
      "name" : "Nepal",
      "coordinates" : [28.00, 84.00],
      "zoomLevel" : 7.5,
      "color" : "red"
    }
  ]
  
  return (
    <MapContainer center={[9.1450, 40.4897]} zoom={14} scrollWheelZoom={false} style={{height: "100%", width: "100%"}}>
        <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; <a href=&quot;http://osm.org/copyright&quot;>OpenStreetMap</a> contributors"
        /> 

        

        {GeoJsonLayerData.map((region) => {
         const onEachFeature = (feature, layer) => {
          // console.log(region)
           layer.bindTooltip(region.region_name)
         }
          return(
        
            // <Tooltip key={`${region.country_name}_tooltip`}>
            // </Tooltip>
            <GeoJSON  onEachFeature={onEachFeature} key={`${region.region_name}`} data={region.geo_json_info} />
          )
        })}
        <Marker 
            position={[40.8054,-74.0241]}
            draggable={true}
            animate={true}
         >
        </Marker>
        <Legend country_info_list={TempCountryList}></Legend>
        <OtherLinks></OtherLinks>

    </MapContainer>
  )
}

export default Map