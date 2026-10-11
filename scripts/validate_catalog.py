#!/usr/bin/env python3
"""Check source integrity, export agreement and local catalog paths."""
import csv
import hashlib
import json
from pathlib import Path
from build_catalog import ROOT, convert, positions


def validate():
    datasets = json.loads((ROOT/'catalog/datasets.json').read_text())
    seen = set()
    for d in datasets:
        assert d['id'] not in seen, 'Duplicate dataset ID'; seen.add(d['id'])
        assert d['scope'] in {'assam','regional','india','local','unverified'}
        for path in d['formats'].values():
            p = (ROOT/path).resolve()
            assert p.is_relative_to(ROOT) and p.is_file(), 'Missing or unsafe download path'
        assert hashlib.sha256((ROOT/d['raw_path']).read_bytes()).hexdigest() == d['sha256'], 'Source changed'
        geo = json.loads((ROOT/d['formats']['geojson']).read_text())
        expected = convert((ROOT/d['formats']['kml']).read_bytes(), d['id'])
        assert geo == expected, 'KML/GeoJSON mismatch'
        assert geo['type'] == 'FeatureCollection' and len(geo['features']) == d['feature_count']
        ids = [f['id'] for f in geo['features']]; assert len(ids) == len(set(ids))
        for feature in geo['features']:
            if feature['geometry']:
                assert list(positions(feature['geometry'])), 'Empty geometry'
        with (ROOT/d['formats']['csv']).open(newline='') as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == d['feature_count'], 'CSV count mismatch'
        for row, feature in zip(rows, geo['features']):
            assert row['feature_id'] == feature['id']
            assert json.loads(row['geometry_geojson']) == feature['geometry']
            assert json.loads(row['properties_json']) == feature['properties']
    print(f'Validated {len(datasets)} datasets, checksums, geometry/attribute agreement, and download paths')


if __name__ == '__main__':
    validate()
