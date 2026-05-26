// Leaflet map for owner dashboard - reliable inline version moved to static
document.addEventListener('DOMContentLoaded', async function() {
  const mapContainer = document.getElementById('propertyMap');
  if (!mapContainer) return;

  const rawAddress = `{{ selected_pg.address|default:"New Delhi" }}, {{ selected_pg.city|default:"New Delhi" }}, {{ selected_pg.state|default:"Delhi" }} {{ selected_pg.pin_code|default:"110001" }}`.trim();
  
  if (rawAddress === '') {
    mapContainer.innerHTML = '<p style="padding:20px;text-align:center;color:#999;">Address not available</p>';
    return;
  }

  mapContainer.innerHTML = '<div style="height:100%;display:flex;align-items:center;justify-content:center;background:#f0f8ff;border-radius:20px;color:#666;">🔍 Locating property...</div>';

  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(rawAddress)}&format=json&limit=1&countrycodes=in&addressdetails=1`
    );
    
    const data = await response.json();
    
    if (data.length && data[0]) {
      const { lat, lon } = data[0];
      
      mapContainer.style.height = '360px';
      mapContainer.innerHTML = '';
      
      const map = L.map('propertyMap').setView([parseFloat(lat), parseFloat(lon)], 16);
      
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
      }).addTo(map);
      
      // Owner PG blue marker
      const pgIcon = L.divIcon({
        className: 'pg-marker',
        html: '<div style="background:#0099ff;border-radius:50%;width:12px;height:12px;border:3px solid white;box-shadow:0 2px 6px rgba(0,153,255,0.4);"></div>',
        iconSize: [18, 18],
        iconAnchor: [9, 9]
      });
      
      L.marker([parseFloat(lat), parseFloat(lon)], {icon: pgIcon}).addTo(map)
        .bindPopup(`
          <div style="max-width:250px;padding:12px;">
            <h6 style="margin:0 0 8px 0;font-weight:700;color:#1e293b;">{{ selected_pg.title }}</h6>
            <p style="margin:4px 0;font-size:13px;color:#64748b;">📍 ${rawAddress}</p>
            <p style="margin:8px 0 0 0;font-weight:700;color:#059669;font-size:15px;">₹{{ selected_pg.price_per_month }}/month</p>
          </div>
        `)
        .openPopup();
        
    } else {
      // Robust fallback
      loadFallbackMap(mapContainer, rawAddress);
    }
  } catch (e) {
    console.error('Geocoding error:', e);
    loadFallbackMap(mapContainer, rawAddress);
  }
});

function loadFallbackMap(container, address) {
  container.innerHTML = '';
  
  const map = L.map('propertyMap').setView([28.6139, 77.2090], 11);
  
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map);
  
  L.marker([28.6139, 77.2090]).addTo(map).bindPopup(
    `<div style="padding:12px;text-align:center;">
      <strong>📍 Delhi (Fallback)</strong><br>
      <small style="color:#94a3b8;">"${address}" not found precisely<br>
      Map shows general Delhi area</small>
    </div>`
  ).openPopup();
}

