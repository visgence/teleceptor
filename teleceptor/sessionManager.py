"""
    (c) 2014 Visgence, Inc.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

# System Imports
import teleceptor
import models
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


@contextmanager
def sessionScope():
    """Provide a transactional scope around a series of operations."""

    db = create_engine(engine)
    models.Base.metadata.create_all(db, checkfirst=True)
    Session = sessionmaker(bind=db)
    session = Session()

    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
