"""
Defines high level functions for retrieving Teleceptor aggregation levels.

Authors: Victor Szczepanski

"""

from sys import maxsize

"""Defines the aggregation levels used by Teleceptor.
 The form is (period_start, period_end): aggregation_value.
 So, if some value v is between period_start and period_end, aggregation_value should be used.
 Does not admit negative values or values > sys.maxsize
 """

hour = 3600
day = hour * 24
week = day * 7
month = week * 4
year = month * 12
aggregation_levels = {
    (0, hour): 10,          # 0 to an hour       - 10 seconds
    (hour, week): 60,       # hour to a week     - 1 minute
    (week, month): 60 * 10,   # week to a month    - 10 minutes
    (month, year): hour,    # month to a year    - an hour
    (year, maxsize): day    # longer than a year - a day
}


def getAggregationLevel(start, end):
    """
    Get the appropriate aggregation level for the time period `start` - `end`.

    .. note::
        Uses the aggregation_levels dictionary for lookup. We assume the keys
        in aggregation_levels are non-overlapping - undefined behaviour may occur if this is not true.

    :params start: The start time in seconds.
    :type start: int
    :param end: The end time in seconds.
    :type end: int

    :returns: int -- The number of seconds to aggregate on.
    """
    period = end - start
    for (period_start, period_end), aggregation_level in aggregation_levels.items():
        if period >= period_start and period < period_end:
            return aggregation_level
    raise LookupError("Period {} is out of aggregation range.".format(period))


def getElasticSearchAggregationLevel(start, end):
    """
    Get the appropriate aggregation level for the time period `start` - `end`, in EalsticSearch format.

    This function will return the aggregation period in the lowest common division possible.
    For example, if the aggregation period requested is > 60 seconds but < 1 hour, this function will
    return the aggregation in minutes, rather than seconds or hours.

    Example:
        time_frame = getElasticSearchAggregationLevel(0,3 * 3600 + 1)
        assert(time_frame is "1m")
        time_frame = getElasticSearchAggregationLevel(0,120*60 + 1)
        assert(time_frame is "10s")

    :params start: The start time in seconds.
    :type start: int
    :param end: The end time in seconds.
    :type end: int

    :returns: str -- The aggregation period in ElasticSearch format, in the lowest common division.
    """
    aggregation_period = getAggregationLevel(start, end)
    aggregation_string = "10m"
    if aggregation_period < 60:
        return "{}s".format(int(aggregation_period))
    if aggregation_period < hour:
        # One hour
        return "{}m".format(int(aggregation_period / 60.0))
    if aggregation_period < day:
        # One day
        return "{}h".format(int(aggregation_period / hour))
    return "{}d".format(int(aggregation_period / day))


if __name__ == "__main__":
    # Some basic usage examples
    start1 = 0
    end1 = 60
    end2 = 121
    end3 = 60 * 60 * 24 + 60
    print("Aggregation period given start = {} and end = {}".format(start1, end1))
    print(getAggregationLevel(start1, end1))
    print("Aggregation period given start = {} and end = {}".format(start1, end2))
    print(getAggregationLevel(start1, end2))
    print("Aggregation period given start = {} and end = {}".format(start1, end3))
    print(getAggregationLevel(start1, end3))

    print("ElasticSearch Aggregation period given start = {} and end = {}".format(start1, end1))
    print(getElasticSearchAggregationLevel(start1, end1))
    print("ElasticSearch Aggregation period given start = {} and end = {}".format(start1, end2))
    print(getElasticSearchAggregationLevel(start1, end2))
    print("ElasticSearch Aggregation period given start = {} and end = {}".format(start1, end3))
    print(getElasticSearchAggregationLevel(start1, end3))
