"""Unit-tests with python unittest. Please read the official documentation at
https://docs.python.org/3/library/unittest.html
"""
import json
import unittest

class TestNB100(unittest.TestCase):
    def test_parse(self):
        from dataforwarding import nb100

        document = {}
        with open("test-assets/nb100.json", "r") as file:
            document = json.load(file)

        parsed = nb100.parse(document)
        self.assertEqual(parsed["battery"], 3.613)
        self.assertEqual(parsed["deveui"], "11000014")
        self.assertEqual(parsed["humidity"], 30)
        self.assertEqual(parsed["pressure"], 101601)
        self.assertEqual(parsed["rssi"], -75)
        self.assertEqual(parsed["temperature"], 26.9)
        self.assertEqual(parsed["timestamp_node"], 1623159476)
        self.assertIn("timestamp_parser", parsed)

if __name__ == "__main__":
    unittest.main()