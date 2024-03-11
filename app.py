from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import itertools
import time

app = Flask(__name__)
CORS(app)

# Function to get the coordinates of a location
def get_location_coordinates(location_name):
    geolocator = Nominatim(user_agent="devops app")
    time.sleep(1)  # Introduce a delay
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None  # Return None if coordinates are not found

# API endpoint to get the coordinates of a selected place
@app.route('/get-coordinates', methods=['GET'])
def get_coordinates():
    place_name = request.args.get('place')
    if place_name:
        latitude, longitude = get_location_coordinates(place_name)
        if latitude is not None and longitude is not None:
            return jsonify({'latitude': latitude, 'longitude': longitude})
        else:
            return jsonify({'error': 'Coordinates not found for the specified place'}), 404
    else:
        return jsonify({'error': 'Please provide a place name in the "place" query parameter'}), 400

@app.route('/calculate-best-path', methods=['POST'])
def calculate_best_path():
    data = request.get_json()
    places_names = data['places']
    
    # Coordinates of the places
    places_coordinates = [get_location_coordinates(place) for place in places_names]
    
    # Distance matrix
    distances = np.zeros((len(places_coordinates), len(places_coordinates)))
    for i in range(len(places_coordinates)):
        for j in range(len(places_coordinates)):
            distances[i, j] = geodesic(places_coordinates[i], places_coordinates[j]).miles
    
    # Permutations to find the shortest distance
    permutations = list(itertools.permutations(range(len(places_coordinates))))
    
    total_distances = [sum(distances[perm[i-1], perm[i]] for i in range(len(perm))) for perm in permutations]
    
    best_permutation = permutations[np.argmin(total_distances)]
    
    best_path = [places_names[i] for i in best_permutation]
    
    return jsonify({'bestPath': best_path})

if __name__ == '__main__':
    app.run(debug=True)
