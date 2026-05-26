// Leaflet map fix for owner_dashboard.html - clean implementation
document.addEventListener('DOMContentLoaded', async function() {
  const mapContainer = document.getElementById('propertyMap');
  if (!mapContainer) return;

  const pgAddress = `{{ selected_pg.address }}, {{ selected_pg.city }}, {{ selected_pg.state }} {{ selected_pg.pin_code }}`.trim();
  
  if (!pgAddress) {
    mapContainer.innerHTML = '<p style="padding: 20px; text-align: center; color: #999;">No address available</p>';
    return;
  }

  try {
    // Nominatim geocoding with better params for India addresses
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(pgAddress)}&countrycodes=in&addressdetails=1&polygon_svg=1`
    );
    
    if (!response.ok) throw new Error('Geocoding API error');
    
    const data = await response.json();
    
    if (data && data.length > 0) {
      const lat = parseFloat(data[0].lat);
      const lon = parseFloat(data[0].lon);
      
      // Create map
      const map = L.map('propertyMap').setView([lat, lon], 16);
      
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
      }).addTo(map);
      
      // Custom blue marker matching Google style
      const blueIcon = L.divIcon({
        className: 'custom-marker',
        html: `
          <svg width="28" height="40" viewBox="0 0 28 40" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 0A14 14 0 0 0 0 14v26a14 14 0 0 0 28 0V14A14 14 0 0 0 14 0Z" fill="#0099ff"/>
            <circle cx="14" cy="14" r="2" fill="white"/>
          </svg>
        `,
        iconSize: [28, 40],
        iconAnchor: [14, 40],
        popupAnchor: [0, -40]
      });
      
      const marker = L.marker([lat, lon], {icon: blueIcon}).addTo(map)
        .bindPopup(`
          <div style="min-width: 200px; padding: 12px;">
            <h6 style="margin: 0 0 8px 0; color: #1e1f3d;">${'{{ selected_pg.title }}'}</h6>
            <p style="margin: 4px 0; font-size: 13px; color: #666;">📍 {{ selected_pg.address }}</p>
            <p style="margin: 4px 0; font-weight: bold; color: #00d4ff;">₹{{ selected_pg.price_per_month }}/month</p>
          </div>
        `).openPopup();
        
    } else {
      // Fallback to Delhi + error message
      const fallbackMap = L.map('propertyMap').setView([28.6139, 77.2090], 10);
      
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(fallbackMap);
      
      fallbackMap.addLayer(L.marker([28.6139, 77.2090]).bindPopup(
        '<div style="padding: 12px;"><strong>Using fallback location (Delhi)</strong><br>' +
        'Precise address not found. Consider adding lat/lng coordinates for better accuracy.</div>'
      ));
    }
  } catch (error) {
    console.error('Map initialization failed:', error);
    mapContainer.innerHTML = `
      <div style="padding: 20px; text-align: center; color: #999;">
        <p>Map temporarily unavailable</p>
        <small>Check browser console for details</small>
      </div>
    `;
  }
});
