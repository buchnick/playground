import argparse
import csv
import json
import random

from geopy.geocoders import Nominatim


# Function to convert a CSV to JSON
def make_json():
    # create a dictionary
    data = {}

    # Open a csv reader called DictReader
    with open(csv_file_path, encoding='utf-8') as csvf:
        csv_reader = csv.DictReader(csvf)

        # Convert each row into a dictionary
        # and add it to data
        for row in csv_reader:
            # row without unique_key count as invalid
            if unique_key in row:
                # try to extract coordinates out of the location field value
                location_str = row.get(location_key)
                if location_str:
                    location = geolocator.geocode(location_str)
                    if location:
                        row['coordinate'] = f'{location.latitude}, {location.longitude}'

                # Open a json writer, and use the json.dumps()
                # function to dump data
                with open(f'output/{row[unique_key]}.json', 'w', encoding='utf-8') as jsonf:
                    jsonf.write(json.dumps(row, indent=4))


if __name__ == '__main__':
    # generate Nominatim geolocator client
    geolocator = Nominatim(user_agent=f'the_cool_guy{random.randint(20, 30)}')

    # get script arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv_file_path', required=True, help='the input file path')
    parser.add_argument('--unique_key', required=True, help='the row unique key. will be used to name the output file')
    parser.add_argument('--location_key', required=False, default='',
                        help='the location field on which coordinate calculation will be based on')

    args = parser.parse_args()
    csv_file_path = args.csv_file_path
    unique_key = args.unique_key
    location_key = args.location_key

    # Call the make_json function
    make_json()
