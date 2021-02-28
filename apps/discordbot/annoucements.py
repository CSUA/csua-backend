import datetime
from apps.db_data.models import Event

_MONTHNAMES = [None, 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
               'September', 'October', 'November', 'December']


def posixtime_to_str(posix_time):
    """Takes a posixtime and returns its representation in the following format:
    <Month Name> <Day> <Ordinal Suffix>, <Optional Year>. 
    Year 0 does not exist so it is used to indicate a date with no definite year.
    """
    dt = datetime.datetime.utcfromtimestamp(posix_time)
    suffix = 'th'
    if dt.day % 10 == 1:
        suffix = 'st'
    elif dt.day % 10 == 2:
        suffix = 'nd'
    elif dt.day % 10 == 3:
        suffix = 'rd'

    date_string = f"{_MONTHNAMES[dt.month]} {dt.day}{suffix}"

    # Only nonzero years are displayed
    if dt.year:
        date_string = f"{date_string}, {dt.year}"

    return date_string

# An implementation of current DST (Daylight Savings Time) rules for major US time zones 2007 and later.
# Adapted from: https://docs.python.org/3/library/datetime.html#datetime.tzinfo


ZERO = datetime.timedelta(0)
HOUR = datetime.timedelta(hours=1)
SECOND = datetime.timedelta(seconds=1)


def first_sunday_on_or_after(dt):
    """Finds the first sunday on or after a specific datetime.
    """
    days_to_go = 6 - dt.weekday()
    if days_to_go:
        dt += datetime.timedelta(days_to_go)
    return dt


def us_dst_range(year):
    """ Returns start and end times for US DST on a given year after 2006.
    ---------------------------------------------------------------------
    US DST Rules
    This is a simplified (i.e., wrong for a few cases) set of rules for US
    DST start and end times. For a complete and up-to-date set of DST rules
    and timezone definitions, visit the Olson Database (or try pytz):
    http://www.twinsun.com/tz/tz-link.htm
    http://sourceforge.net/projects/pytz/ (might not be up-to-date)
    In the US, since 2007, DST starts at 2am (standard time) on the second
    Sunday in March, which is the first Sunday on or after Mar 8.
    and ends at 2am (DST time) on the first Sunday of Nov.
    """
    start = first_sunday_on_or_after(
        datetime.datetime(1, 3, 8, 2).replace(year=year))
    end = first_sunday_on_or_after(
        datetime.datetime(1, 11, 1, 2).replace(year=year))
    return start, end


class USTimeZone(datetime.tzinfo):
    """A Class representing a USTimeZone, complete with DST. Inherits from datetime.tzinfo.
    """

    def __init__(self, hours):
        self.stdoffset = datetime.timedelta(hours=hours)

    def utcoffset(self, dt):
        return self.stdoffset + self.dst(dt)

    def dst(self, dt):
        """Calculates the timezone offset due to DST. Overriden from the tzinfo interface.
        """
        assert dt is not None and dt.tzinfo is self, "Invalid Datetime Object"
        start, end = us_dst_range(dt.year)
        # Can't compare naive to aware objects, so strip the timezone from
        # dt first.
        dt = dt.replace(tzinfo=None)
        if start + HOUR <= dt < end - HOUR:
            # DST is in effect.
            return HOUR
        if end - HOUR <= dt < end:
            # Fold (an ambiguous hour): use dt.fold to disambiguate.
            return ZERO if dt.fold else HOUR
        if start <= dt < start + HOUR:
            # Gap (a non-existent hour): reverse the fold rule.
            return HOUR if dt.fold else ZERO
        # DST is off.
        return ZERO

    def fromutc(self, dt):
        """Overriding the fromutc function in tzinfo.
        """
        assert dt.tzinfo is self
        start, end = us_dst_range(dt.year)
        start = start.replace(tzinfo=self)
        end = end.replace(tzinfo=self)
        std_time = dt + self.stdoffset
        dst_time = std_time + HOUR
        if end <= dst_time < end + HOUR:
            # Repeated hour
            return std_time.replace(fold=1)
        if std_time < start or dst_time >= end:
            # Standard time
            return std_time
        if start <= std_time < end - HOUR:
            # Daylight savings time
            return dst_time

def event_checker():
    """
    Checks events in db to see if any match the day
    """
    today = datetime.date.today()
    events = Event.objects.filter(date=today).order_by("time")
    return events
