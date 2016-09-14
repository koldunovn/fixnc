Basic Tutorial
--------------
Let't open some netCDF file with netCDF4. We will use *test.nc* located in *tests* directory ::


    In [1]: from netCDF4 import Dataset
    In [2]: fl = Dataset('./tests/test.nc')


And create ncfile instance::


	In [3]: from fixnc import ncfile
	In [4]: nc = ncfile(fl)


Here is how the header of the netCDF file will look like::
    
	In [5]: nc
	Out[5]:
	File format: NETCDF4
	Dimentions: X(10), Y(10), T(5)
	variables:
		 float32 T(T)
		   unuts: hours since 2001-01-01 00:00:00
		 float32 mytemp(T, X, Y)
		   longname: Temperature
		   shortname: temp

We would like to rename dimentions, update variable names and add some attributes. The netCDF header is represented as set of Ordered dictionaries. For example here are our dimentions::

	In [6]: nc.dims
	Out[6]:
	OrderedDict([(u'X',
	              OrderedDict([('name', u'X'),
	                           ('size', 10),
	                           ('isunlimited', False)])),
	             (u'Y',
	              OrderedDict([('name', u'Y'),
	                           ('size', 10),
	                           ('isunlimited', False)])),
	             (u'T',
	              OrderedDict([('name', u'T'),
	                           ('size', 5),
	                           ('isunlimited', True)]))])


We can change the names of dimentions with **rename_dim** method::


	In [7]: nc.rename_dim('X','lon')
	   ...: nc.rename_dim('Y','lat')
	   ...: nc.rename_dim('T','time',)
	   ...: nc
	   ...:
	Out[7]:
	File format: NETCDF4
	Dimentions: lon(10), lat(10), time(5)
	variables:
		 float32 T(time)
		   unuts: hours since 2001-01-01 00:00:00
		 float32 mytemp(time, lon, lat)
		   longname: Temperature
		   shortname: temp




Note, that names of the dimentions in the description of the variables are also changed. You can change this behaviour by setting *renameall=False*. 

Now rename variables::


	In [8]: nc.rename_var('T','time')
	   ...: nc.rename_var('mytemp', 'temp')
	   ...: nc
	   ...:
	Out[8]:
	File format: NETCDF4
	Dimentions: lon(10), lat(10), time(5)
	variables:
		 float32 time(time)
		   unuts: hours since 2001-01-01 00:00:00
		 float32 temp(time, lon, lat)
		   longname: Temperature
		   shortname: temp




Note that unit attribute for time is wrong, let's fix it::


	In [9]: nc.rename_attr('time','unuts','units')
	   ...: nc
	   ...:
	Out[9]:
	File format: NETCDF4
	Dimentions: lon(10), lat(10), time(5)
	variables:
		 float32 time(time)
		   units: hours since 2001-01-01 00:00:00
		 float32 temp(time, lon, lat)
		   longname: Temperature
		   shortname: temp




Add a bit more information about time by providing additional attributes::

	In [10]: nc.add_attr('time','standard_name', 'time')
	    ...: nc.add_attr('time','calendar','proleptic_gregorian')
	    ...: nc
	    ...:
	Out[10]:
	File format: NETCDF4
	Dimentions: lon(10), lat(10), time(5)
	variables:
		 float32 time(time)
		   units: hours since 2001-01-01 00:00:00
		   standard_name: time
		   calendar: proleptic_gregorian
		 float32 temp(time, lon, lat)
		   longname: Temperature
		   shortname: temp




And add some global attribute as well::


	In [11]: nc.add_gattr('history','fixed with fixnc')
	    ...: nc
	    ...:
	Out[11]:
	File format: NETCDF4
	Dimentions: lon(10), lat(10), time(5)
	variables:
		 float32 time(time)
		   units: hours since 2001-01-01 00:00:00
		   standard_name: time
		   calendar: proleptic_gregorian
		 float32 temp(time, lon, lat)
		   longname: Temperature
		   shortname: temp

		 history:fixed with fixnc



Now we can save the result::


	In [12]: nc.save('out.nc')

And compare once again the original and the resulting files::


	In [14]: !ncdump -h ./tests/test.nc
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

::

	In [15]: !ncdump -h ./out.nc
	netcdf out {
	dimensions:
		lon = 10 ;
		lat = 10 ;
		time = UNLIMITED ; // (5 currently)
	variables:
		float time(time) ;
			time:units = "hours since 2001-01-01 00:00:00" ;
			time:standard_name = "time" ;
			time:calendar = "proleptic_gregorian" ;
		float temp(time, lon, lat) ;
			temp:longname = "Temperature" ;
			temp:shortname = "temp" ;

	// global attributes:
			:history = "fixed with fixnc" ;
	}

