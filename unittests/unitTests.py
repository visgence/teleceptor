import unittest
import os
import sys
PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PATH)
from test_timeAggregation import elasticAggregationTests, sqlAggregationTests

def suite():
    suite = unittest.TestSuite()
    suite.addTest(elasticAggregationTests('test_to_hour'))
    suite.addTest(elasticAggregationTests('test_to_day'))
    suite.addTest(elasticAggregationTests('test_to_week'))
    suite.addTest(elasticAggregationTests('test_to_month'))
    suite.addTest(elasticAggregationTests('test_to_year'))
    suite.addTest(elasticAggregationTests('test_over_year'))

    suite.addTest(sqlAggregationTests('test_to_hour'))
    suite.addTest(sqlAggregationTests('test_to_day'))
    suite.addTest(sqlAggregationTests('test_to_week'))
    suite.addTest(sqlAggregationTests('test_to_month'))
    suite.addTest(sqlAggregationTests('test_to_year'))
    suite.addTest(sqlAggregationTests('test_over_year'))
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
