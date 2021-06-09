"""Unit-tests with python unittest. Please read the official documentation at
https://docs.python.org/3/library/unittest.html
"""
import json
import unittest

class TestParser(unittest.TestCase):
    def test_parse_aistin_mv(self):
        from dataforwarding import parser

        document = {}
        with open("test-assets/aistin-mv.json", "r") as file:
            document = json.load(file)

        parsed = parser.parse(document)
        self.assertIn("battery", parsed)
        self.assertIn("deveui", parsed)
        self.assertIn("humidity", parsed)
        self.assertIn("pressure", parsed)
        self.assertIn("rssi", parsed)
        self.assertIn("temperature", parsed)
        self.assertIn("timestamp_node", parsed)
        self.assertIn("timestamp_parser", parsed)
        print(parsed)

    def test_parse_nb100(self):
        from dataforwarding import parser

        document = {}
        with open("test-assets/nb100.json", "r") as file:
            document = json.load(file)

        parsed = parser.parse(document)
        self.assertEqual(parsed["battery"], 3.613)
        self.assertEqual(parsed["deveui"], "11000014")
        self.assertEqual(parsed["humidity"], 30)
        self.assertEqual(parsed["pressure"], 101601)
        self.assertEqual(parsed["rssi"], -75)
        self.assertEqual(parsed["temperature"], 26.9)
        self.assertEqual(parsed["timestamp_node"], 1623159476)
        self.assertIn("timestamp_parser", parsed)

    def test_parse_raise(self):
        from dataforwarding import parser

        with self.assertRaises(parser.MeasurementTypeError):
            parser.parse({})

if __name__ == "__main__":
    unittest.main()