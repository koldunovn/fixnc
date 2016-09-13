import numpy as np
from netCDF4 import Dataset

import sh
from collections import OrderedDict
import pickle

def create_variable(data, dimentions, hasunlimdim=False, datatype='float32', FillValue=None,
                    attributes=OrderedDict()):
    '''
    Create  dictionary that contain information nessesary for creation of the
    netCDF variable.
    INPUT:
        data:
                numpy array, or object that can return numpy array with []
                syntax

        dimentions:
                tuple with dimention names, like ('time', 'lat', 'lon').
                Dimentions should exist in the source file, or should be added
                in the ncfile object.

        hasunlimdim:
                True if variable have unlimited dimention, otherwise False.
                !!NOTE!! At present unlimited dimention in your new variable has
                to be the same size as in the original data (e.g. number of time steps).
                This should be changed.

        datatype:
                numpy datatype as a string, like "float32"

        FillValue:
                If it exist, otherwise None

        attributes:
                Orderd dict with attributes and their values.

    '''
    vvar = OrderedDict([('data',data),
                        ('dimentions',dimentions),
                        ('hasunlimdim',hasunlimdim),
                        ('datatype',np.dtype(datatype)),
                        ('FillValue',FillValue),
                        ('attributes',attributes)])
    return vvar

def dump_variable(var, filename):
    outfile = open(filename, 'wb')
    pickle.dump(var, outfile)
    outfile.close()

def load_variable(filename):
    ifile = open(filename, 'r')
    var = pickle.load(ifile)
    ifile.close()
    return var

def reorder(odict, neworder):
    '''
    Reorder Ordered Dictionary according to the list of keys provided in
    neworder.
    '''
    if len(odict) != len(neworder):
        raise ValueError('Number of elemnts in the dictionary and in the new order have to be equal')
    for key in neworder:
        if key not in odict:
            raise ValueError('Key {} from neworder is not in the dictionary'.format(key))

    ordered = OrderedDict()
    for key in neworder:
        ordered[key] = odict[key]
    return ordered

class ncfile(object):
    '''
    Th class is initiated with original netCDF file object
    created by Dataset from netCDF4 package. The properties of the file
    are copied to the attributes of the class and cna be then saved together
    with data of the original file. The purpose is to be able to fix
    description of the netCDF file, like dimention names, attributes and so on,
    but to save the rest of the structure of the original file as much as
    possible.
    Initial version of the class is based on the code from here
    https://github.com/Unidata/netcdf4-python/blob/master/netCDF4/utils.py

    '''

    def __init__(self, ifile):

        self.ifile = ifile
        self.nchunk = 10
        self.istop = -1
        self.nchunk = 10
        self.istart = 0
        self.istop = -1

        # Read dimentions
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
            variab[varname]['dimentions']= ncvar.dimensions
            hasunlimdim = False
            # Check if dimention is unlimited
            for vdim in variab[varname]['dimentions']:
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

        self.variab = variab

        #Set global attributes
        gattrs_names = self.ifile.ncattrs()
        
        gattrs = OrderedDict()
        for gatt in gattrs_names:
            gattrs[gatt] = getattr(self.ifile,gatt)
            #setattr(ncfile4, gatt, getattr(self.ifile,gatt))
        self.gattrs = gattrs
        
    def add_dim(self, name, size, isunlimited=False):
        '''
        Add dimention to the list of dimentions already copied from the file.
        '''
        self.dims[name] = OrderedDict()
        self.dims[name]['name'] = name
        self.dims[name]['size'] = size
        self.dims[name]['isunlimited'] = isunlimited

    def rename_dim(self, oldname, newname, renameall = True):
        '''
        Rename dimention. If renameall is True, rename coresponding
        dimntions in the variables as well.
        '''
        newdim = OrderedDict((newname if k == oldname else k, v) for k, v in
                             self.dims.viewitems())
        newdim[newname]['name'] = newname
        self.dims = newdim
        if renameall:
            for var in self.variab:
                self.rename_dim_invar(var, oldname, newname)

    def rename_dim_invar(self, var, oldname, newname):
        '''
        Rename dimention in the variable.
        '''
        vardims = self.variab[var]['dimentions']
        if oldname in vardims:
                    #print 'find old name'
            tempdim = list(vardims)
            for i in range(len(tempdim)):
                if tempdim[i] == oldname:
                    tempdim[i] = newname
            
            self.variab[var]['dimentions'] = tuple(tempdim)

    def rename_attr(self, var, oldname, newname):
        '''
        Renames the attribute, but the value of the attribute stays the same.
        '''
        newattr = OrderedDict((newname if k == oldname else k, v) for k, v in
                             self.variab[var]['attributes'].viewitems())
        self.variab[var]['attributes'] = newattr

    def rename_gattr(self, oldname, newname):
        '''
        Renames the global attribute, but the value of the attribute stays the same.
        '''
        newattr = OrderedDict((newname if k == oldname else k, v) for k, v in
                             self.gattrs.viewitems())
        self.gattrs = newattr

    def change_attr(self, var, attrname, newvalue):
        '''
        Change the value of the attribute in specified variable
        '''
        if self.variab[var]['attributes'].has_key(attrname):
            self.variab[var]['attributes'][attrname] = newvalue
        else:
            raise ValueError('there is no attribute with name {} in variable {}'.format(attrname, var))
    def change_gattr(self, attrname, newvalue):
        '''
        Change the value of the global attribute in specified variable
        '''
        if self.gattrs.has_key(attrname):
            self.gattrs[attrname] = newvalue
        else:
            raise ValueError('there is no global attribute with name {}'.format(attrname))


    def rename_var(self, oldname, newname):
        '''
        Rename variable.
        '''
        if self.variab.has_key(oldname):
            newvar = OrderedDict((newname if k == oldname else k, v) for k, v in
                             self.variab.viewitems())
            self.variab = newvar
        else:
            raise ValueError('there is no variable with name {}'.format(oldname))

    def add_attr(self, var, attr, value):
        '''
        Adds attribute to specified variable
        '''
        self.variab[var]['attributes'][attr] = value

    def add_gattr(self, attr, value):
        '''
        Adds global attribute to specified variable
        '''
        self.gattrs[attr] = value

    def dell_attr(self, var, attr):
        '''
        Delete attribute from the variable
        '''
        if self.variab[var]['attributes'].has_key(attr):
            del self.variab[var]['attributes'][attr]
        else:
            raise ValueError('there is no attribute with name {} in variable {} '.format(attr, var))

    def add_var(self, varname, var):
        '''
        Adds variable to the netCDF file (should be OrderedDict, prepared with 'create_variable' function).
        '''
        self.variab[varname] = var

    def reorder_dims(self, neworder):
        '''
        Reorder dimentions in the OrderedDict.
        '''
        ordered = reorder(self.dims, neworder)
        self.dims = ordered

    def reorder_vars(self, neworder):
        '''
        Reorder variables.
        '''
        ordered = reorder(self.variab, neworder)
        self.variab = ordered

    def change_data(self, var, data):
        '''
        Change data values in the variable. Should be exactly the same shape as original data.
        Data should be numpy array, or object that can return numpy array with []
        syntax
        '''
        self.variab[var]['data'] = data



    def save(self, fname):
        '''
        Create netCDF file from the ncfile object 
        '''

        try:
            sh.rm(fname)
        except:
            pass

        ncfile4 = Dataset(fname,'w',clobber=False,format='NETCDF4_CLASSIC')

        # Create dimentions
        for dim in self.dims.itervalues():
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
                                         perem['dimentions'], \
                                         fill_value=perem['FillValue'],\
                                         complevel=1)

            #attdict = perem['data'].__dict__
            #if '_FillValue' in attdict: del attdict['_FillValue']
            var.setncatts(perem['attributes'])

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
        sinfo.append('Dimentions: '+', '.join(sdims))

        svars = ['variables:\n']
        for key in self.variab:
            #print "\t {} {}".format(self.variab[key]['datatype'], key)
            svars.append("\t {} {}({})\n".format(self.variab[key]['datatype'],\
                                               key, \
                                               ', '.join(self.variab[key]['dimentions'])))
            for attr in self.variab[key]['attributes'].items():
                svars.append("\t   {}: {}\n".format(attr[0], attr[1]))
            if self.variab[key]['FillValue']:
                svars.append("\t   FillValue: {}\n".format(attr[0], str(self.variab[key]['FillValue'])))
        svars = ''.join(svars)
        sinfo.append(svars)
        sgattr = []
        for attr in self.gattrs:
            sgattr.append('\t {}:{}\n'.format(attr, self.gattrs[attr]))
        sgattr = ''.join(sgattr)
        sinfo.append(sgattr)
        return '\n'.join(sinfo)


