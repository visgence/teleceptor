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

#!/usr/bin/env python
import os,glob
from setuptools import setup,find_packages

#Get version from version file
exec(open(os.path.join('teleceptor','version.py')).read())


datadir = os.path.join('webroot')
datafiles = [(d, [os.path.join(d, f) for f in files]) for d,folders,files in os.walk(datadir)]
datafiles.append(('whisperData',[os.path.join('whisperData','blank.txt')]))
datafiles.append(('database',[os.path.join('database','blank.txt')]))
datafiles.append(('defaults.json'))

#for d in datafiles:
#    print d

setup(
    name='teleceptor',
    scripts = ["teleceptorcmd"],
    version=__version__,
    install_requires = ['sqlalchemy','cherrypy','requests','whisper','pySerial','jinja2'],
    zip_safe=False,
    platforms='any',
    url='https://github.com/visgence/teleceptor',
    download_url='https://github.com/visgence/teleceptor/tarball/' + __version__,
    license='GPL3',
    author='Visgnece Inc.',
    author_email='info@visgence.com',
    description='Data collection web application for microcontrollers',
    include_package_data=True,
    data_files = datafiles,
    packages=find_packages())

