import sqlite3
import csv
import psycopg2

from os.path import expanduser
from teleceptor.models import Calibration, DataStream, Sensor, MessageQueue, Message, Session, User, SensorReading, Path
from teleceptor.sessionManager import sessionScope

#  TODO
tables = ['', '', '', '', '', 'session', 'user', 'sensorreading']

sqconn = sqlite3.connect('base_station.db')
sqcursor = sqconn.cursor()

with sessionScope() as session:

    # calibration
    sqcursor.execute("select * from calibration;")
    for i in sqcursor:
        print i
        new = Calibration(id=i[0], sensor_id=i[1], timestamp=i[2], user=i[3], coefficients=i[4])
        session.add(new)
        session.commit()

    # messagequeue
    sqcursor.execute("select * from messagequeue;")
    for i in sqcursor:
        print i
        new = MessageQueue(id=i[0], messages=i[1], sensor_id=i[2])
        session.add(new)
        session.commit()

    # This was created because there were messages and sensor requiring a queue but it didnt exist in the previous data base.
    try:
        session.add(MessageQueue(id=1))
        session.commit()
    except:
        print "an error occured"

    # message
    sqcursor.execute("select * from message;")
    for i in sqcursor:
        print i
        new = Message(id=i[0], message=i[1], message_queue_id=i[2], timeout=i[3], read=bool(i[4]))
        session.add(new)
        session.commit()

    # sensor
    sqcursor.execute("select * from sensor;")
    for i in sqcursor:
        print i
        new = Sensor(
            uuid=i[0], sensor_IOtype=bool(i[1]), sensor_type=i[2], last_value=i[3],
            name=i[4], units=i[5], model=[6], description=i[7], last_calibration_id=i[8],
            message_queue_id=i[9], _meta_data=i[10])
        session.add(new)
        session.commit()

    # create default path

    # datastream
    print "streams:"
    sqcursor.execute("select * from datastream;")
    for i in sqcursor:
        print i
        new = DataStream(id=i[0], sensor=i[1], owner=i[2], min_value=i[3], max_value=i[4], name=i[1], description=[6])

        session.add(new)
        session.commit()
        new = Path(datastream_id=i[0], path="/newSensor")
        session.add(new)
        session.commit()

    # session
    sqcursor.execute("select * from session;")
    for i in sqcursor:
        print i
        new = Session(id=i[0], key=i[1], expiration=i[2], user=i[3])
        session.add(new)
        session.commit()

    # user
    sqcursor.execute("select * from user;")
    for i in sqcursor:
        print i
        new = User(id=i[0], email=i[1], firstname=i[2], lastname=i[3], active=i[4], password=i[5])
        session.add(new)
        session.commit()

    # sensorreading
    sqcursor.execute("select * from sensorreading;")
    counter = 0
    for i in sqcursor:
        # print i
        new = SensorReading(id=i[0], datastream=i[1], sensor=i[2], value=i[3], timestamp=i[4])
        # print "id: {}, datastream: {}, semsor: {}, value: {}, timestamp: {}".format(i[0], i[1], i[2], i[3], i[4])
        session.add(new)
        counter += 1
        if counter % 10000 == 0:
            print "commiting: {}".format(counter)
            session.commit()
