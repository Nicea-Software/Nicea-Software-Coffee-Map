import { GeoJSON } from 'react-leaflet/GeoJSON'

import fs from 'fs'



function load_all_geojson_layers(){
  const directoryPath = '../../../data/geo_json_info/'
  const geoJsonFiles = [];
  // console.log(path.join(process.cwd(), directoryPath))
  try {
    const files = fs.readdirSync(directoryPath)
    files.forEach(file => {
      let geo_json_info = import (`../../../data/geo_json_info/${file}`)
      let region_name = file.split('.')[0];
      geoJsonFiles.push(
          {
            'html' : `<GeoJSON key="${country_name}" data={geo_json_info} />`,
            'region_name' : region_name,
          }
      )
    })    
    
  } catch (err) {
    console.error('Error reading directory:', err)
  }

  return geoJsonFiles;
}


const GeoData = () => {
  return (
    <div>
      {load_all_geojson_layers()}
    </div>
  )
}

