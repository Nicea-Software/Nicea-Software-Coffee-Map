import { GeoJSON } from 'react-leaflet/GeoJSON'

import fs from 'fs'

type GeoJsonFileOutputType = {
  html: string,
  region_name : string
}


function load_all_geojson_layers(){
  const directoryPath = '../../../data/geo_json_info/'
  const geoJsonFiles : GeoJsonFileOutputType[] = [];
  // console.log(path.join(process.cwd(), directoryPath))
  try {
    const countries : string[] = fs.readdirSync(directoryPath)
    countries.forEach(country   => {
      const regionFiles : string[] = fs.readdirSync(directoryPath + '/' + country)
      regionFiles.forEach(regionFile => {
          const geo_json_info = import (`../../../data/geo_json_info/${regionFile}`)
          const region_name = regionFile.split('.')[0];
          
          geoJsonFiles.push(
              {
                'html' : `<GeoJSON key="${country}" data="${geo_json_info}" />`,
                'region_name' : region_name
              }
          )
      })
      
      
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

