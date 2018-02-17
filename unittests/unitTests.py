import unittest
import os
import sys
import logging
PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PATH)
# Path must be adjusted for unit tests to work as if they were a part of the
# Teleceptor module so we tell pep8 to ignore E402 with the #noqa flag.
from test_timeAggregation import elasticAggregationTests, sqlAggregationTests  # noqa


def suite():
    suite = unittest.TestSuite()

    print('Running tests for time aggregation utils.')
    suite.addTest(sqlAggregationTests('test_to_hour'))
    suite.addTest(sqlAggregationTests('test_to_day'))
    suite.addTest(sqlAggregationTests('test_to_week'))
    suite.addTest(sqlAggregationTests('test_to_month'))
    suite.addTest(sqlAggregationTests('test_to_year'))
    suite.addTest(sqlAggregationTests('test_over_year'))
    suite.addTest(elasticAggregationTests('test_to_hour'))
    suite.addTest(elasticAggregationTests('test_to_day'))
    suite.addTest(elasticAggregationTests('test_to_week'))
    suite.addTest(elasticAggregationTests('test_to_month'))
    suite.addTest(elasticAggregationTests('test_to_year'))
    suite.addTest(elasticAggregationTests('test_over_year'))

    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
