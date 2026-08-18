
COUNTRY_DIRECTORIES=$( ls -dh -1 geo_json_info/*/)

rm -rf coffee-map-app/src/data/geo_json_info/*.json


OUTPUT_DIRECTORY="coffee-map-app/data/"

rm -rf $OUTPUT_DIRECTORY
mkdir -p $OUTPUT_DIRECTORY

while IFS= read -r country_directory; do
    
    COUNTRY_OUTPUT_DIRECTORY=$OUTPUT_DIRECTORY/$country_directory/

    mkdir -p $COUNTRY_OUTPUT_DIRECTORY

    REGION_FILES=$(ls -1 $country_directory)
    
    while IFS= read -r region_file; do
        region_file_json=$(echo $region_file | sed 's/geojson/json/g')

        crs_name=$(cat $country_directory$region_file  | jq .crs.properties.name | sed 's/\"//g')

        echo "CRS Name: $crs_name"
        echo $region_file_json

        # echo $country_directory$region_file
        if [[ $crs_name == *"EPSG::3857"* ]]; then
            # echo "
            ogr2ogr -f "GeoJSON" $COUNTRY_OUTPUT_DIRECTORY$region_file_json $country_directory/$region_file -s_srs "urn:ogc:def:crs:EPSG::3857" -t_srs "urn:ogc:def:crs:OGC:1.3:CRS84" -lco WRITE_NAME=NO   -lco RFC7946=NO
        else
            cp -r "$country_directory/$region_file" $COUNTRY_OUTPUT_DIRECTORY/$region_file_json
        fi
    done <<< "$REGION_FILES"
done <<< "$COUNTRY_DIRECTORIES"