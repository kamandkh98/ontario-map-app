# Ontario Regional Map

An interactive web application for identifying whether a location is in Northern or Southern Ontario. This tool helps determine regional classifications for funding eligibility and other location-based services.

## Features

- Interactive map with Northern and Southern Ontario regions
- Search locations by address or GPS coordinates
- Automatic region detection
- Mobile-friendly responsive design

## Getting Started

Install dependencies and run the application:

```bash
pip install -r requirements.txt
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

Search for any Ontario location by entering:
- An address (e.g., "Toronto, ON" or "Thunder Bay, ON")
- Coordinates (e.g., "43.6532, -79.3832")

The map will show whether the location is in Northern or Southern Ontario.

## Technology

Built with Flask (Python), Leaflet.js, and Tailwind CSS.
