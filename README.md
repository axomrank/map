# Assam Map Portal & Map Archive

Explore Assam districts and villages, browse thematic maps, and download reusable GIS exports. This repository combines the existing village portal with a catalog of 12 supplied KML/KMZ datasets containing **1,870 placemarks**. Counts include overlapping maps; they are not counts of unique places.

## Explore

- [District and village portal](assam/) — existing search and boundary viewer.
- [Map collection browser](collection/) — theme filtering, map previews, and downloads.
- [Naduar village map](naduar/) — existing local viewer.
- [Download catalog](catalog/README.md) — every supplied map and its available formats.

To use the interactive pages, serve the repository over HTTP. Opening HTML files directly can prevent data loading.

```bash
git clone https://github.com/axomrank/map.git
cd map
python3 -m http.server 8000
```

Open `http://localhost:8000/` or `http://localhost:8000/collection/`. No Node build or API key is required. Leaflet and basemap tiles require internet access; exports are usable offline in GIS software.

## Collection

| Theme | Supplied maps |
| --- | --- |
| Boundaries | Assam districts; India districts |
| Hydrology | Rivers |
| Transport | National highways; northeast railways |
| Settlements | Jamuguri villages; India cities |
| Heritage | Old temples in Assam |
| Elections | Lok Sabha constituencies, India reference |
| Travel | Jamugurihat routes; Uronto Apeswari |
| Mixed | Districts and rivers |

India and regional layers remain separate from Assam and local layers. The catalog scope is descriptive, not a geographic clip. The archive is an initial collection, not complete coverage of Assam.

## Repository layout

```text
assam/                  Existing Assam district/village application and data
naduar/                 Existing Naduar application and KML
collection/             Collection browser
catalog/                Dataset metadata, CSV index, download table, source registry
data/raw/<theme>/       Byte-for-byte originals with consistent filenames
data/derived/<theme>/   One folder per dataset: KML, GeoJSON, CSV, KMZ icon assets
scripts/                Reproducible conversion and validation
tests/                  Geometry conversion checks
docs/                   Development, formats, sourcing, and Assam collection plan
```

Existing portal datasets are retained separately and have not been replaced by the imported boundary collection. In particular, a supplied 33-feature district file must not be presented as today's authoritative district list.

## Formats

- **KMZ / original KML:** untouched source files; KMZ retains Google Earth styles and assets.
- **KML:** readable source XML with extracted icon assets alongside it.
- **GeoJSON:** one feature per placemark, longitude/latitude in WGS 84, with polygons, holes, lines, points, and mixed geometry collections. Names, descriptions, folders, styles, and attributes are retained as properties. Google Earth styling is not reproduced in GeoJSON.
- **CSV:** a feature table with properties and full GeoJSON geometry columns; polygons are not reduced to invented centroid points.

[Format details and optional GeoPackage/Shapefile workflows](docs/FORMATS.md).

## Rebuild and validate

Python 3.10 or later, standard library only:

```bash
python3 scripts/build_catalog.py
python3 scripts/validate_catalog.py
python3 -m unittest discover -s tests -v
```

The builder extracts KML/KMZ and regenerates exports, checksums, counts, and download links from `catalog/datasets.json`. CI checks conversions and detects stale generated files. Validation checks structure and coordinates; it does not prove polygon topology, positional accuracy, or legal boundary correctness.

## Develop and expand

Start with [development instructions](docs/DEVELOPMENT.md), follow [the contribution process](CONTRIBUTING.md), and use [the Assam collection plan](docs/COLLECTION_PLAN.md) to prioritize new themes. [The source registry](catalog/sources.csv) records researched discovery links, access notes, and collection status. Source discovery links are not downloaded datasets.

Priorities: verify provenance and dates of this collection, reconcile dated administrative boundaries, add rivers and wetlands, transport and amenities, flood/environment layers, then cultural, economic, historical, and demographic maps. Preserve source dates and identifiers so older maps remain useful without being confused with current geography.

## Provenance and reuse

The supplied files have no verified source URLs, data dates, or licenses. Their catalog status is **unverified**, and no new license is assigned to their contents. Repository availability does not establish reuse rights. Check each provider's terms before redistributing new downloads. Store a copy or reference to the applicable terms and required attribution per dataset.

Descriptions are retained as source text. The collection viewer displays plain text rather than executing embedded HTML. Combined maps can duplicate features in individual maps. Boundaries and constituency data may predate later administrative or electoral changes.
