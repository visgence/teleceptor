import json
import requests
import time
import sys

import pytz
from datetime import datetime
import dateutil.parser as dp

from teleceptor.models import DataStream, Sensor, SensorReading
from teleceptor.sessionManager import sessionScope

tz = pytz.timezone('America/Denver')


def init():
    try:
        with open('weatherconfig.json') as data_file:
            config = json.load(data_file)
    except:
        print "no config file found!"
        return
    with sessionScope() as session:
        queryObjs = []
        for i in config['stations']:
            endTime = datetime.fromtimestamp(time.time(), tz).isoformat()
            startTime = datetime.fromtimestamp(time.time()-1000, tz).isoformat()
            url = "?command=DataQuery&uri={}&format=json&mode=most-recent&p1=1&p2= ".format(config['baseurl'], i)
            print "querying {}".format(i)
            data = requests.get(url).json()
            print "finding all database entries"

            for j in data['head']['fields']:
                try:
                    sensor = session.query(Sensor.uuid).filter(Sensor.uuid == "{}-{}".format(i, j['name'])).one()
                    print "{} sensor already in database.".format("{}-{}".format(i, j['name']))
                except Exception, e:
                    print "adding new sensor"
                    Uuid = "{}-{}".format(i, j['name'])
                    print Uuid
                    desc = "process: {}\nsettable: {}\ntype: {}".format(j['process'], j['settable'], j['type'])
                    sensor = Sensor(uuid=Uuid, units=j['units'], description=desc, name="{}-{}".format(i, j['name']))
                    session.add(sensor)
                    session.commit()

                try:
                    datastream = session.query(DataStream.name).filter(DataStream.name == "{}-{}".format(i, j['name'])).one()
                    print "{} datastream already in database".format("{}-{}".format(i, j['name']))
                except Exception, e:
                    print" Adding new Datastream"
                    datastream = DataStream(sensor="{}-{}".format(i, j['name']), name="{}-{}".format(i, j['name']))
                    session.add(datastream)
                    session.commit()


def update():
    try:
        with open('campbellconfig.json') as data_file:
            config = json.load(data_file)
    except:
        print "no config file found!"
        return
    with sessionScope() as session:
        for i in config['stations']:
            datastreams = session.query(DataStream).filter(DataStream.name.contains(i))
            if len(datastreams.all()) == 0:
                print "you must run with the '--init' argument first to start getting streams from: {}".format(i)
                continue
            lastReadings = session.query(SensorReading).filter(SensorReading.datastream == datastreams[0].id).all()
            lastDate = 0
            if len(lastReadings) == 0:
                lastDate = time.time()-24*60*60
            for k in lastReadings:
                if k.toDict()['timestamp'] > lastDate:
                    lastDate = k.toDict()['timestamp']
            print "last update was: {}".format(lastDate)
            if time.time() - lastDate < 60*60*15:
                print "skipping update for {} because its last update was less than 15 minutes ago.".format(i)
                continue
            lastDate = datetime.fromtimestamp(lastDate, tz).isoformat()
            endDate = datetime.fromtimestamp(time.time(), tz).isoformat()
            url = "{}?command=DataQuery&uri={}&format=json&mode=date-range&p1={}&p2={}".format(config['baseurl']i, lastDate, endDate)
            newData = requests.get(url).json()
            for a in datastreams:
                for b in range(0, len(newData['head']['fields']) - 1):
                    if a.toDict()['name'] == "{}-{}".format(i, newData['head']['fields'][b]['name']):
                        sensor = session.query(Sensor).filter(Sensor.uuid == "{}-{}".format(i, newData['head']['fields'][b]['name'])).one()
                        for c in newData['data']:
                            newReading = SensorReading(
                                    datastream=a.toDict()['id'], sensor=sensor.toDict()['uuid'],
                                    timestamp=dp.parse(c['time']).strftime('%s'), value=c['vals'][b])
                            session.add(newReading)
        session.commit()


if "__main__" == __name__:
    if len(sys.argv) > 1:
        if sys.argv[1] == "--init":
            print "Checking for new sensors."
            init()
        else:
            print "invalid argument"
    else:
        print "updating"
        update()
