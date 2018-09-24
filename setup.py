from setuptools import setup

VERSION = '0.0.1'
QUALIFIER = ''


DISTNAME = 'fixnc'
LICENSE = 'MIT'
AUTHOR = 'Nikolay Koldunov'
AUTHOR_EMAIL = 'koldunovn@gmail.com'
URL = 'https://github.com/koldunovn/fixnc/'
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Intended Audience :: Science/Research',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Topic :: Scientific/Engineering',
]

INSTALL_REQUIRES = ['netcdf4 >= 1.1.8']
TESTS_REQUIRE = ['pytest >= 2.7.1']

DESCRIPTION = "Easy edit of netCDF files."
LONG_DESCRIPTION = """
This package makes changing the meta information of the netCDF file easy. 
You can add, delete and rename dimentions, variables and attributes.

What it does
------------

* renames dimentions, variables and attributes in netCDF files.
* changes values of variables and attributes.
* adds dimentions, variables and attributes.
* removes attributes.
* reorders dimentions and variables.

Important links
---------------
- HTML documentation: https://fixnc.readthedocs.io/
- Source code: https://github.com/koldunovn/fixnc/

"""


setup(name=DISTNAME,
      version=VERSION,
      license=LICENSE,
      author=AUTHOR,
      author_email=AUTHOR_EMAIL,
      classifiers=CLASSIFIERS,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      install_requires=INSTALL_REQUIRES,
      tests_require=TESTS_REQUIRE,
      url=URL,
      packages=['fixnc'],
      include_package_data=True,
      zip_safe=False)
      
      
