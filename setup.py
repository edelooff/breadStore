"""breadStore Web API installation script."""

import os
from setuptools import setup, find_packages


REQUIREMENTS = [
    'mysql-python',
    'pyramid',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'sqlalchemy',
    'transaction',
    'waitress',
    'zope.sqlalchemy',
]


def readme():
  with file(os.path.join(os.path.dirname(__file__), 'README.md')) as f_readme:
    return f_readme.read()


setup(
    name='breadstore',
    version='0.1',
    description='breadStore RESTful Web API',
    long_description=readme(),
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='',
    url='https://github.com/edelooff/breadStore',
    keywords='web wsgi bfg pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': 'initdb_breadstore = breadstore.scripts.initdb:main',
        'paste.app_factory': 'main = breadstore:main',
    }
)
