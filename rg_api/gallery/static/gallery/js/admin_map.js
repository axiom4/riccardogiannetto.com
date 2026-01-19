document.addEventListener('DOMContentLoaded', function() {
    // Wait for everything to load
    const latInput = document.getElementById('id_latitude');
    const lonInput = document.getElementById('id_longitude');
    
    if (!latInput || !lonInput) return;

    // Create container for map
    const mapDiv = document.createElement('div');
    mapDiv.id = 'admin_map_canvas';
    mapDiv.style.height = '500px';
    mapDiv.style.width = '100%';
    mapDiv.style.marginTop = '10px';
    mapDiv.style.border = '1px solid #ccc';
    
    // Find the closest row to inject the map
    const formRow = latInput.closest('.form-row');
    if (formRow) {
        formRow.parentNode.insertBefore(mapDiv, formRow.nextSibling);
    } else {
        // Fallback
        latInput.parentNode.appendChild(mapDiv);
    }

    // Default to a generic location (Rome) if empty
    let initialLat = parseFloat(latInput.value) || 41.9028;
    let initialLon = parseFloat(lonInput.value) || 12.4964;
    let zoomLevel = (latInput.value && lonInput.value) ? 16 : 5;

    const map = L.map('admin_map_canvas').setView([initialLat, initialLon], zoomLevel);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    }).addTo(map);

    let marker;

    if (latInput.value && lonInput.value) {
        marker = L.marker([initialLat, initialLon], {draggable: true}).addTo(map);
        
        // Update inputs on drag
        marker.on('dragend', function(e) {
            updateInputs(e.target.getLatLng());
        });
    }

    // Map Click Event
    map.on('click', function(e) {
        if (marker) {
            marker.setLatLng(e.latlng);
        } else {
            marker = L.marker(e.latlng, {draggable: true}).addTo(map);
            marker.on('dragend', function(ev) {
                updateInputs(ev.target.getLatLng());
            });
        }
        updateInputs(e.latlng);
    });

    function updateInputs(latlng) {
        latInput.value = latlng.lat.toFixed(6);
        lonInput.value = latlng.lng.toFixed(6);
    }
    
    // Listen to manual input changes
    function manualUpdate() {
        const lat = parseFloat(latInput.value);
        const lon = parseFloat(lonInput.value);
        if (!isNaN(lat) && !isNaN(lon)) {
             const newLatLng = new L.LatLng(lat, lon);
             if (marker) {
                 marker.setLatLng(newLatLng);
             } else {
                 marker = L.marker(newLatLng, {draggable: true}).addTo(map);
                 marker.on('dragend', function(ev) {
                    updateInputs(ev.target.getLatLng());
                });
             }
             map.panTo(newLatLng);
        }
    }
    
    latInput.addEventListener('change', manualUpdate);
    lonInput.addEventListener('blur', manualUpdate); // blur is safer to not jump around while typing
});
