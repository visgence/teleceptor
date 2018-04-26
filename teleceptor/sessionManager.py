"""
SessionManager.py.

Authors: Victor Szczepanski

"""

# System Imports
import teleceptor
from contextlib import contextmanager
from sqlalchemy import create_engine
import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from teleceptor import USE_DEBUG

session_maker = None

if USE_DEBUG:
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(format='%(levelname)s:%(asctime)s %(message)s', level=logging.INFO)

if teleceptor.USEPG:
    dboptions = {}
    dboptions['drivername'] = 'postgres'
    dboptions['host'] = teleceptor.PGSQLDBHOST
    dboptions['port'] = teleceptor.PGSQLDBPORT
    dboptions['username'] = teleceptor.PGSQLDBUSERNAME
    dboptions['password'] = teleceptor.PASSWORD
    dboptions['database'] = teleceptor.PGSQLDBNAME
    engine = URL(**dboptions)
else:
    engine = "sqlite:///" + teleceptor.DBFILE

testEngine = "sqlite:///" + teleceptor.TESTDBFILE


@contextmanager
def sessionScope():
    """Provide a transactional scope around a series of operations."""

    session = createSession()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_pg_session_maker():
    if teleceptor.isTesting:
        db = create_engine(testEngine)
    else:
        db = create_engine(engine)
    Session = sessionmaker(bind=db)
    return Session


def createSession():
    global session_maker
    if session_maker is None:
        logging.debug("Creating new session maker.")
        session_maker = create_pg_session_maker()
    return session_maker()
