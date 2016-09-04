import pytest
import fixnc as fnc
from netCDF4 import Dataset

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
    assert nc.dims.keys() == ['lon', u'Y', u'T']
    assert nc.variab['mytemp']['dimentions'] == (u'T', 'lon', u'Y')
    #return nc

def test_rename_dim2():
    #nc.rename_dim('X','lon')
    nc.rename_dim('Y','lat',  renameall=False)
    assert nc.dims.keys() == ['lon', u'lat', u'T']
    assert nc.variab['mytemp']['dimentions'] == (u'T', 'lon', u'Y')



