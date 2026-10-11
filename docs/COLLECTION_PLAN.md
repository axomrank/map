# Building a broad Assam map archive

The goal is a dated, searchable archive of Assam's geography, places, infrastructure, environment, economy, and history. The current import covers 12 supplied files. This plan describes gaps and discovery sources; it does not claim that all themes have already been collected.

## Themes to collect

| Theme | Layers and related tables | First discovery sources | Current status |
| --- | --- | --- | --- |
| Administration | State, districts, subdivisions, circles, blocks, panchayats, wards, villages; dated change history | Assam district sites, Census, Bharat Maps | Supplied district/village files; verify vintage |
| Settlements & population | Towns, villages, population, households, amenities, language and demographic aggregates | Census district handbooks and PCA tables | Local village layer + India city reference; demographic joins pending |
| Elections | Dated Assembly/Lok Sabha boundaries, polling stations, delimitation documents | Election Commission of India | India Lok Sabha source imported; vintage unknown |
| Water | Brahmaputra/Barak tributaries, wetlands, beels, drainage, catchments, embankments, gauges | Bhuvan, ASDMA, relevant government departments | River lines imported; remaining layers pending |
| Transport | Roads, bridges, rail/stations, airports, ferries, ports, public transport | OSM regional extracts, official agencies | Highway/rail/local-route samples imported |
| Terrain & geology | Elevation, contours, slope, soils, geology, groundwater | Survey of India, Bhuvan and original scientific publishers | Discovery/rights checks pending |
| Hazards & climate | Flood extent by date, flood hazard, erosion, landslides, earthquake risk, rainfall | ASDMA, Bhuvan, original monitoring agencies | Source registry prepared |
| Forest & biodiversity | Protected areas, forests, wildlife corridors, habitats, wetlands | Environment/forest departments, Bhuvan | Pending verified downloadable sources |
| Agriculture & economy | Land use, tea gardens, crops, irrigation, industry, markets | Bhuvan, official department statistics, OSM | Pending |
| Public services | Hospitals, schools, colleges, police/fire, shelters, utilities | ASDMA utility mapping, district sites, OSM | Discovery source prepared |
| Urban planning | Municipalities, wards, master plans, land use, drainage | Assam GIS GeoHub | Source identified |
| Culture & tourism | Temples, satras, mosques, monuments, museums, visitor facilities, trails | Official tourism/district/heritage inventories; verified field contributions | Temple and travel samples imported |
| Land records | Cadastral map references, survey parcels, public access instructions | Assam Bhunaksha | Link-only discovery; review terms and personal-data fields |
| Historical maps | Gazetteers, dated administrative maps, old transport routes, georeferenced scans | Census archives, official/library collections | Census 2011 map source identified |
| Satellite imagery & time series | Dated imagery, land-cover change, seasonal flood imagery | Bhuvan and original earth-observation publishers | Pending |

## Phased work

1. **Establish provenance.** Identify publishers, dates, and rights for the imported files; audit the existing portal separately. Compare Assam district and election layers with dated official records. Add an administrative change log instead of relabeling old boundaries as current.
2. **Build a reference base.** Collect verified state/district boundaries and stable official codes, then villages/towns, rivers, transport, and public amenities. Record Assam versus northeast/India scope. Clip regional data only against a documented boundary version.
3. **Add environmental and social layers.** Prioritize flood hazard and dated flood observations, wetlands/forest, terrain, land use, and Census aggregates. Keep observation time separate from retrieval time. Never compare census figures using mismatched boundary vintages without a crosswalk.
4. **Add culture and history.** Verify local place names, multilingual labels, photos with reuse permission, historical maps, and travel information. Preserve archival context and uncertainty.
5. **Improve delivery.** Add search by theme/district/date, multiple overlay comparison, time controls, download bundles, accessible legends, print layouts, and documented tiles for large layers. Keep analytical downloads separate from simplified previews.

## Source discovery and acquisition

[The source registry](../catalog/sources.csv) stores links checked on 11 October 2026. It currently records discovery sources, not completed external downloads. Portals may require registration, interactive selection, or license review; availability of a viewing service does not establish permission for bulk redistribution.

Useful starting points:

- [Assam GIS GeoHub announcement and portal link](https://tcp.assam.gov.in/frontimpotentdata/launch-of-gis-geohub-portal-by-the-department-of-housing-urban-affairs-government): urban spatial planning datasets.
- [Assam flood hazard resources](https://asdma.gov.in/flood_hazard.html) and [ASDMA utility mapping project](https://www.onlineasdma.assam.gov.in/project_gis_mappimg.html): hazard and infrastructure discovery.
- [Bhuvan](https://bhuvan-app1.nrsc.gov.in/bhuvan2d2.0/): thematic and earth-observation discovery; check product-specific terms.
- [Census 2011 Assam administrative map](https://censusindia.gov.in/nada/index.php/catalog/1369/) and [district census handbooks](https://www.censusindia.gov.in/census.website/node/45): dated geography and village/amenity context.
- [ECI delimitation resources](https://www.eci.gov.in/delimitation/): Assam 2023 delimitation documents.
- [Geofabrik northeast extract](https://download.geofabrik.de/asia/india/north-eastern-zone.html): OSM PBF, Shapefile and GeoPackage download options; the region is broader than Assam. Preserve OSM attribution and follow [ODbL terms](https://www.openstreetmap.org/copyright).
- [Survey of India Online Maps](https://onlinemaps.surveyofindia.gov.in/): topographic map products with access/product conditions.
- [Assam district websites](https://gad.assam.gov.in/information-and-services/district-websites): official district resources and local context.

Before acquiring a source, record its exact product URL, version/date, extent, CRS, scale/resolution, format, terms, attribution, and expected size. Download an immutable dated snapshot, hash it, and retain the original. For a manual portal download, log selection parameters. For an API/ETL job, keep a reproducible script with limits and cached responses.

## Organizing Assam information beyond maps

Store geospatial files under `data/raw/<theme>/` and generated files under `data/derived/<theme>/<id>/`. Add non-spatial tables under `data/tables/<theme>/` once available. Related reports, gazetteers and metadata belong under `docs/references/<theme>/`, or in the source registry when redistribution is restricted. Do not create empty placeholder files that look like collected datasets.

For place tables, prefer fields: `place_id`, `official_code`, `name_original`, `name_en`, `name_as`, `category`, `district_code`, `boundary_version`, `longitude`, `latitude`, `source_url`, `data_date`, `retrieved_at`, `license`, `verification_status`. Use null for unknowns. Sensitive ownership/person-level details require a separate access-controlled workflow; public maps should use appropriate aggregate/place information.

## Completion measures

Track themes collected, districts covered per dated boundary version, source/licensing completeness, features with official codes, validation issues, and update lag. A theme is complete only against a stated checklist and date. Every release should list known gaps and distinguish verified official records, community observations, derived analyses, and historical material.
