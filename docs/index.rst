fix netCDF files
================

**fixnc** helps to change meta information of the netCDF files. You can easilly add, delete and rename dimentions, variables and attributes.

Quick start:
------------
In the *tests* directory you will find a netCDF file *test.nc*, that have *X*, *Y* and *T* dimentions.::

	netcdf test {
	dimensions:
		X = 10 ;
		Y = 10 ;
		T = UNLIMITED ; // (5 currently)
	variables:
		float T(T) ;
			T:unuts = "hours since 2001-01-01 00:00:00" ;
		float mytemp(T, X, Y) ;
			mytemp:longname = "Temperature" ;
			mytemp:shortname = "temp" ;
	}

We would like to change the names of this dimentions to lon lat and time::

    import fixnc as fnc
    from netCDF4 import Dataset

    fl = Dataset('./tests/test.nc') # create netCDF4 instance
    nc = fnc.ncfile(fl)             # create ncfile instance, that is just a collection
                                    # of ordered dictionaries.
    # rename dimentions
    nc.rename_dim('X','lon')    
    nc.rename_dim('Y','lat')
    nc.rename_dim('T','time',)
    
    # save output
    nc.save('out.nc')

This should generate a new netCDF file (*out.nc*), that have exactly the same content as the original one, but with dimention names changed.::

	netcdf out {
	dimensions:
		lon = 10 ;
		lat = 10 ;
		time = UNLIMITED ; // (5 currently)
	variables:
		float T(time) ;
			T:unuts = "hours since 2001-01-01 00:00:00" ;
		float mytemp(time, lon, lat) ;
			mytemp:longname = "Temperature" ;
			mytemp:shortname = "temp" ;
	}


In this case dimention names in the variables will be also changed.

To add an attribute to T variable you simply::

    nc.add_attr('T','standard_name', 'time')

Documentation
-------------

.. toctree::
   :maxdepth: 3
   
   installation
   tutorial
   api







Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

