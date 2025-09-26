/**
 * Ontario Map Application Frontend
 * Interactive map with region detection and location search
 */

class OntarioMapApp {
    constructor() {
        this.map = null;
        this.regionsLayer = null;
        this.searchMarker = null;
        this.apiBaseUrl = 'http://localhost:5000/api';
        
        this.init();
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            this.initMap();
            await this.loadRegions();
            this.setupEventListeners();
            console.log('✓ Ontario Map App initialized successfully');
        } catch (error) {
            console.error('✗ Failed to initialize app:', error);
            this.showError('Failed to initialize the map application. Please refresh the page.');
        }
    }

    /**
     * Initialize the Leaflet map
     */
    initMap() {
        // Initialize map centered on Ontario
        this.map = L.map('map', {
            center: [50.0, -85.0],
            zoom: 5,
            zoomControl: true,
            scrollWheelZoom: true,
            doubleClickZoom: true,
            dragging: true
        });

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 18,
            tileSize: 256,
            zoomOffset: 0
        }).addTo(this.map);

        // Add scale control
        L.control.scale({
            position: 'bottomleft',
            metric: true,
            imperial: false
        }).addTo(this.map);
    }

    /**
     * Load and display Ontario regions from the backend
     */
    async loadRegions() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/regions`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const geojsonData = await response.json();
            
            // Define region colors
            const regionColors = {
                'south': '#3b82f6', // Blue for Southern Ontario
                'north': '#16a34a'  // Green for Northern Ontario
            };

            // Create regions layer
            this.regionsLayer = L.geoJSON(geojsonData, {
                style: (feature) => ({
                    fillColor: regionColors[feature.properties.region] || '#6b7280',
                    weight: 2,
                    opacity: 1,
                    color: '#374151',
                    dashArray: '3',
                    fillOpacity: 0.4
                }),
                onEachFeature: (feature, layer) => {
                    // Add hover effects
                    layer.on({
                        mouseover: (e) => {
                            const layer = e.target;
                            layer.setStyle({
                                weight: 3,
                                color: '#1f2937',
                                dashArray: '',
                                fillOpacity: 0.6
                            });
                            layer.bringToFront();
                            
                            // Show tooltip
                            const tooltip = `
                                <div class="font-semibold">${feature.properties.name}</div>
                            `;
                            layer.bindTooltip(tooltip, {
                                permanent: false,
                                direction: 'top',
                                className: 'custom-tooltip'
                            }).openTooltip();
                        },
                        mouseout: (e) => {
                            this.regionsLayer.resetStyle(e.target);
                            e.target.closeTooltip();
                        }
                    });
                }
            }).addTo(this.map);

            // Fit map bounds to regions
            this.map.fitBounds(this.regionsLayer.getBounds(), {
                padding: [20, 20]
            });

        } catch (error) {
            console.error('Error loading regions:', error);
            this.showError('Failed to load Ontario regions data.');
        }
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        const searchBtn = document.getElementById('search-btn');
        const locationInput = document.getElementById('location-input');

        // Search button click
        searchBtn.addEventListener('click', () => this.handleSearch());

        // Enter key in search input
        locationInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleSearch();
            }
        });

        // Clear previous results when typing
        locationInput.addEventListener('input', () => {
            this.hideSearchResult();
        });
    }

    /**
     * Handle location search
     */
    async handleSearch() {
        const locationInput = document.getElementById('location-input');
        const searchBtn = document.getElementById('search-btn');
        const searchText = document.getElementById('search-text');
        const searchLoading = document.getElementById('search-loading');

        const location = locationInput.value.trim();
        if (!location) {
            this.showError('Please enter a location to search.');
            return;
        }

        // Show loading state
        searchText.textContent = 'Searching...';
        searchLoading.classList.remove('hidden');
        searchBtn.disabled = true;

        try {
            const response = await fetch(`${this.apiBaseUrl}/geocode`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ location })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Geocoding failed');
            }

            // Handle successful geocoding
            this.handleSearchResult(data);

        } catch (error) {
            console.error('Search error:', error);
            this.showError(error.message || 'Failed to search location. Please try again.');
        } finally {
            // Reset loading state
            searchText.textContent = 'Search';
            searchLoading.classList.add('hidden');
            searchBtn.disabled = false;
        }
    }

    /**
     * Handle successful search result
     */
    handleSearchResult(data) {
        const { latitude, longitude, region, message, input_type } = data;

        // Remove previous search marker
        if (this.searchMarker) {
            this.map.removeLayer(this.searchMarker);
        }

        // Create custom marker icon
        const markerIcon = L.divIcon({
            className: 'custom-marker',
            html: `
                <div class="w-8 h-8 bg-red-500 border-2 border-white rounded-full shadow-lg flex items-center justify-center">
                    <div class="w-3 h-3 bg-white rounded-full"></div>
                </div>
            `,
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        });

        // Add marker to map
        this.searchMarker = L.marker([latitude, longitude], { icon: markerIcon })
            .addTo(this.map);

        // Create popup content - use display_address from API for address searches
        let displayAddress = '';
        if (data.input_type === 'address' && data.display_address) {
            displayAddress = data.display_address;
        } else if (data.input_type === 'coordinates') {
            displayAddress = 'Coordinates Location';
        } else {
            displayAddress = 'Location';
        }

        const popupContent = `
            <div class="text-center">
                <div class="font-bold text-gray-900 mb-2">${displayAddress}</div>
                <div class="text-sm text-gray-600 mb-1">
                    ${latitude.toFixed(4)}, ${longitude.toFixed(4)}
                </div>
                ${region ? `
                    <div class="text-sm font-medium text-gray-700">
                        Located in ${region.region === 'north' ? 'Northern' : 'Southern'} Ontario Region
                    </div>
                ` : ''}
            </div>
        `;

        this.searchMarker.bindPopup(popupContent).openPopup();

        // Zoom to location with smooth animation
        this.map.flyTo([latitude, longitude], 14, {
            animate: true,
            duration: 1.5
        });

        // Show search result message
        this.showSearchResult(message, region, input_type);
    }

    /**
     * Show search result message
     */
    showSearchResult(message, region, inputType) {
        const resultDiv = document.getElementById('search-result');
        
        let bgColor = 'bg-blue-50 border-blue-200';
        let textColor = 'text-blue-800';
        let icon = '📍';

        if (region) {
            if (region.region === 'north') {
                bgColor = 'bg-green-50 border-green-200';
                textColor = 'text-green-800';
                icon = '🌲';
            } else if (region.region === 'south') {
                bgColor = 'bg-blue-50 border-blue-200';
                textColor = 'text-blue-800';
                icon = '🏙️';
            }
        } else {
            bgColor = 'bg-yellow-50 border-yellow-200';
            textColor = 'text-yellow-800';
            icon = '⚠️';
        }

        resultDiv.className = `mt-4 p-4 rounded-lg border fade-in ${bgColor}`;
        resultDiv.innerHTML = `
            <div class="flex items-start space-x-3">
                <span class="text-xl">${icon}</span>
                <div class="flex-1">
                    <div class="font-medium ${textColor}">${message}</div>
                </div>
            </div>
        `;
        resultDiv.classList.remove('hidden');
    }

    /**
     * Hide search result message
     */
    hideSearchResult() {
        const resultDiv = document.getElementById('search-result');
        resultDiv.classList.add('hidden');
    }

    /**
     * Show error message
     */
    showError(message) {
        const resultDiv = document.getElementById('search-result');
        resultDiv.className = 'mt-4 p-4 rounded-lg border bg-red-50 border-red-200 fade-in';
        resultDiv.innerHTML = `
            <div class="flex items-start space-x-3">
                <span class="text-xl">❌</span>
                <div class="flex-1">
                    <div class="font-medium text-red-800">Error</div>
                    <div class="text-sm text-red-600 mt-1">${message}</div>
                </div>
            </div>
        `;
        resultDiv.classList.remove('hidden');
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new OntarioMapApp();
});

// Add custom CSS for markers and tooltips
const style = document.createElement('style');
style.textContent = `
    .custom-marker {
        background: transparent !important;
        border: none !important;
    }
    
    .custom-tooltip {
        background: rgba(0, 0, 0, 0.8) !important;
        border: none !important;
        border-radius: 6px !important;
        color: white !important;
        font-size: 14px !important;
        padding: 8px 12px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
    
    .custom-tooltip::before {
        border-top-color: rgba(0, 0, 0, 0.8) !important;
    }
    
    .leaflet-popup-content-wrapper {
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }
`;
document.head.appendChild(style);
