#!/usr/bin/env python3
"""
Ontario Map Application Backend
A Flask API for geocoding locations and determining Ontario regions.
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple, Union

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from shapely.geometry import Point, shape
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

# Global variable to store GeoJSON data
ontario_regions = None

def load_geojson_data() -> Dict:
    """Load Ontario regions GeoJSON data from file."""
    global ontario_regions
    if ontario_regions is None:
        try:
            with open('ontario_regions.geojson', 'r', encoding='utf-8') as f:
                ontario_regions = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("ontario_regions.geojson file not found")
        except json.JSONDecodeError:
            raise ValueError("Invalid GeoJSON format in ontario_regions.geojson")
    return ontario_regions

def parse_coordinates(location_input: str) -> Optional[Tuple[float, float]]:
    """
    Parse coordinate string in various formats.
    
    Args:
        location_input: String that might contain lat,lon coordinates
        
    Returns:
        Tuple of (latitude, longitude) or None if not valid coordinates
    """
    # Remove whitespace and common separators
    clean_input = re.sub(r'[^\d\.-]', ' ', location_input.strip())
    parts = clean_input.split()
    
    if len(parts) == 2:
        try:
            lat, lon = float(parts[0]), float(parts[1])
            # Validate coordinate ranges
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return (lat, lon)
        except ValueError:
            pass
    
    return None

def geocode_address(address: str) -> Optional[Tuple[float, float, str]]:
    """
    Geocode an address using Nominatim API with multiple fallback strategies.
    
    Args:
        address: Address string to geocode
        
    Returns:
        Tuple of (latitude, longitude, simplified_address) or None if geocoding fails
    """
    print(f"Attempting to geocode address: '{address}'")
    
    # Try different address variations to improve success rate
    address_variations = [
        address,  # Original address
        f"{address}, Ontario, Canada",  # Add province and country
        f"{address}, ON, Canada",  # Abbreviated province
        address.replace(",", "").strip(),  # Remove commas
    ]
    
    for i, addr_variant in enumerate(address_variations):
        print(f"Trying variation {i+1}: '{addr_variant}'")
        
        try:
            # Use Nominatim API with proper headers and address details
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': addr_variant,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'ca',  # Limit to Canada
                'addressdetails': 1    # Get structured address components
            }
            headers = {
                'User-Agent': 'Ontario-Map-App/1.0'
            }
            
            print(f"Making request to Nominatim with params: {params}")
            response = requests.get(url, params=params, headers=headers, timeout=10)
            print(f"Response status: {response.status_code}")
            
            response.raise_for_status()
            
            data = response.json()
            print(f"Response data: {data}")
            
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                print(f"Successfully geocoded to: {lat}, {lon}")
                
                # Extract simplified address components
                result = data[0]
                address_details = result.get('address', {})
                address_parts = []
                
                # Get house number and street name
                house_number = address_details.get('house_number', '')
                road = address_details.get('road', '')
                
                if house_number and road:
                    address_parts.append(f"{house_number} {road}")
                elif road:
                    address_parts.append(road)
                
                # Get city/town/village (try multiple fields as different places use different terms)
                city = (address_details.get('city') or 
                       address_details.get('town') or 
                       address_details.get('village') or 
                       address_details.get('municipality'))
                
                if city:
                    address_parts.append(city)
                
                # Create simplified address or fallback to display_name
                if address_parts:
                    simplified_address = ", ".join(address_parts)
                else:
                    # Fallback: use display_name but try to simplify it
                    display_name = result.get('display_name', address)
                    # Try to extract just the first few parts before province
                    parts = display_name.split(', ')
                    if len(parts) > 2:
                        # Take first 2-3 parts, avoiding province/country
                        simplified_parts = []
                        for part in parts[:4]:  # Take up to 4 parts
                            if part.lower() not in ['ontario', 'canada', 'on']:
                                simplified_parts.append(part)
                            if len(simplified_parts) >= 2:  # Stop after 2 meaningful parts
                                break
                        simplified_address = ", ".join(simplified_parts) if simplified_parts else display_name
                    else:
                        simplified_address = display_name
                    
                print(f"Simplified address: {simplified_address}")
                return (lat, lon, simplified_address)
            else:
                print(f"No results returned from Nominatim API for variation {i+1}")
                
        except requests.RequestException as e:
            print(f"Request error during geocoding (variation {i+1}): {e}")
        except KeyError as e:
            print(f"KeyError during geocoding (variation {i+1}): {e}")
        except ValueError as e:
            print(f"ValueError during geocoding (variation {i+1}): {e}")
        except IndexError as e:
            print(f"IndexError during geocoding (variation {i+1}): {e}")
        except Exception as e:
            print(f"Unexpected error during geocoding (variation {i+1}): {e}")
    
    print("All geocoding variations failed")
    return None

def calculate_funding_eligibility(applicant_type: str, municipality_population: Optional[str], region: Optional[str]) -> Dict:
    """
    Calculate funding eligibility based on applicant type, municipality population, and region.
    
    Args:
        applicant_type: Type of applicant (indigenous, municipality, business)
        municipality_population: Population size for municipalities (below-170k, above-170k)
        region: Ontario region (north, south, or None if outside Ontario)
        
    Returns:
        Dictionary with funding information
    """
    # Default values
    funding_percentage = 0
    applicant_type_display = ""
    municipality_population_display = ""
    
    # Set display names
    applicant_type_displays = {
        'indigenous': 'Indigenous community or business',
        'municipality': 'Municipalities',
        'business': 'Businesses, not for profit corporations, and broader public sector'
    }
    
    municipality_population_displays = {
        'below-170k': 'Below 170,000',
        'above-170k': 'Above 170,000'
    }
    
    applicant_type_display = applicant_type_displays.get(applicant_type, applicant_type)
    
    if municipality_population:
        municipality_population_display = municipality_population_displays.get(municipality_population, municipality_population)
    
    # Calculate funding percentage based on rules:
    # - All applicants in Northern region: 75%
    # - Indigenous community or business and Municipalities with populations below 170,000: 75%
    # - Businesses, not for profit corporations, and broader public sector and municipalities with populations above 170,000: 50%
    
    if region == 'north':
        # All applicants in Northern region get 75%
        funding_percentage = 75
    elif region == 'south':
        if applicant_type == 'indigenous':
            # Indigenous communities get 75% in Southern Ontario
            funding_percentage = 75
        elif applicant_type == 'municipality':
            if municipality_population == 'below-170k':
                # Municipalities below 170k get 75% in Southern Ontario
                funding_percentage = 75
            elif municipality_population == 'above-170k':
                # Municipalities above 170k get 50% in Southern Ontario
                funding_percentage = 50
        elif applicant_type == 'business':
            # Businesses get 50% in Southern Ontario
            funding_percentage = 50
    else:
        # Outside Ontario - no funding
        funding_percentage = 0
    
    return {
        'applicant_type': applicant_type,
        'applicant_type_display': applicant_type_display,
        'municipality_population': municipality_population,
        'municipality_population_display': municipality_population_display,
        'funding_percentage': funding_percentage,
        'region': region
    }

def point_in_region(lat: float, lon: float) -> Optional[Dict]:
    """
    Determine which Ontario region contains the given point.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Dictionary with region information or None if not in any region
    """
    try:
        geojson_data = load_geojson_data()
        point = Point(lon, lat)  # Note: Shapely uses (x, y) = (lon, lat)
        
        for feature in geojson_data['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(point):
                return {
                    'region': feature['properties']['region'],
                    'name': feature['properties']['name'],
                    'description': feature['properties']['description']
                }
                
    except Exception as e:
        print(f"Point-in-polygon error: {e}")
    
    return None

@app.route('/api/regions', methods=['GET'])
def get_regions():
    """Return the Ontario regions GeoJSON data."""
    try:
        geojson_data = load_geojson_data()
        return jsonify(geojson_data)
    except Exception as e:
        print(f"Error loading regions: {e}")
        return jsonify({'error': 'Failed to load region data'}), 500

@app.route('/api/geocode', methods=['POST'])
def geocode():
    """
    Geocode a location and determine its Ontario region with funding eligibility.
    
    Request body:
    {
        "location": "address or coordinates",
        "applicant_type": "indigenous|municipality|business",
        "municipality_population": "below-170k|above-170k" (optional, only for municipalities)
    }
    
    Returns:
    {
        "success": true,
        "latitude": float,
        "longitude": float,
        "region": {
            "region": "north|south",
            "name": "Region Name",
            "description": "Region Description"
        },
        "input_type": "coordinates|address",
        "display_address": "Simplified address",
        "funding_info": {
            "applicant_type": "indigenous|municipality|business",
            "applicant_type_display": "Display name",
            "municipality_population": "below-170k|above-170k",
            "municipality_population_display": "Display name",
            "funding_percentage": 75 or 50,
            "region": "north|south"
        }
    }
    """
    try:
        data = request.get_json()
        if not data or 'location' not in data:
            return jsonify({'error': 'Location parameter is required'}), 400
        
        location_input = data['location'].strip()
        if not location_input:
            return jsonify({'error': 'Location cannot be empty'}), 400
        
        # Get applicant type and municipality population
        applicant_type = data.get('applicant_type')
        municipality_population = data.get('municipality_population')
        
        if not applicant_type:
            return jsonify({'error': 'Applicant type is required'}), 400
        
        # Validate applicant type
        valid_applicant_types = ['indigenous', 'municipality', 'business']
        if applicant_type not in valid_applicant_types:
            return jsonify({'error': 'Invalid applicant type'}), 400
        
        # Validate municipality population if applicable
        if applicant_type == 'municipality':
            if not municipality_population:
                return jsonify({'error': 'Municipality population is required for municipality applicants'}), 400
            valid_populations = ['below-170k', 'above-170k']
            if municipality_population not in valid_populations:
                return jsonify({'error': 'Invalid municipality population size'}), 400
        
        # First, try to parse as coordinates
        coords = parse_coordinates(location_input)
        input_type = 'coordinates'
        display_address = None
        
        # If not coordinates, try geocoding as address
        if coords is None:
            geocode_result = geocode_address(location_input)
            input_type = 'address'
            
            if geocode_result is None:
                return jsonify({
                    'error': 'Could not geocode the provided location. Please try:\n• Adding "Ontario, Canada" to your address\n• Using a more specific address (e.g., "123 Main Street, Toronto, ON")\n• Checking the spelling of your address\n• Using coordinates in the format "latitude, longitude"'
                }), 400
            
            lat, lon, display_address = geocode_result
        else:
            lat, lon = coords
        
        # Check if point is in Ontario regions
        region_info = point_in_region(lat, lon)
        
        # Calculate funding eligibility
        region_name = region_info['region'] if region_info else None
        funding_info = calculate_funding_eligibility(applicant_type, municipality_population, region_name)
        
        if region_info is None:
            return jsonify({
                'success': True,
                'latitude': lat,
                'longitude': lon,
                'region': None,
                'input_type': input_type,
                'display_address': display_address,
                'message': 'This location is outside of Ontario or in an unmapped area.',
                'funding_info': funding_info
            })
        
        return jsonify({
            'success': True,
            'latitude': lat,
            'longitude': lon,
            'region': region_info,
            'input_type': input_type,
            'display_address': display_address,
            'message': f'This location is in {region_info["name"]}.',
            'funding_info': funding_info
        })
        
    except Exception as e:
        print(f"Geocoding endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'ontario-map-api'})

@app.route('/')
def index():
    """Serve the main HTML page."""
    return app.send_static_file('index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return app.send_static_file(filename)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure GeoJSON data loads on startup
    try:
        load_geojson_data()
        print("Ontario regions GeoJSON data loaded successfully")
    except Exception as e:
        print(f"Error loading GeoJSON data: {e}")
        exit(1)
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)