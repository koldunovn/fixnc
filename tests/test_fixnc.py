import pytest
import fixnc as fnc
from netCDF4 import Dataset
from collections import OrderedDict
import os
import numpy as np

fl2 = Dataset('./tests/test.nc')
nc = fnc.ncfile(fl2)


def test_repr():
    assert len(nc.__repr__()) > 0
    assert nc.__repr__().startswith('File')

def test_ncfile():
    fl2_dims = OrderedDict([(u'X', ''), (u'Y', ''), (u'T', '')])
    fl2_variables = OrderedDict([(u'T', ''), (u'mytemp', '')])
    assert nc.dims.keys() == fl2_dims.keys()
    assert nc.variab.keys() == fl2_variables.keys()

def test_rename_dim():
    fl2_dims = OrderedDict([(u'lon', ''), (u'Y', ''), (u'time', '')])
    nc.rename_dim('X','lon')
    nc.rename_dim('T','time',)
    assert nc.dims.keys() == fl2_dims.keys()
    assert nc.variab['mytemp']['dimensions'] == (u'time', 'lon', u'Y')

def test_rename_dim2():
    fl2_dims = OrderedDict([(u'lon', ''), (u'lat', ''), (u'time', '')])
    nc.rename_dim('Y','lat', renameall=False)
    assert nc.dims.keys() == fl2_dims.keys()
    assert nc.variab['mytemp']['dimensions'] == (u'time', 'lon', u'Y')

def test_rename_dim_invar():
    nc.rename_dim_invar('mytemp','Y','lat')
    assert nc.variab['mytemp']['dimensions'] == (u'time', 'lon', u'lat')

def test_rename_var():
    fl2_variables = OrderedDict([(u'time', ''), (u'temp', '')])
    nc.rename_var('T','time')
    nc.rename_var('mytemp', 'temp')
    assert nc.variab.keys() == fl2_variables.keys()

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

def test_add_var():
    fl2_variables = OrderedDict([(u'time', ''), (u'temp', ''), (u'newvar', '')])
    data = np.zeros((5,10,10))
    newvar = fnc.create_variable(data,('time','lon','lat'), True, data.dtype, -1, OrderedDict([('name','zeros')]))
    nc.add_var('newvar', newvar)
    assert nc.variab.keys() == fl2_variables.keys()

def test_change_dtype():
    nc.change_dtype('newvar', np.dtype('int16'))
    assert nc.variab['newvar']['datatype'] == np.dtype('int16')

def test_save():
    fl2_variables = OrderedDict([(u'time', ''), (u'temp', ''), (u'newvar', '')])
    fl2_dimensions = OrderedDict([(u'lon', ''), (u'lat', ''), (u'time', '')])
    try:
        os.remove('./tests/out.nc')
    except OSError:
        pass
    nc.save('./tests/out.nc')
    fl2 = Dataset('./tests/out.nc', mode='r')
    assert fl2.variables.keys() == fl2_variables.keys()
    assert fl2.dimensions.keys() == fl2_dimensions.keys()
    assert len(fl2.dimensions['lon']) == 10
    assert len(fl2.dimensions['time']) == 5

