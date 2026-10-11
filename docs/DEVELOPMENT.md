# Development guide

## Run locally

Use Python 3.10+ from the repository root:

```bash
python3 -m http.server 8000
```

Visit `/assam/`, `/naduar/`, and `/collection/`. The root redirects to the Assam portal. The project is a static site; no database or Node build is required. Test mobile widths and slow connections, and inspect the browser console for failed downloads.

## Add a dataset

1. Find the original publisher, determine geographic scope and date, and record download terms and attribution. Use `catalog/sources.csv` for discovery.
2. Add the untouched file to `data/raw/<theme>/<stable-id>.kml` or `.kmz`. Avoid spaces in new paths. Keep regional/India layers labeled accurately.
3. Add an entry in `catalog/datasets.json`: `id`, `title`, `theme`, `scope`, `original_filename`, `raw_path`, `source`, `source_url`, `license`, `date_of_data`, `verification_status`, `notes`. Use `null` for unknown dates/URLs and `unknown` for unverified rights. A stable ID must be unique.
4. Run `python3 scripts/build_catalog.py`, then `python3 scripts/validate_catalog.py` and the unit tests. Check names, bounds, counts, coordinate order, holes, and multi-geometries in QGIS and the browser.
5. Record acquisition date, publisher version, resolution/scale, official identifiers, attribution, and transformations in a companion metadata document when supplied. Add source license files under `docs/licenses/<id>/` if redistribution allows them.
6. Commit raw, derived, and catalog changes together. Open a PR with provenance, counts, known limitations, and a preview screenshot when the UI changes.

Other formats need explicit import adapters: preserve the original raster/PDF/GeoPackage and extend the catalog and validator before adding them to this KML pipeline. Do not rename a different format to `.kml`.

## UI and data architecture

`assam/index.html` handles the existing district/village application. Its village data is partitioned under `assam/villages-data/`; its custom JSON schema is separate from the standard GeoJSON collection.

`collection/index.html` and `collection/collection.js` load the generated catalog and automatically fetch the selected GeoJSON on page load and after a dataset or theme selection. Selection changes discard stale requests. Popups use text nodes for descriptions. Avoid eagerly loading nationwide polygons on the village portal.

Keep large full-resolution layers downloadable and generate separately documented simplified or tiled previews when needed. Record tolerance and tool version; simplification must not overwrite the source.

## Checks and releases

```bash
python3 -m unittest discover -s tests -v
python3 scripts/build_catalog.py
python3 scripts/validate_catalog.py
git diff --exit-code -- catalog data/derived
```

CI runs these checks on push and pull request. They check conversion integrity and reproducibility; use GIS topology tools for self-intersections and coverage gaps. For a release, tag the data date/version, record changes, and publish a checksum list. Monitor GitHub's file limits; use a documented external download archive for large rasters and national extracts.

GitHub Pages can serve these files from the repository root. Keep existing hosting settings unless explicitly changing deployment. Links should remain relative so previews work under a repository subpath.
