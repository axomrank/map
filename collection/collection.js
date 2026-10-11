'use strict';
const theme = document.getElementById('theme');
const dataset = document.getElementById('dataset');
const details = document.getElementById('details');
const downloads = document.getElementById('downloads');
const status = document.getElementById('status');
const load = document.getElementById('load');
let datasets = [], layer = null, request = 0;
const map = L.map('map').setView([26.2, 92.8], 7);
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors', maxZoom: 19
}).addTo(map);
function selected() { return datasets.find(d => d.id === dataset.value); }
function info() {
  ++request; // Invalidate an in-flight load when selection changes.
  load.disabled = false;
  if (layer) { map.removeLayer(layer); layer = null; }
  const item = selected();
  details.replaceChildren(); downloads.replaceChildren();
  if (!item) { load.disabled = true; return; }
  for (const text of [`${item.feature_count} features · ${item.scope}`, `Verification: ${item.verification_status}`, `Data date: ${item.date_of_data || 'unknown'} · License: ${item.license}`, item.notes]) {
    const p = document.createElement('p'); p.textContent = text; details.append(p);
  }
  for (const [format, path] of Object.entries(item.formats)) {
    const a = document.createElement('a'); a.textContent = format.toUpperCase(); a.href = '../' + path; a.download = ''; downloads.append(a);
  }
  status.textContent = 'Select Show on map to preview this dataset.';
}
function options() {
  dataset.replaceChildren();
  for (const item of datasets.filter(d => !theme.value || d.theme === theme.value)) {
    const option = document.createElement('option'); option.value = item.id; option.textContent = item.title; dataset.append(option);
  }
  info();
}
theme.addEventListener('change', options);
dataset.addEventListener('change', info);
load.addEventListener('click', async () => {
  const item = selected(), ticket = ++request;
  if (!item) return;
  load.disabled = true; status.textContent = 'Loading map…';
  try {
    const response = await fetch('../' + item.formats.geojson);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const geojson = await response.json();
    if (ticket !== request) return;
    const next = L.geoJSON(geojson, {
      style: {color:'#176b4b', weight:2, fillOpacity:0.12},
      pointToLayer: (feature, latlng) => L.circleMarker(latlng, {radius:5, color:'#176b4b', fillOpacity:0.8}),
      onEachFeature: (feature, child) => {
        const popup = document.createElement('div');
        const title = document.createElement('strong'); title.textContent = feature.properties.name || feature.id;
        const description = document.createElement('p'); description.textContent = feature.properties.description || 'No description supplied.';
        popup.append(title, description); child.bindPopup(popup);
      }
    });
    if (layer) map.removeLayer(layer);
    layer = next.addTo(map);
    if (layer.getBounds().isValid()) map.fitBounds(layer.getBounds(), {padding:[20,20], maxZoom:14});
    status.textContent = `Showing ${item.title}: ${geojson.features.length} features.`;
  } catch (error) {
    if (ticket === request) status.textContent = `Could not load map: ${error.message}. Serve the repository with an HTTP server.`;
  } finally { if (ticket === request) load.disabled = false; }
});
(async () => {
  try {
    const response = await fetch('../catalog/datasets.json');
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    datasets = await response.json();
    for (const value of [...new Set(datasets.map(d => d.theme))].sort()) {
      const option = document.createElement('option'); option.value = value; option.textContent = value; theme.append(option);
    }
    options();
  } catch (error) { status.textContent = `Could not load catalog: ${error.message}.`; }
})();
