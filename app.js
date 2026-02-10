// app.js

// Function to create a basic map
function createMap() {
    const mapContainer = document.getElementById('map');
    const mapOptions = {
        center: { lat: 0, lng: 0 }, // Center of the map
        zoom: 2,
        mapTypeId: 'terrain'
    };

    const map = new google.maps.Map(mapContainer, mapOptions);
}

// Call createMap on window load
window.onload = createMap;