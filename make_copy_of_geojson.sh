
COUNTRY_DIRECTORIES=$( ls -dh -1 geo_json_info/*/)

rm -rf coffee-map-app/src/data/geo_json_info/*.json


while IFS= read -r country_directory; do
    
    REGION_FILES=$(ls -1 $country_directory)
    
    while IFS= read -r region_file; do
        region_file_json=$(echo $region_file | sed 's/geojson/json/g')

        echo $region_file_json

        # echo $country_directory$region_file
        cp -r "$country_directory/$region_file" coffee-map-app/data/geo_json_info/$region_file_json
    done <<< "$REGION_FILES"
done <<< "$COUNTRY_DIRECTORIES"