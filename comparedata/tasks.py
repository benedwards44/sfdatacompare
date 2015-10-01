from __future__ import absolute_import
from celery import Celery
import os
import json	
import ast
import requests
import datetime
import time
import sys
import sqlite3
import StringIO
import glob
import traceback

# Celery config
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sfdatacompare.settings')
app = Celery('tasks', broker=os.environ.get('REDIS_URL', 'redis://localhost'))


reload(sys)
sys.setdefaultencoding("utf-8")

