# fixnc
fix netCDF header


This package make changing the header of the netCDF file easy. You can add, delete and rename dimentions, variables and attributes.

## Motivation:

Many people and programs still do not follow CF convention. Wrong attributes or variable names will break your work flow. It is difficult to rename or add attributes in existing files using netCDF4 python library. This is a wrapper around netCDF4 that allows quick change of your netCDF header.

## Requirements:

netCDF4 https://github.com/Unidata/netcdf4-python

sh https://github.com/amoffat/sh

## Basic usage:

Let't open some netCDF file with netCDF4:


```python
from netCDF4 import Dataset
```

```python
fl2 = Dataset('test.nc')
```

And create ncfile instance:


```python
from fixnc import ncfile
nc = ncfile(fl2)
```

Here is how the header of the netCDF file will look like:
```python
nc
```




    File format: NETCDF4
    Dimentions: X(10), Y(10), T(5)
    variables:
    	 float32 T(T)
    	   unuts:hours since 2001-01-01 00:00:00
    	 float32 mytemp(T, X, Y)
    	   longname:Temperature
    	   shortname:temp




We would like to rename dimentions, update variable names and add some attributes. The netCDF header is represented as set of Ordered dictionaries. For example here are our dims:


```python
nc.dims
```




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



We can change the names of dimentions with 'rename_dim' method:


```python
nc.rename_dim('X','lon')
nc.rename_dim('Y','lat')
nc.rename_dim('T','time',)
```


```python
nc
```




    File format: NETCDF4
    Dimentions: lon(10), lat(10), time(5)
    variables:
    	 float32 T(time)
    	   unuts:hours since 2001-01-01 00:00:00
    	 float32 mytemp(time, lon, lat)
    	   longname:Temperature
    	   shortname:temp




Note, that names of the dimentions in the description of the variables are also changed. You can change this behaviour by setting `renameall=False`. 

Now rename variables:


```python
nc.rename_var('T','time')
nc.rename_var('mytemp', 'temp')
```


```python
nc
```




    File format: NETCDF4
    Dimentions: lon(10), lat(10), time(5)
    variables:
    	 float32 time(time)
    	   unuts:hours since 2001-01-01 00:00:00
    	 float32 temp(time, lon, lat)
    	   longname:Temperature
    	   shortname:temp




Note that unit attribute for time is wrong, let's fix it:


```python
nc.rename_attr('time','unuts','units')
nc
```




    File format: NETCDF4
    Dimentions: lon(10), lat(10), time(5)
    variables:
    	 float32 time(time)
    	   units:hours since 2001-01-01 00:00:00
    	 float32 temp(time, lon, lat)
    	   longname:Temperature
    	   shortname:temp




Add a bit more information about time by providing additional attributes:


```python
nc.add_attr('time','standard_name', 'time')
nc.add_attr('time','calendar','proleptic_gregorian')
nc
```




    File format: NETCDF4
    Dimentions: lon(10), lat(10), time(5)
    variables:
    	 float32 time(time)
    	   units:hours since 2001-01-01 00:00:00
    	   standard_name:time
    	   calendar:proleptic_gregorian
    	 float32 temp(time, lon, lat)
    	   longname:Temperature
    	   shortname:temp




And add some glabal attribute as well:


```python
nc.add_gattr('history','fixed with fixnc')
```


```python
nc
```




    File format: NETCDF4
    Dimentions: lon(10), lat(10), time(5)
    variables:
    	 float32 time(time)
    	   units:hours since 2001-01-01 00:00:00
    	   standard_name:time
    	   calendar:proleptic_gregorian
    	 float32 temp(time, lon, lat)
    	   longname:Temperature
    	   shortname:temp
    
    	 history:fixed with fixnc



Now we can save the results:


```python
nc.save('out.nc')
```

And compare once again the original and the resulting files:


```python
!ncdump -h test.nc
```

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



```python
!ncdump -h out.nc
```

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
