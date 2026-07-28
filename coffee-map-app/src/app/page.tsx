import MapClientWrapper from "./component/MapClientWrapper";

import { GeoJSON } from 'react-leaflet/GeoJSON'

import path from 'path'
import fs from 'fs'
import fsPromises from 'fs/promises';



async function load_all_geojson_layers() {
  const geoJsonFiles = [];
  const read_path = path.join(process.cwd(), 'data/geo_json_info/');

  try {
    const files = fs.readdirSync(read_path);
    for (const file of files) {
      const geoJsonData = await fsPromises.readFile(read_path + file, 'utf-8');
      const geo_json_info = JSON.parse(geoJsonData);
      const region_name = file.split('.')[0].replace('_', ' ');
      geoJsonFiles.push({
          'region_name' : region_name,
          'geo_json_info' : geo_json_info
      });
    }
  } catch (err) {
    console.error('Error reading directory:', err);
  }

  return geoJsonFiles;
}



export default async function Home() {
  var  geo_json_files  = await load_all_geojson_layers();

  // test = ""
  // console.log(Object.keys(geo_json_files))

  return (
    // give the main element a viewport height so the MapContainer (height: 100%) is visible
    <main style={{ height: "100vh" }}>
      <MapClientWrapper GeoJsonLayerData={geo_json_files} />
    </main>
  );
}