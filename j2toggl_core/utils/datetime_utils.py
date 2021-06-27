#!/usr/bin/env python3


from datetime import datetime, date
import pytz
import tzlocal


def get_now_with_timezone():
    utc_now = datetime.utcnow()
    local_zone = tzlocal.get_localzone()
    local_now = utc_now.replace(tzinfo=pytz.utc).astimezone(local_zone)

    return local_now


def shrink_time(dt: datetime):
    result = datetime(year=dt.year, month=dt.month, day=dt.day, tzinfo=dt.tzinfo)
    return result


def date2datetime(d: date):
    local_zone = tzlocal.get_localzone()
    result = datetime(year=d.year, month=d.month, day=d.day, tzinfo=local_zone)
    return result
