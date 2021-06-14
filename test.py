"""Unit-tests with python unittest. Please read the official documentation at
https://docs.python.org/3/library/unittest.html
"""
import glob
import json
import unittest

from dataforwarding import parser2 as parser

def document(fn):
    """Load a json document"""
    document = {}
    with open(fn) as file:
        document = json.load(file)
    return document

def sample_documents(globstring):
    """Iterate over json-parsed test documents"""
    for fn in glob.glob(globstring):
        yield fn, document(fn)

class TestParser(unittest.TestCase):
    def test_parse_aistin_common_in(self):
        """All test documents should produce the common measurements"""
        for name, document in sample_documents("test-assets/aistin/*.json"):
            with self.subTest(case=name):
                parsed = parser.parse(document, "aistin")
                self.assertIn("acceleration", parsed)
                self.assertIn("x", parsed.get("acceleration"))
                self.assertIn("y", parsed.get("acceleration"))
                self.assertIn("z", parsed.get("acceleration"))
                self.assertIn("battery", parsed)
                self.assertIn("battery_percentage", parsed)
                self.assertIn("deveui", parsed)
                self.assertIn("humidity", parsed)
                self.assertIn("orientation", parsed)
                self.assertIn("pressure", parsed)
                self.assertIn("temperature", parsed)
                self.assertIn("timestamp_parser", parsed)

    def test_parse_aistin_common_values_mv(self):
        """Mv should produce correct common values"""
        parsed = parser.parse(document("test-assets/aistin/mv.json"), "aistin")
        self.assertEqual(parsed.get("acceleration", {}).get("x"), 0.005)
        self.assertEqual(parsed.get("acceleration", {}).get("y"), 0.02)
        self.assertEqual(parsed.get("acceleration", {}).get("z"), 1.013)
        self.assertEqual(parsed.get("battery"), 3.35)
        self.assertEqual(parsed.get("battery_percentage"), 29)
        self.assertEqual(parsed.get("deveui"), "187c569c081ccbe9")
        self.assertEqual(parsed.get("humidity"), 42.9)
        self.assertEqual(parsed.get("orientation"), 1.1)
        self.assertEqual(parsed.get("pressure"), 1.008)
        self.assertEqual(parsed.get("temperature"), 23.9)
        self.assertEqual(parsed.get("timestamp_node"), 1623419299)

    def test_parse_aistin_common_values_sh(self):
        """Sh should produce correct common values"""
        parsed = parser.parse(document("test-assets/aistin/sh.json"), "aistin")
        self.assertEqual(parsed.get("acceleration", {}).get("x"), -0.003)
        self.assertEqual(parsed.get("acceleration", {}).get("y"), 0.003)
        self.assertEqual(parsed.get("acceleration", {}).get("z"), 1.009)
        self.assertEqual(parsed.get("battery"), 3.35)
        self.assertEqual(parsed.get("battery_percentage"), 29)
        self.assertEqual(parsed.get("deveui"), "02e5cc9ede0cbb7d")
        self.assertEqual(parsed.get("humidity"), 43)
        self.assertEqual(parsed.get("orientation"), 0.2)
        self.assertEqual(parsed.get("pressure"), 1.008)
        self.assertEqual(parsed.get("temperature"), 23.8)
        self.assertEqual(parsed.get("timestamp_node"), 1623419897)

    def test_parse_aistin_dp(self):
        """Dp should be correct"""
        parsed = parser.parse(document("test-assets/aistin/dp.json"), "aistin")
        self.assertEqual(parsed.get("differential_pressure"), -4)  # TODO name, unit

    def test_parse_aistin_ect(self):
        """Ect should be correct"""
        parsed = parser.parse(document("test-assets/aistin/ect.json"), "aistin")
        self.assertEqual(parsed.get("co2"), 400)
        self.assertEqual(parsed.get("organic_compounds"), 40)  # TODO name, unit

    def test_parse_aistin_mv(self):
        """Mv should be correct"""
        parsed = parser.parse(document("test-assets/aistin/mv.json"), "aistin")
        self.assertEqual(parsed.get("amplitude"), 30)
        self.assertEqual(parsed.get("frequency"), 11)

    def test_parse_aistin_pir(self):
        """Pir should be correct"""
        parsed = parser.parse(document("test-assets/aistin/pir.json"), "aistin")
        # TODO this is quite different
        NotImplemented

    def test_parse_aistin_sh(self):
        """Sh should be correct"""
        parsed = parser.parse(document("test-assets/aistin/sh.json"), "aistin")
        self.assertEqual(parsed.get("object_temperature"), 23.7)
        self.assertEqual(parsed.get("moisture"), 44.9)

    def test_parse_nb100(self):
        """Nb100 should be correct""" 
        for name, document in sample_documents("test-assets/nb100/*.json"):
            with self.subTest(case=name):
                parsed = parser.parse(document, "nb_100")
                self.assertEqual(parsed["battery"], 3.613)
                self.assertEqual(parsed["deveui"], "11000014")
                self.assertEqual(parsed["humidity"], 29.6)
                self.assertEqual(parsed["pressure"], 1.016)
                self.assertEqual(parsed["rssi"], -75)
                self.assertEqual(parsed["temperature"], 26.9)
                self.assertEqual(parsed["timestamp_node"], 1623159476)
                self.assertIn("timestamp_parser", parsed)

    def test_parse_no_none(self):
        """No measurement should be empty"""
        for name, document in sample_documents("test-assets/nb100/*.json"):
            parsed = parser.parse(document)
            for k, v in parsed.items():
                with self.subTest(case=F"{k} shouldn't be empty when parsing {name}"):
                    self.assertIsNotNone(v, F"{k} is a None")
                    self.assertNotEqual("", v, F"{k} is an empty string")
                    self.assertNotEqual(0, v, F"{k} is zero")

    def test_parse_raise(self):
        """Bad document should raise MeasurementTypeError"""
        with self.assertRaises(parser.MeasurementTypeError):
            parser.parse({})

if __name__ == "__main__":
    unittest.main()