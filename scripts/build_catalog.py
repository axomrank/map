#!/usr/bin/env python3
"""Reproducible KML/KMZ exports. Python standard library; no network access."""
import csv
import hashlib
import html
import json
import math
import re
import zipfile
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {'k': 'http://www.opengis.net/kml/2.2'}
GEOMETRIES = {'Point', 'LineString', 'Polygon', 'MultiGeometry'}


def local(tag):
    return tag.rsplit('}', 1)[-1]


def coordinates(node):
    result = []
    for value in (node.findtext('k:coordinates', '', NS)).split():
        point = [float(v) for v in value.split(',')]
        if len(point) not in (2, 3) or not all(math.isfinite(v) for v in point):
            raise ValueError('Invalid coordinate: ' + value)
        if not (-180 <= point[0] <= 180 and -90 <= point[1] <= 90):
            raise ValueError('Coordinate outside longitude/latitude range')
        result.append(point)
    return result


def geometry(node):
    kind = local(node.tag)
    if kind in ('Point', 'LineString'):
        points = coordinates(node)
        if len(points) < (1 if kind == 'Point' else 2):
            raise ValueError('Empty/short ' + kind)
        if kind == 'Point' and len(points) != 1:
            raise ValueError('Point contains multiple coordinates')
        return {'type': kind, 'coordinates': points[0] if kind == 'Point' else points}
    if kind == 'Polygon':
        rings = []
        for boundary in ['outerBoundaryIs', 'innerBoundaryIs']:
            for ring in node.findall('k:' + boundary + '/k:LinearRing', NS):
                points = coordinates(ring)
                if points and points[0] != points[-1]:
                    points.append(points[0][:])
                if len(points) < 4:
                    raise ValueError('Polygon ring needs at least four positions')
                rings.append(points)
        if not node.findall('k:outerBoundaryIs/k:LinearRing', NS):
            raise ValueError('Polygon missing outer ring')
        return {'type': 'Polygon', 'coordinates': rings}
    if kind == 'MultiGeometry':
        children = [geometry(c) for c in node if local(c.tag) in GEOMETRIES]
        if not children:
            raise ValueError('Empty MultiGeometry')
        return {'type': 'GeometryCollection', 'geometries': children}
    raise ValueError('Unsupported geometry ' + kind)


def positions(g):
    if g['type'] == 'GeometryCollection':
        for child in g['geometries']:
            yield from positions(child)
    else:
        def walk(value):
            if value and isinstance(value[0], (float, int)):
                yield value
            else:
                for child in value:
                    yield from walk(child)
        yield from walk(g['coordinates'])


def plain(value):
    return html.unescape(re.sub('<[^>]+>', ' ', value)).strip()


def convert(document, dataset_id):
    root = ET.fromstring(document)
    unsupported = [local(e.tag) for e in root.iter() if local(e.tag) in {'Track', 'MultiTrack', 'Model', 'GroundOverlay', 'NetworkLink'}]
    if unsupported:
        raise ValueError('Unsupported spatial content: ' + ', '.join(unsupported))
    features = []
    def visit(node, folders):
        if local(node.tag) in ('Folder', 'Document'):
            name = node.findtext('k:name', '', NS)
            folders = folders + ([name] if name else [])
        if local(node.tag) == 'Placemark':
            description = node.findtext('k:description', '', NS)
            properties = {'name': node.findtext('k:name', '', NS), 'description': plain(description),
                          'description_html': description, 'folder_path': ' / '.join(folders),
                          'source_dataset': dataset_id, 'style_url': node.findtext('k:styleUrl', '', NS),
                          'extended_data': {}}
            for item in node.findall('.//k:Data', NS):
                properties['extended_data'][item.get('name', '')] = item.findtext('k:value', '', NS)
            for item in node.findall('.//k:SimpleData', NS):
                properties['extended_data'][item.get('name', '')] = item.text or ''
            # Google exports frequently put attributes into HTML rather than ExtendedData.
            attributes = {}
            for part in re.split(r'<br\s*/?>', description, flags=re.I):
                part = plain(part)
                if ':' in part:
                    key, value = part.split(':', 1)
                    if key.strip() and key.strip().lower() != 'description':
                        attributes[key.strip()] = value.strip()
            properties['description_attributes'] = attributes
            if not properties['name']:
                for key in ('city', 'district', 'PC_NAME', 'District'):
                    if attributes.get(key):
                        properties['name'] = attributes[key]
                        break
            gs = [geometry(c) for c in node if local(c.tag) in GEOMETRIES]
            g = gs[0] if len(gs) == 1 else ({'type': 'GeometryCollection', 'geometries': gs} if gs else None)
            features.append({'type': 'Feature', 'id': f'{dataset_id}-{len(features)+1:04}', 'properties': properties, 'geometry': g})
        for child in node:
            visit(child, folders)
    visit(root, [])
    return {'type': 'FeatureCollection', 'features': features}


def build():
    catalog_path = ROOT / 'catalog/datasets.json'
    datasets = json.loads(catalog_path.read_text())
    for entry in datasets:
        raw = ROOT / entry['raw_path']
        dest = ROOT / 'data/derived' / entry['theme'] / entry['id']
        dest.mkdir(parents=True, exist_ok=True)
        if raw.suffix == '.kmz':
            with zipfile.ZipFile(raw) as archive:
                names = [n for n in archive.namelist() if n.lower().endswith('.kml')]
                if len(names) != 1:
                    raise ValueError('Expected exactly one KML in ' + str(raw))
                document = archive.read(names[0])
                # Preserve archive-relative asset paths alongside the readable KML.
                for name in archive.namelist():
                    if name == names[0] or name.endswith('/'):
                        continue
                    target = (dest / name).resolve()
                    if not target.is_relative_to(dest.resolve()):
                        raise ValueError('Unsafe archive path')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.read(name))
                if '/' in names[0]:
                    raise ValueError('Nested KML requires explicit relative asset handling')
        else:
            document = raw.read_bytes()
        (dest / 'map.kml').write_bytes(document)
        collection = convert(document, entry['id'])
        (dest / 'map.geojson').write_text(json.dumps(collection, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n')
        with (dest / 'features.csv').open('w', newline='') as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(['feature_id', 'name', 'geometry_type', 'folder_path', 'description', 'properties_json', 'geometry_geojson'])
            for feature in collection['features']:
                p, g = feature['properties'], feature['geometry']
                writer.writerow([feature['id'], p['name'], g['type'] if g else '', p['folder_path'], p['description'], json.dumps(p, ensure_ascii=False), json.dumps(g, separators=(',', ':'), allow_nan=False)])
        points = [p for f in collection['features'] if f['geometry'] for p in positions(f['geometry'])]
        entry.update(sha256=hashlib.sha256(raw.read_bytes()).hexdigest(), raw_bytes=raw.stat().st_size,
                     feature_count=len(collection['features']), geometry_types=dict(Counter(f['geometry']['type'] if f['geometry'] else 'null' for f in collection['features'])),
                     bbox=[min(p[0] for p in points), min(p[1] for p in points), max(p[0] for p in points), max(p[1] for p in points)] if points else None,
                     formats={'original': entry['raw_path'], 'kml': str((dest/'map.kml').relative_to(ROOT)), 'geojson': str((dest/'map.geojson').relative_to(ROOT)), 'csv': str((dest/'features.csv').relative_to(ROOT))})
    catalog_path.write_text(json.dumps(datasets, ensure_ascii=False, indent=2)+'\n')
    with (ROOT / 'catalog/datasets.csv').open('w', newline='') as f:
        fields = ['id', 'title', 'theme', 'scope', 'feature_count', 'license', 'date_of_data', 'verification_status', 'raw_path', 'sha256']
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore', lineterminator='\n'); writer.writeheader(); writer.writerows(datasets)
    lines = ['# Map collection catalog', '', 'Generated by `python3 scripts/build_catalog.py`. Coordinates are longitude/latitude, WGS 84. Dates and reuse rights remain unverified for supplied files.', '', '| Dataset | Theme / scope | Features | Downloads |', '| --- | --- | ---: | --- |']
    for entry in datasets:
        links = ' · '.join(f'[{kind.upper()}](../{path})' for kind, path in entry['formats'].items())
        lines.append(f"| {entry['title']} | {entry['theme']} / {entry['scope']} | {entry['feature_count']} | {links} |")
    (ROOT / 'catalog/README.md').write_text('\n'.join(lines)+'\n')
    print(f"Built {len(datasets)} datasets / {sum(d['feature_count'] for d in datasets)} features")


if __name__ == '__main__':
    build()
