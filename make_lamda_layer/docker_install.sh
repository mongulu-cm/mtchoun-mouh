#!/bin/bash
virtualenv --python=/usr/bin/python3.8 python #Python is the name of de layer
soure python/bin/active
pip install -r requirements.txt -t python/lib/python3.8/site-pakages

zip -r9 python.zip python
