from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import re
import sys

"""
DEVELOPMENT SETUP

This will get the necessary environment setup to use the source of ZeexApp. 
This will be complied into an executeable though and distributed so normal users 
probably wouldn't want to install this way unless.
"""

here = os.path.abspath(os.path.dirname(__file__))

version_file = open(os.path.join(here, 'zeex', '__init__.py'), 'rU')
__version__ = re.sub(
    r".*\b__version__\s+=\s+'([^']+)'.*",
    r'\1',
    [line.strip() for line in version_file if '__version__' in line].pop(0)
)
version_file.close()


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

short_description = """A Python GUI studio for data analysis."""

try:
    long_description = read('README.md')
except:
    long_description = "See README.md where installed"


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

tests_require = ['easygui', 'pandas >= 0.17.1', 'PySide', 'pytest',
                            'pytest-cov', 'pytest-qt', 'python-magic==0.4.6']
setup(
    name='zeex',
    version=__version__,
    url='https://github.com/zbarge/zeex',
    license='GPL',
    namespace_packages=['zeex'],
    author='Zeke Barge',
    tests_require=tests_require,
    install_requires=['PySide','easygui', 'pandas>=0.17.1', 'pytest',
                      'pytest-qt>=1.2.2', 'pytest-cov', 'python-magic>=0.4.6',
                      'openpyxl','xlrd','sqlalchemy'],
                      
    cmdclass={'test': PyTest},
    author_email='zekebarge@gmail.com',
    description=short_description,
    long_description=long_description,
    include_package_data=True,
    packages=['zeex'],

    platforms='any',
    test_suite='tests',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPL',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces'
        ],
    extras_require={
        'testing': tests_require,
    }
)
