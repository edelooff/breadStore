# breadStore

An open rewrite of the customer management for a Dutch food bank


## Installing and running Pyramid development server

```bash
virtualenv env
source env/bin/activate
python setup.py develop
initdb_breadstore development.ini
pserve development.ini --reload
```