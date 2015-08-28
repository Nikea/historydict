from setuptools import setup
import history

setup(name='history',
      version=history.__version__,
      author='Brookhaven National Laboratory',
      py_modules=['history'],
      description='A persistent dictionary with history backed by sqlite',
      url='http://github.com/Nikea/history',
      platforms='Cross platform (Linux, Mac OSX, Windows)',
      install_requires=['six']
      )
