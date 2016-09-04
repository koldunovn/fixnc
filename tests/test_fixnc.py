import pytest
import fixnc as fnc
from netCDF4 import Dataset
from collections import OrderedDict
import os

fl2 = Dataset('./tests/test.nc')
nc = fnc.ncfile(fl2)


def test_repr():
    assert len(nc.__repr__()) > 0
    assert nc.__repr__().startswith('File')

def test_ncfile():
    assert nc.dims.keys() == [u'X', u'Y', u'T']
    assert nc.variab.keys() == [u'T', u'mytemp']

def test_rename_dim():
    nc.rename_dim('X','lon')
    nc.rename_dim('T','time',)
    assert nc.dims.keys() == ['lon', u'Y', u'time']
    assert nc.variab['mytemp']['dimentions'] == (u'time', 'lon', u'Y')
    #return nc

def test_rename_dim2():
    nc.rename_dim('Y','lat',  renameall=False)
    assert nc.dims.keys() == ['lon', u'lat', u'time']
    assert nc.variab['mytemp']['dimentions'] == (u'time', 'lon', u'Y')

def test_rename_dim_invar():
    nc.rename_dim_invar('mytemp','Y','lat')
    assert nc.variab['mytemp']['dimentions'] == (u'time', 'lon', u'lat')

def test_rename_var():

    nc.rename_var('T','time')
    nc.rename_var('mytemp', 'temp')

    assert nc.variab.keys() == ['time', 'temp']

def test_rename_attr():
    nc.rename_attr('time','unuts','units')
    assert nc.variab['time']['attributes'] == OrderedDict([('units', u'hours since 2001-01-01 00:00:00')])

def test_add_attr():

    nc.add_attr('time','standard_name', 'time')
    nc.add_attr('time','calendar','proleptic_gregorian')
    assert nc.variab['time']['attributes'] == OrderedDict([('units', u'hours since 2001-01-01 00:00:00'),
                                                           ('standard_name', 'time'),
                                                           ('calendar', 'proleptic_gregorian')])

def test_add_gattr():
    nc.add_gattr('history','fixed with fixnc')
    assert nc.gattrs == OrderedDict([('history', 'fixed with fixnc')])

def test_save():
    try:
        os.remove('./tests/out.nc')
    except OSError:
        pass
    nc.save('./tests/out.nc')
    fl2 = Dataset('./tests/out.nc', mode='r')
    assert fl2.variables.keys() == [u'time', u'temp']
    assert fl2.dimensions.keys() == [u'lon', u'lat', u'time']
    assert fl2.dimensions['lon'].size == 10
    assert fl2.dimensions['time'].size == 5

    



