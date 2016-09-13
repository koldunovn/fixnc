fixnc's documentation
=====================

This package makes changing the meta information of the netCDF file easy. You can add, delete and rename dimentions, variables and attributes.

Quick start:
============
This will show some basic usage. In the tests directory you will find a netCDF file, that have X, Y and T dimentions.
We would like to change the names of this dimentions to lon lat and time::

    import fixnc as fnc
    from netCDF4 import Dataset

    fl = Dataset('./tests/test.nc')
    nc = fnc.ncfile(fl)

    nc.rename_dim('X','lon')
    nc.rename_dim('Y','lat')
    nc.rename_dim('T','time',)

    nc.save('out.nc')

This should generate a new netCDF file, that have exactly the same content as the original one, but with dimention names changed. In this case dimention names in the variables will be also changed.

To add an attribute to T variable you simply::

    nc.add_attr('T','standard_name', 'time')




.. toctree::
   :maxdepth: 2


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

