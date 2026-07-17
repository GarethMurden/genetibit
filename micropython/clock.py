from machine import I2C, Pin
import time
import urtc


# Initialize RTC connected to I2C via Qwiic connector
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
rtc = urtc.DS1307(i2c)

class Clock():
    def __init__(self):
        pass

    def set_time(self, year, month, day, hour, minute, second):
        initial_time = time.mktime((
            year,
            month,
            day,
            hour,
            minute,
            second,
            0,      # millisecond
            0       # nanosecond?
        ))
        initial_time = urtc.seconds2tuple(initial_time)
        rtc.datetime(initial_time)

    def zero_pad(self, original):
        if len(str(original)) < 2:
            return f'0{original}'
        else:
            return str(original)

    def get_time(self):
        current_datetime = rtc.datetime()
        return f'{self.zero_pad(current_datetime.hour)}:{self.zero_pad(current_datetime.minute)}:{self.zero_pad(current_datetime.second)}'

    def get_date(self):
        current_datetime = rtc.datetime()
        return f'{current_datetime.year}-{self.zero_pad(current_datetime.month)}-{self.zero_pad(current_datetime.day)}'

    def get_datetime(self):
        current_datetime = rtc.datetime()
        return f'{current_datetime.year}-{self.zero_pad(current_datetime.month)}-{self.zero_pad(current_datetime.day)} {self.zero_pad(current_datetime.hour)}:{self.zero_pad(current_datetime.minute)}:{self.zero_pad(current_datetime.second)}'

    def is_in_the_past(self, time_string):
        if time_string is None or time_string == '':
            return True
        else:
            now = self.get_datetime()
            return now > time_string

    def get_seconds_from_now(self, seconds):
        current_seconds = urtc.tuple2seconds(rtc.datetime())
        new_time = urtc.seconds2tuple(current_seconds + seconds)
        return f'{new_time.year}-{self.zero_pad(new_time.month)}-{self.zero_pad(new_time.day)} {self.zero_pad(new_time.hour)}:{self.zero_pad(new_time.minute)}:{self.zero_pad(new_time.second)}'

    def get_seconds_until(self, target_time):
        target_year = int(target_time.split('-')[0])
        target_month = int(target_time.split('-')[1])
        target_day = int(target_time.split('-')[-1].split(' ')[0])
        target_hour = int(target_time.split(' ')[1].split(':')[0])
        target_minute = int(target_time.split(' ')[1].split(':')[1])
        target_second = int(target_time.split(' ')[1].split(':')[-1])
        target_seconds = time.mktime((
            target_year,
            target_month,
            target_day,
            target_hour,
            target_minute,
            target_second,
            0,      # ?
            0       # ?
        ))
        current_seconds = urtc.tuple2seconds(rtc.datetime())
        if target_second > current_seconds:
            in_the_future = True
        else:
            in_the_future = False
        return in_the_future, target_seconds - current_seconds

def main():
    clock = Clock()
    print(f'The current time is {clock.get_datetime()}')
    print(f'30 seconds from now it will be {clock.get_seconds_from_now(30)}')
    if clock.is_in_the_past('2026-01-01 09:00:00'):
        print('2026-01-01 09:00:00 is in the past')
    if not clock.is_in_the_past('2060-01-01 09:00:00'):
        print('2060-01-01 09:00:00 is in the future')
    in_the_future, seconds_away = clock.get_seconds_until('2026-07-17 15:30:00')
    print(f'2026-07-17 15:30 is in {seconds_away} seconds')

main()
