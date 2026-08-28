# Assam Map Portal

An interactive web map application for visualizing districts and villages across Assam. This project provides a performant map interface for finding and exploring detailed geographic boundaries in the state.

## 🌟 Features
- **Interactive Mapping:** Powered by Leaflet for smooth panning and zooming.
- **District & Village Search:** Fast, client-side search filtering through thousands of villages and all districts.
- **Dynamic Boundary Loading:** Efficiently fetches and renders exact simplified polygon boundaries for districts and individual villages on demand.
- **Mobile Friendly:** Fully responsive design built to work seamlessly on mobile and desktop.

## 🛠️ Tech Stack
- **Frontend:** HTML, CSS, JavaScript (Vanilla)
- **Mapping:** Leaflet.js
- **Data Formats:** GeoJSON for districts, custom JSON structures for fast village indexing and boundary caching.

## 🚀 Getting Started
Simply serve the files using any standard HTTP server.
```bash
# Example using Python's built-in server:
python3 -m http.server 8000
```
Then navigate to `http://localhost:8000/` in your browser.

## 📊 Data
Geographic data is optimized for performance, split into:
- `districts-simple.geojson` for district boundaries.
- `villages-index.json` / `villages-slim.json` for rapid village search and point rendering.
- `villages-data/` caching exact boundaries for villages by district.
