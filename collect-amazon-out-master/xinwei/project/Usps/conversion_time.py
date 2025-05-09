import re
import datetime


def conversion_time(time_str):
    """type November19,2022,12:57pm transform to type 2022-12-19 12:57:00"""
    month_dict = {"January": 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7,
                  'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
    time_data = time_str.split(',')
    month_and_day = time_data[0]
    year = int(time_data[1])
    try:
        hour_minute = time_data[2]
    except:
        hour_minute = None
    if hour_minute:
        month = month_dict[re.search('(\w+?)\d', month_and_day).group(1)]
        day = int(re.search('\w+?(\d+)', month_and_day).group(1))
        hour = int(re.search('(.*?):', hour_minute).group(1))
        minute = int(re.search(':(\d+)\w', hour_minute).group(1))
        am_or_pm = re.search('\d+:\d+(\w+)', hour_minute).group(1)
        if am_or_pm == 'pm' and hour != 12:
            hour += 12
        times = datetime.datetime(year, month, day, hour, minute, 00).strftime("%Y-%m-%d %H:%M:%S")
        return times
    else:
        month = month_dict[re.search('(\w+?)\d', month_and_day).group(1)]
        day = int(re.search('\w+?(\d+)', month_and_day).group(1))
        hour = 0
        minute = 0

        times = datetime.datetime(year, month, day, hour, minute, 00).strftime("%Y-%m-%d %H:%M:%S")
        return times


