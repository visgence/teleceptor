import unittest

from teleceptor.timeAggregationUtils import getElasticSearchAggregationLevel, getAggregationLevel

minute = 60
hour = minute * 60
day = hour * 24
week = day * 7
month = week * 4
year = month * 12

class sqlAggregationTests(unittest.TestCase):
    def test_to_hour(self):
        res = getAggregationLevel(0, hour - 1)
        self.assertEqual(res, 10)

    def test_to_day(self):
        res = getAggregationLevel(0, day - 1)
        self.assertEqual(res, minute)

    def test_to_week(self):
        res = getAggregationLevel(0, week - 1)
        self.assertEqual(res, minute)

    def test_to_month(self):
        res = getAggregationLevel(0, month - 1)
        self.assertEqual(res, minute * 10)

    def test_to_year(self):
        res = getAggregationLevel(0, year - 1)
        self.assertEqual(res, hour)

    def test_over_year(self):
        res = getAggregationLevel(0, year + 1)
        self.assertEqual(res, day)

class elasticAggregationTests(unittest.TestCase):
    def test_to_hour(self):
        res = getElasticSearchAggregationLevel(0, hour - 1)
        self.assertEqual(res, '10s')

    def test_to_day(self):
        res = getElasticSearchAggregationLevel(0, day - 1)
        self.assertEqual(res, '1m')

    def test_to_week(self):
        res = getElasticSearchAggregationLevel(0, week - 1)
        self.assertEqual(res, '1m')

    def test_to_month(self):
        res = getElasticSearchAggregationLevel(0, month - 1)
        self.assertEqual(res, '10m')

    def test_to_year(self):
        res = getElasticSearchAggregationLevel(0, year - 1)
        self.assertEqual(res, '1h')

    def test_over_year(self):
        res = getElasticSearchAggregationLevel(0, year + 1)
        self.assertEqual(res, '1d')

if __name__ == "__main__":
    unittest.main()
