import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from build_catalog import convert


def document(content):
    return '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>'+content+'</Document></kml>'


class ConversionTests(unittest.TestCase):
    def test_mixed_geometry_keeps_hole_point_altitude_and_metadata(self):
        source = document('''<Folder><name>Village folder</name><Placemark><name>Example</name>
        <ExtendedData><Data name="code"><value>18</value></Data></ExtendedData>
        <MultiGeometry><Point><coordinates>92,26,4</coordinates></Point><Polygon>
        <outerBoundaryIs><LinearRing><coordinates>91,25 93,25 93,27 91,27</coordinates></LinearRing></outerBoundaryIs>
        <innerBoundaryIs><LinearRing><coordinates>91.5,25.5 91.5,26 92,26 91.5,25.5</coordinates></LinearRing></innerBoundaryIs>
        </Polygon></MultiGeometry></Placemark></Folder>''')
        feature = convert(source, 'village')['features'][0]
        self.assertEqual(feature['properties']['extended_data']['code'], '18')
        self.assertEqual(feature['properties']['folder_path'], 'Village folder')
        self.assertEqual(feature['geometry']['type'], 'GeometryCollection')
        point, polygon = feature['geometry']['geometries']
        self.assertEqual(point['coordinates'], [92,26,4])
        self.assertEqual(len(polygon['coordinates']), 2)
        self.assertEqual(polygon['coordinates'][0][0], polygon['coordinates'][0][-1])

    def test_description_attributes_supply_missing_name(self):
        f = convert(document('<Placemark><description><![CDATA[city: Tezpur<br>state: Assam]]></description><Point><coordinates>92,26</coordinates></Point></Placemark>'), 'cities')['features'][0]
        self.assertEqual(f['properties']['name'], 'Tezpur')
        self.assertEqual(f['properties']['description_attributes']['state'], 'Assam')

    def test_invalid_and_unsupported_spatial_content_fails(self):
        for content in ['<NetworkLink/>', '<Placemark><Point><coordinates>190,26</coordinates></Point></Placemark>', '<Placemark><LineString><coordinates>92,26</coordinates></LineString></Placemark>', '<Placemark><Point><coordinates>nan,26</coordinates></Point></Placemark>']:
            with self.subTest(content=content), self.assertRaises(ValueError):
                convert(document(content), 'bad')

    def test_no_geometry_remains_explicit_null(self):
        f = convert(document('<Placemark><name>Note</name></Placemark>'), 'notes')['features'][0]
        self.assertIsNone(f['geometry'])


if __name__ == '__main__':
    unittest.main()
