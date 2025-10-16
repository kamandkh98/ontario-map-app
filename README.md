# Ontario Region Map

A web application that displays an interactive map of Ontario, showing Northern and Southern regions with location search functionality.

## Features

-  **Interactive Map**: Built with Leaflet.js showing Ontario regions
-  **Location Search**: Search by address or coordinates (lat, lon)
-  **Region Detection**: Automatic detection of Northern vs Southern Ontario
-  **Responsive Design**: Works on desktop and mobile devices
-  **Accessible**: ARIA labels and keyboard navigation support
-  **Geocoding**: Uses Nominatim API for address-to-coordinate conversion
-  **Visual Legend**: Color-coded regions with descriptions

## Tech Stack

### Backend
- **Python 3.8+**
- **Flask** - Web framework
- **Shapely** - Geometric operations for point-in-polygon detection
- **Requests** - HTTP client for geocoding API calls
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **HTML5** with semantic markup
- **Tailwind CSS** - Utility-first CSS framework
- **Leaflet.js** - Interactive mapping library
- **Vanilla JavaScript** - No heavy frameworks, pure ES6+

## Quick Start

### 1. Install Dependencies

```bash
# Navigate to project directory
cd ontario-map-app

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
# Copy environment template
cp env_template .env

# Edit .env if needed (optional)
```

### 3. Run the Application

```bash
# Start the Flask backend
python app.py
```

The backend will start on `http://localhost:5000`

### 4. Open the Frontend

Open `index.html` in your web browser, or serve it with a simple HTTP server:

```bash
# Using Python's built-in server
python -m http.server 8000

# Then open http://localhost:8000 in your browser
```


## Usage Examples

### Search by Address
- "Toronto, ON"
- "Ottawa, Ontario"
- "Thunder Bay, ON"

### Search by Coordinates
- "43.6532, -79.3832" (Toronto)
- "45.4215, -75.6972" (Ottawa)
- "48.3809, -89.2477" (Thunder Bay)

## Project Structure

```
ontario-map-app/
├── app.py                 # Flask backend application
├── ontario_regions.geojson # GeoJSON data for Ontario regions
├── index.html            # Frontend HTML
├── app.js               # Frontend JavaScript
├── requirements.txt     # Python dependencies
├── env_template        # Environment variables template
└── README.md          # This file
```

## Development

### Backend Development
- The Flask app runs in debug mode by default
- GeoJSON data is loaded once on startup and cached
- CORS is enabled for frontend development

### Frontend Development
- Pure JavaScript ES6+ with modern browser APIs
- Responsive design with mobile-first approach
- Accessible components with ARIA labels
- Smooth animations and transitions

### Customization
- Modify `ontario_regions.geojson` to change region boundaries
- Update colors in `app.js` regionColors object
- Customize styling in `index.html` or add external CSS

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- **OpenStreetMap** - Map tiles and geocoding data
- **Leaflet.js** - Excellent mapping library
- **Tailwind CSS** - Beautiful utility-first CSS framework
- **Nominatim** - Free geocoding service
