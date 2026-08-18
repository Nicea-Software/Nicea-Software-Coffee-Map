import MapClientWrapper from "./component/MapClientWrapper";

import { GeoJSON } from 'react-leaflet/GeoJSON'

import path from 'path'
import fs from 'fs'
import fsPromises from 'fs/promises';



async function load_all_geojson_layers() {
  const geoJsonFiles = [];
  const read_path = path.join(process.cwd(), 'data/geo_json_info/');

  try {
    const country_directories = fs.readdirSync(read_path);

    for (const country_directory of country_directories) {
      const files_path = path.join(process.cwd(), 'data/geo_json_info/' , country_directory)
      // console.log(files_path)
      const files = fs.readdirSync(files_path)

      for (const file of files) {
        const geoJsonData = await fsPromises.readFile(files_path + '/' + file, 'utf-8');
        const geo_json_info = JSON.parse(geoJsonData);
        const region_name = file.split('.')[0].replace('_', ' ');
        geoJsonFiles.push({
            'country_name' : country_directory,
            'region_name' : region_name,
            'geo_json_info' : geo_json_info,
        });
      }
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