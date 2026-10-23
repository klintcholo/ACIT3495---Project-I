
import unittest

from analytics import calculate_statistics


class TestCalculateStatistics(unittest.TestCase):

    def test_calculates_statistics(self):
        result = calculate_statistics([70, 80, 90, 100])

        self.assertEqual(result["count"], 4)
        self.assertEqual(result["minimum"], 70)
        self.assertEqual(result["maximum"], 100)
        self.assertEqual(result["average"], 85)

    def test_handles_empty_grades(self):
        result = calculate_statistics([])

        self.assertEqual(result["count"], 0)
        self.assertIsNone(result["minimum"])
        self.assertIsNone(result["maximum"])
        self.assertIsNone(result["average"])

    def test_handles_one_grade(self):
        result = calculate_statistics([75])

        self.assertEqual(result["count"], 1)
        self.assertEqual(result["minimum"], 75)
        self.assertEqual(result["maximum"], 75)
        self.assertEqual(result["average"], 75)


if __name__ == "__main__":
    unittest.main()

