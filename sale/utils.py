import pytz
import datetime
from random import randrange

def convert_str_to_datetime(date_str):
    date_strs = date_str.split('-')
    year      = int(date_strs[0])
    month     = int(date_strs[1])
    day       = int(date_strs[2])
    return datetime.datetime(year, month, day, 0, 0, 0, 0, pytz.UTC)