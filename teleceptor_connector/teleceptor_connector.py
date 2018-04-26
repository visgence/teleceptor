import requests
import json
import math
import time
from datetime import datetime, timedelta
import pandas as pd
from pandas import DataFrame, Series


class Teleceptor(object):
    """
    Provides an interface to a teleceptor instance.
    """

    SENSORSPATH = "api/sensors/"
    DATASTREAMSPATH = "api/datastreams/"
    READINGSPATH = "api/readings/"
    DATASOURCES = ["SQL", "ElasticSearch"]

    def __init__(self, teleceptor_uri):
        self.teleceptor_uri = teleceptor_uri
        if not teleceptor_uri.endswith("/"):
            self.teleceptor_uri += "/"

    def list_sensors(self):
        """
        Returns the uuids of all available sensors.
        """

        try:
            response = requests.get(self.teleceptor_uri + self.SENSORSPATH)
            sensors = response.json()['sensors']
        except Exception as e:
            print("An exception occured when getting sensor list: {}".format(e))
            raise e
        else:
            return [sensor['uuid'] for sensor in sensors]

    def fetch(self, *sensor_uuid, **kwargs):
        """
        Returns the scaled readings for `sensor_uuid` between `start` and `end`, using data source `source`.

        Args:
            sensor_uuid (list[str]): The uuids of the sensors to fetch readings for
            start optional(datetime): The start time to fetch from. Defaults to 1 hour before `end`.
            end optional(datetime): The end time to fetch until. Default to now.
            source optional(str): One of the options defined in Teleceptor.DATASOURCES. Defines the datasource to fetch from.

        Returns:
            Dataframe: A pandas DataFrame if len(sensor_uuids) > 1 with index as timestamp and columns as the scaled data for each sensor in sensor_uuids.
            Vector: A pandas Vector if len(sensor_uuids) == 1 with index as timestamp and column as the scaled data for sensor_uuid.

        Raises:
            ValueError - if there are no sensor_uuids.
        """

        if len(sensor_uuid) == 0:
            raise ValueError("fetch requires as least one uuid.")

        end = kwargs.get('end', datetime.now())
        start = kwargs.get('start', end - timedelta(hours=1))
        assert start < end

        source = kwargs.get('source', "SQL")
        assert source in self.DATASOURCES

        print("Getting data from {} to {} with source {}".format(start, end, source))

        readings = []

        for sensor in sensor_uuid:
            # make request for datastream before getting readings
            datastream_response = requests.get(self.teleceptor_uri + self.DATASTREAMSPATH + "?sensor={}".format(sensor))
            assert datastream_response.status_code == requests.codes.ok
            datastream_id = datastream_response.json()['datastreams'][0]['id']

            # now get readings
            readings_request = self.teleceptor_uri + self.READINGSPATH + "?datastream={}&source={}&start={}&end={}".format(
                datastream_id, source, int(time.mktime(start.timetuple())), int(time.mktime(end.timetuple())))
            print(readings_request)
            readings_response = requests.get(readings_request)
            if readings_response.status_code != requests.codes.ok:
                print(readings_response)
                print(readings_response.text)
                return None

            # get the scaling function for this sensor
            sensor_response = requests.get(self.teleceptor_uri + self.SENSORSPATH + "{}/".format(sensor))
            assert sensor_response.status_code == requests.codes.ok

            scaling_function = sensor_response.json()['sensor']['last_calibration']['coefficients']

            scaled_readings = readings_response.json()['readings']
            for i in range(len(scaled_readings)):
                scaled_reading = 0
                for index, coefficient in enumerate(scaling_function):
                    scaled_reading += (math.pow(scaled_readings[i][1], len(scaling_function) - index - 1) * coefficient)
                scaled_readings[i][1] = scaled_reading

            readings.append(scaled_readings)

        # currently readings is in the form [  [  [timestamp, value], [timestamp, value], ... ], [  [timestamp, value], ...], ...  ]
        # But to pass to a dataframe, we need to turn each sensor's data into a Series
        series = []
        for idx, reading in enumerate(readings):
            series.append(Series([value[1] for value in reading], index=[datetime.fromtimestamp(timestamp[0]) for timestamp in reading], name=sensor_uuid[idx]))

        return pd.concat(series, axis=1)


if __name__ == "__main__":
    tc = Teleceptor("http://deserttest.visgence.com")
    print(tc.list_sensors())
    df_es = tc.fetch('particle_1temp', 'mfi_mfi01temp', source="ElasticSearch", start=datetime.fromtimestamp(1462122000))
    df_sql = tc.fetch('particle_1temp', 'mfi_mfi01temp', source="SQL", start=datetime.fromtimestamp(1462122000))
    print("Elasticsearch: \n{}\nSQL:\n{}".format(df_es, df_sql))
    df_sql.plot()
