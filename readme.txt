SECTION 1 : LIBRARY INSTALLATION:

You need to install basemap library and GEOS library to run the application as showed in the following steps:

0) Install pre-requisite python modules numpy and matplotlib.

1) Then download basemap-X.Y.Z.tar.gz (approx 100 mb) from
the sourceforge download site, unpack and cd to basemap-X.Y.Z.

2) Install the GEOS library.  If you already have it on your
system, just set the environment variable GEOS_DIR to point to the location 
of libgeos_c and geos_c.h (if libgeos_c is in /usr/local/lib and
geos_c.h is in /usr/local/include, set GEOS_DIR to /usr/local).
Then go to step (3).  If you don't have it, you can build it from
the source code included with basemap by following these steps:

 > cd geos-3.3.3
 > export GEOS_DIR=<where you want the libs and headers to go>
   A reasonable choice on a Unix-like system is /usr/local, or
   if you don't have permission to write there, your home directory.
 > ./configure --prefix=$GEOS_DIR 
 > make; make install

3) cd back to the top level basemap directory (basemap-X.Y.Z) and
run the usual 'python setup.py install'.  Check your installation
by running "from mpl_toolkits.basemap import Basemap" at the python
prompt.

SECTION 2: HOW TO USE THIS APPLICATION

The frontend is a light website using Django framework. The user could get access to the fontend as follows:

1) The user may cd to the directory named vote under the cs122-project directory, and run the command: python manage.py runserver.

2) The user may type the address http://127.0.0.1:8000 in a browser, the main page should show up. 

3) The user may choose one of the two links on the main page to explore the search function and predict funtion respectively. 

4) The user may enter ctrl-c to quit the application. 
