"""
SessionManager.py.

Authors: Victor Szczepanski

"""

# System Imports
import teleceptor
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL

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
    if teleceptor.isTesting:
        db = create_engine(testEngine)
    else:
        db = create_engine(engine)
    Session = sessionmaker(bind=db)
    session = Session()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def createSession():
    db = create_engine(engine)
    Session = sessionmaker(bind=db)
    session = Session()
    return session
