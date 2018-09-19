import numpy as np
from netCDF4 import Dataset
from netCDF4 import stringtoarr

from collections import OrderedDict
import pickle

import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf8')
except:
    pass


def create_variable(data, dimensions, hasunlimdim=False, datatype='float32', FillValue=None,
                    attributes=OrderedDict()):
    '''Creates dictionary that can be added as a variable to the netCDF file.

    Create  dictionary that contains information necessary for creation of the
    netCDF variable.

    Parameters  
    ----------
    data : array-like
        Numpy array, array-like object that contains the actual data values.
    dimensions : tuple
        tuple with dimension names, like ('time', 'lat', 'lon').
        dimensions should exist in the source file, or should be added
        in the ncfile object.
    hasunlimdim : bool
         True if variable have unlimited dimension, otherwise False.
         !!NOTE!! At present unlimited dimension in your new variable has
         to be the same size as in the original data (e.g. number of time steps).
         This should be changed.
    datatype: datatype
        numpy datatype as a string, like "float32".
    FillValue: number, optional
        If your data should have one, otherwise None
    attributes: OrderedDict
        Orderd dictionary with attributes and their values.

    Returns
    -------
    OrderedDict
        Ordered dictionary that can be used to add data to netCDF file.
    '''
    vvar = OrderedDict([('data',data),
                        ('dimensions',dimensions),
                        ('hasunlimdim',hasunlimdim),
                        ('datatype',np.dtype(datatype)),
                        ('FillValue',FillValue),
                        ('attributes',attributes)])
    return vvar

def dump_variable(var, filename):
    '''Use `pickle` to dump OrderedDict to the file.

    Parameters
    ----------
    var : OrderedDict
        OrderedDict, supposedly produced by `create_variable` function.
    filename : str
        name of the file.

    Returns
    -------
    bool
        True is succes.
    '''
    outfile = open(filename, 'wb')
    pickle.dump(var, outfile)
    outfile.close()
    return True

def load_variable(filename):
    '''Use `pickle` load OrderedDict from the file to the variable.

    Parameters
    ----------
    filename : str
        name of the file.

    Returns
    -------
    OrderedDict

    '''
    ifile = open(filename, 'r')
    var = pickle.load(ifile)
    ifile.close()
    return var

def reorder(odict, neworder):
    '''Reorder values in the OrderedDict

    Reorder Ordered Dictionary according to the list of keys provided in
    neworder.

    Parameters
    ----------
    odict : OrderedDict

    neworder : list
        list with keys from the odict, positioned in the new order.

    Returns
    -------
    OrderedDict
        Ordered dictionary with key-value pairs reordered according to the `neworder`.
    '''
    if len(odict) != len(neworder):
        raise ValueError('Number of elements in the dictionary and in the new order have to be equal')
    for key in neworder:
        if key not in odict:
            raise ValueError('Key {} from neworder is not in the dictionary'.format(key))

    ordered = OrderedDict()
    for key in neworder:
        ordered[key] = odict[key]
    return ordered

class ncfile(object):
    '''Main class of the fixnc.

    This class is initiated with original netCDF file object
    created by Dataset from the netCDF4 package. The properties of the file
    are copied to the attributes of the class and cna be then saved together
    with data of the original file. The purpose is to be able to fix
    metadata in the netCDF file, like dimension names, attributes and so on,
    but to save the rest of the structure of the original file as much as
    possible.

    Initial version of the class is based on the code from netCDF4 library
    https://github.com/Unidata/netcdf4-python/blob/master/netCDF4/utils.py

    Parameters
    ----------
    ifile : Dataset
        Instance of the Dataset class from the netCDF4 library.

    '''

    def __init__(self, ifile):

        self.ifile = ifile
        self.nchunk = 10
        self.istop = -1
        self.nchunk = 10
        self.istart = 0
        self.istop = -1
        self.file_format = ifile.file_format

        # Read dimensions
        dims = OrderedDict()
        for dimname, dim in ifile.dimensions.items():
            dims[dimname] = OrderedDict()
            try:
                dims[dimname]['name'] = dim.name
            except:
                dims[dimname]['name'] = dimname

            dims[dimname]['size'] = len(dim)
            dims[dimname]['isunlimited'] = dim.isunlimited()

        self.dims = dims

        # Read variable names
        varnames = ifile.variables.keys()

        # I am not sure what this fix is for...
        for dimname in ifile.dimensions.keys():
            if dimname in ifile.variables.keys() and dimname not in varnames:
                    varnames.append(dimname)

        self.varnames = varnames

        # Collect variables
        variab = OrderedDict()
        for varname in varnames:
            variab[varname] = OrderedDict()
            ncvar = ifile.variables[varname]
            variab[varname]['data'] = ncvar
            variab[varname]['dimensions']= ncvar.dimensions
            hasunlimdim = False
            # Check if dimension is unlimited
            for vdim in variab[varname]['dimensions']:
                if ifile.dimensions[vdim].isunlimited():
                    hasunlimdim = True
                    variab[varname]['unlimdimname'] = vdim
            variab[varname]['hasunlimdim'] = hasunlimdim
            variab[varname]['datatype'] =  ncvar.dtype

            if hasattr(ncvar, '_FillValue'):
                variab[varname]['FillValue'] = ncvar._FillValue
            else:
                variab[varname]['FillValue'] = None

            attdict = ncvar.__dict__
            if '_FillValue' in attdict: del attdict['_FillValue']
            variab[varname]['attributes'] = attdict

            try:
                variab[varname]['zlib'] = ncvar.filters()['zlib']
            except:
                variab[varname]['zlib'] = False
            try:
                variab[varname]['complevel'] = ncvar.filters()['complevel']
            except:
                variab[varname]['complevel'] = 1

            if isinstance(ncvar.chunking(), list):
                variab[varname]['chunksizes'] = ncvar.chunking()
            else:
                variab[varname]['chunksizes'] = None

        self.variab = variab

        #Set global attributes
        gattrs_names = self.ifile.ncattrs()

        gattrs = OrderedDict()
        for gatt in gattrs_names:
            gattrs[gatt] = getattr(self.ifile,gatt)
            #setattr(ncfile4, gatt, getattr(self.ifile,gatt))
        self.gattrs = gattrs



    def rename_dim(self, oldname, newname, renameall = True):
        """Rename existing dimension.

        Parameters
        ----------
        oldname : str
            Name of existing dimension.
        newname : str
            New name for the dimension.
        renameall : bool
            If renameall is True, rename corresponding
            dimensions in the variables as well.

        """

        newdim = OrderedDict((newname if k == oldname else k, v) for k, v in
                             self.dims.items())
        newdim[newname]['name'] = newname
        self.dims = newdim
        if renameall:
            for var in self.variab:
                self.rename_dim_invar(var, oldname, newname)

    def rename_dim_invar(self, var, oldname, newname):
        """Rename dimension in the variable.

        Parameters
        ----------
        var : str
            Variable, that should have dimension with `oldname`.
        oldname : str
            Old name of the dimension.
        newname : str
            New name of the dimension.

        """
        vardims = self.variab[var]['dimensions']
        if oldname in vardims:
                    #print 'find old name'
            tempdim = list(vardims)
            for i in range(len(tempdim)):
                if tempdim[i] == oldname:
                    tempdim[i] = newname

            self.variab[var]['dimensions'] = tuple(tempdim)

    def rename_attr(self, var, oldname, newname):
        """Rename existing attribute of the variable.

        The value of the attribute stays the same.

        Parameters
        ----------
        var : str
            Variable, that should have an attribute with `oldname`.
        oldname : str
            Old name of the attribute.
        newname : str
            New name of the attribute.

        """

        newattr = OrderedDict((newname if k == oldname else k, v) for k, v in
                             self.variab[var]['attributes'].items())
        self.variab[var]['attributes'] = newattr

    def rename_gattr(self, oldname, newname):
        """Rename existing global attribute.

        The value of the attribute stays the same.

        Parameters
        ----------
        oldname : str
            Old name of the global attribute.
        newname : str
            New name of the global attribute.

        """

        newattr = OrderedDict((newname if k == oldname else k, v) for k, v in
                             self.gattrs.items())
        self.gattrs = newattr

    def change_attr(self, var, attrname, newvalue):
        '''Change the value of the attribute in specified variable.

        The name of the attribute stays the same.

        Parameters
        ----------
        var : str
            Variable, that should have an attribute with `attrname`.
        attrname : str
            Name of the attribute.
        newvalue : str
            New value of the attribute.
        '''
        if attrname in self.variab[var]['attributes']:
            self.variab[var]['attributes'][attrname] = newvalue
        else:
            raise ValueError('there is no attribute with name {} in variable {}'.format(attrname, var))

    def change_gattr(self, attrname, newvalue):
        '''Change the value of existing global attribute.

        The name of the global attribute stays the same.

        Parameters
        ----------
        attrname : str
            Name of the global attribute.
        newvalue : str
            New value of the global attribute.
        '''
        if attrname in self.gattrs:
            self.gattrs[attrname] = newvalue
        else:
            raise ValueError('there is no global attribute with name {}'.format(attrname))

    def change_data(self, var, data):
        '''Change data values in the existing variable.

        Should be exactly the same shape as original data.
        Data should be numpy array, or array-like object.

        Parameters
        ----------
        var : str
            Name of the variable.
        data : array-like
            Array with new data values of the variable.
            The size should be the same as for the original data.
        '''
        self.variab[var]['data'] = data

    def change_dtype(self, var, dtype):
        '''Change data type values in the existing variable.

        Should be exactly the same shape as original data.
        Data should be numpy array, or array-like object.

        Parameters
        ----------
        var : str
            Name of the variable.
        dtype : numpy dtype, e.g. npumpy.dtype('float16')
            Array with new data values of the variable.
            The size should be the same as for the original data.
        '''
        self.variab[var]['datatype'] = dtype

    def rename_var(self, oldname, newname):
        """Rename existing variable.

        Attributes, dimensions and data stays the same.

        Parameters
        ----------
        oldname : str
            Old name of the variable.
        newname : str
            New name of the variable.

        """
        if oldname in self.variab:
            newvar = OrderedDict((newname if k == oldname else k, v) for k, v in
                             self.variab.items())
            self.variab = newvar
        else:
            raise ValueError('there is no variable with name {}'.format(oldname))

    def add_dim(self, name, size, isunlimited=False):
        """Add dimension.

        Parameters
        ----------
        name : str
            Name of the dimension.
        size : int
            Size of the dimension.
        isunlimited : bool
            Flag to indicate if the dimension is unlimited or not.

        """

        self.dims[name] = OrderedDict()
        self.dims[name]['name'] = name
        self.dims[name]['size'] = size
        self.dims[name]['isunlimited'] = isunlimited

    def add_attr(self, var, attr, value):
        """Add attribute to the variable.

        Parameters
        ----------
        var : str
            Name of the variable.
        attr : str
            Name of the new attribute.
        value : str
            Value of the new attribute.

        """

        self.variab[var]['attributes'][attr] = value

    def add_gattr(self, attr, value):
        """Add global attribute.

        Parameters
        ----------
        attr : str
            Name of the new global attribute.
        value : str
            Value of the new global attribute.

        """
        self.gattrs[attr] = value

    def add_var(self, varname, var):
        """Add variable.

        Parameters
        ----------
        varname : str
            Name of the new variable.
        var : OrderedDict
            Should be OrderedDict, prepared with `create_variable` function.

        """
        self.variab[varname] = var

    def del_attr(self, var, attr):
        """Delete attribute from the variable.

        Parameters
        ----------
        var : str
            Name of the variable.
        attr : str
            Name of the attribute to delete.

        """
        if attr in self.variab[var]['attributes']:
            del self.variab[var]['attributes'][attr]
        else:
            raise ValueError('there is no attribute with name {} in variable {} '.format(attr, var))

    def del_var(self, var):
        """Delete variable.

        Parameters
        ----------
        var : str
            Name of the variable.
        
        """
        if self.variab[var]:
            del self.variab[var]
        else:
            raise ValueError('there is no variable with name {} '.format(var))


    def reorder_dims(self, neworder):
        """Reorder dimensions.

        Parameters
        ----------
        neworder : list
            List with dimension names, positioned in the desired order.

        """

        ordered = reorder(self.dims, neworder)
        self.dims = ordered

    def reorder_vars(self, neworder):
        """Reorder variables.

        Parameters
        ----------
        neworder : list
            List with name of the variables, positioned in the desired order.

        """
        ordered = reorder(self.variab, neworder)
        self.variab = ordered


    def save(self, fname, clobber=False):
        '''Save the file to the disk.

        Create netCDF file from the ncfile object.

        Parameters
        ----------
        fname : str
            File name.


        '''

        ncfile4 = Dataset(fname,'w',clobber=clobber,format=self.file_format)

        # Create dimensions
        for dim in self.dims.values():
            #print(dim)
            if dim["isunlimited"]:
                ncfile4.createDimension(dim['name'],None)
                if self.istop == -1: self.istop=dim['size']
            else:
                ncfile4.createDimension(dim['name'],dim['size'])

        # Loop over variables
        for vari in self.variab:
            #print vari
            perem  = self.variab[vari]

            var = ncfile4.createVariable(vari,
                                         perem['datatype'],
                                         perem['dimensions'],
                                         fill_value=perem['FillValue'],
                                         chunksizes=perem['chunksizes'],
                                         zlib=perem['zlib'],
                                         complevel=perem['complevel'])

            #attdict = perem['data'].__dict__
            #if '_FillValue' in attdict: del attdict['_FillValue']
            var.setncatts(perem['attributes'])

            # Zero size string variables are loaded as masked constants by netCDF4 (e.g. rotated_pole)
            # this workaround seems to solve the problem with not beeing able to
            # save this masked constant to netCDF4 variables
            # Error "Cannot set fill value of string with array of dtype "float64".
            if perem['datatype'].char in 'SU':
                if type(perem['data'][:]) == np.ma.core.MaskedConstant :
                    perem['data'] = stringtoarr('',0)

            if perem['hasunlimdim']: # has an unlim dim, loop over unlim dim index.
                # range to copy
                if self.nchunk:
                    start = self.istart; stop = self.istop; step = self.nchunk
                    if step < 1: step = 1
                    for n in range(start, stop, step):
                        nmax = n+step
                        if nmax > self.istop: nmax=self.istop
                        idata = perem['data'][n:nmax]
                        var[n-self.istart:nmax-self.istart] = idata
                else:
                    idata = perem['data'][:]
                    var[0:len(unlimdim)] = idata


            else: # no unlim dim or 1-d variable, just copy all data at once.
                if perem['data'].shape != ():
                    idata = perem['data'][:]
                    var[:] = idata
                else:
                    var[:] = perem['data']

            ncfile4.sync() # flush data to disk

        #gattrs = self.ifile.ncattrs()
        for gatt in self.gattrs:
            setattr(ncfile4, gatt, self.gattrs[gatt])


        ncfile4.close()

    def __repr__(self):
        '''
        Text representation of the ncfile object.
        '''
        sinfo = []
        sinfo.append('File format: '+ self.ifile.file_format)
        sdims = [name+'('+str(self.dims[name]['size'])+')' for name in self.dims ]
        sinfo.append('dimensions: '+', '.join(sdims))

        svars = ['variables:\n']
        for key in self.variab:
            #print "\t {} {}".format(self.variab[key]['datatype'], key)
            svars.append("\t {} {}({})\n".format(self.variab[key]['datatype'],\
                                               key, \
                                               ', '.join(self.variab[key]['dimensions'])))
            for attr in self.variab[key]['attributes'].items():
                svars.append("\t   {}: {}\n".format(attr[0], attr[1]))
            if self.variab[key]['FillValue']:
                svars.append("\t   FillValue: {}\n".format(attr[0], str(self.variab[key]['FillValue'])))
        svars = ''.join(svars)
        sinfo.append(svars)
        sgattr = []
        for attr in self.gattrs:
            print(attr)
            sgattr.append('\t {}:{}\n'.format(attr , self.gattrs[attr]))
        sgattr = ''.join(sgattr)
        sinfo.append(sgattr)
        print(sinfo)
        return '\n'.join(sinfo)


