import time
import urtc
from machine import I2C, Pin

days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Initialize RTC (connected to I2C)
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
rtc = urtc.DS1307(i2c)


def set_time():
	initial_time = (
		2026,	# year
		7, 		# month
		1,		# day
		14,		# hour
		15, 	# minute
		0, 		# second
		0,		# millisecond
		0 		# nanosecond (?)
	)
	initial_time_seconds = time.mktime(initial_time)
	initial_time = urtc.seconds2tuple(initial_time_seconds)
	rtc.datetime(initial_time)

# set_time()

while True:
    current_datetime = rtc.datetime()
    print('Current date and time:')
    print('Year:', current_datetime.year)
    print('Month:', current_datetime.month)
    print('Day:', current_datetime.day)
    print('Hour:', current_datetime.hour)
    print('Minute:', current_datetime.minute)
    print('Second:', current_datetime.second)
    print('Day of the Week:', days_of_week[current_datetime.weekday])

    time.sleep(1)