from typing import List, NamedTuple
import sched
import time
import datetime
import random


def round_date_time_to_hour(date_time: datetime.datetime) -> datetime.datetime:
    """Round date_time to hour.

    For example, round "2021-12-04 19:58:21.453642" to "2021-12-04 19:00:00".

    Args:
        date_time (datetime.datetime): datetime to be rounded.

    Returns:
        datetime.datetime: datetime rounded.
    """

    # Not entirely sure if this can always do the rounding correctly.
    # rounded_date_time = datetime.datetime(
    #     year=date_time.year,
    #     month=date_time.month,
    #     day=date_time.day,
    #     hour=date_time.hour,
    #     minute=0,
    #     second=0,
    #     microsecond=0,
    #     tzinfo=date_time.tzinfo,
    # )

    # However, this can.
    time_tuple = date_time.timetuple()
    rounded_time_tuple = time.struct_time((
        time_tuple.tm_year,
        time_tuple.tm_mon,
        time_tuple.tm_mday,
        time_tuple.tm_hour,
        0,  # tm_min
        0,  # tm_sec
        time_tuple.tm_wday,
        time_tuple.tm_yday,
        time_tuple.tm_isdst,
    ))

    rounded_date_time = datetime.datetime.fromtimestamp(
        time.mktime(rounded_time_tuple))

    return rounded_date_time


def create_date_time_after_n_hours(date_time: datetime.datetime,
                                   n: int) -> datetime.datetime:
    """Create the datetime after n hours comparing to the input datetime.

    For example, round "2021-12-04 23:00:00" to "2021-12-05 00:00:00".

    Args:
        date_time (datetime.datetime): The input datetime.
        n (int): The number of hours.

    Returns:
        datetime.datetime: The datetime n hours after the the input datetime.
    """

    date_time_delta = datetime.timedelta(hours=n)
    date_time_n_hours_later = date_time + date_time_delta

    return date_time_n_hours_later


def run_every_one_rounded_hour_everyday() -> None:
    """Schedule to run action every one rounded hour for everyday.

    For example, now the time is 14:32, the actions are scheduled to run
    on everyday at 15:00, 16:00, 17:00, ...
    """

    action_period = 1  # hour
    fruits = ["apple", "banana", "cherry"]

    scheduler = sched.scheduler(time.time, time.sleep)

    now_date_time = datetime.datetime.now()
    rounded_date_time = round_date_time_to_hour(date_time=now_date_time)
    # The first action might not run at the rounded time.
    # scheduled_date_time = rounded_date_time
    # If we want to run the first action at the rounded time,
    # the following date_time has to be used for the first scheduled time.
    scheduled_date_time = create_date_time_after_n_hours(
        date_time=rounded_date_time, n=action_period)

    # Loop forever.
    while True:
        t = time.mktime(scheduled_date_time.timetuple())
        scheduler.enterabs(time=t,
                           priority=1,
                           action=eat_fruit,
                           argument=(),
                           kwargs={
                               "fruit": random.choice(fruits),
                           })
        print(f"Scheduled action to run at {scheduled_date_time}.")
        scheduler.run()
        print(f"The action to run at {scheduled_date_time} was completed at "
              f"{datetime.datetime.now()}.")
        # Prepare the time for the next action.
        scheduled_date_time = create_date_time_after_n_hours(
            date_time=scheduled_date_time, n=action_period)


class ScheduledTime(NamedTuple):

    hour: int
    minute: int
    second: int


def run_at_fixed_time_everyday(scheduled_times: List[ScheduledTime]) -> None:
    """Schedule to run action at fixed time everyday.

    For example, the actions are scheduled to run on everyday 
    at 07:00, 12:00, 15:00.

    Args:
        scheduled_times (List[ScheduledTime]): A list of the scheduled time.
    """

    fruits = ["apple", "banana", "cherry"]

    scheduler = sched.scheduler(time.time, time.sleep)

    def create_scheduled_date_times(
            year: int, month: int, day: int,
            scheduled_times: List[ScheduledTime]) -> List[datetime.datetime]:

        scheduled_date_times = []
        for scheduled_time in scheduled_times:
            date_time = datetime.datetime(
                year=year,
                month=month,
                day=day,
                hour=scheduled_time.hour,
                minute=scheduled_time.minute,
                second=scheduled_time.second,
                microsecond=0,
            )
            scheduled_date_times.append(date_time)

        return scheduled_date_times

    now_date_time = datetime.datetime.now()
    scheduled_date_times = create_scheduled_date_times(
        year=now_date_time.year,
        month=now_date_time.month,
        day=now_date_time.day,
        scheduled_times=scheduled_times)

    # Loop forever.
    while True:
        for scheduled_date_time in scheduled_date_times:
            if scheduled_date_time > datetime.datetime.now():
                t = time.mktime(scheduled_date_time.timetuple())
                scheduler.enterabs(time=t,
                                   priority=1,
                                   action=eat_fruit,
                                   argument=(),
                                   kwargs={
                                       "fruit": random.choice(fruits),
                                   })
                print(f"Scheduled action to run at {scheduled_date_time}.")

        scheduler.run()
        print(f"Scheduled actions completed.")

        tomorrow_scheduled_date_times = [
            create_date_time_after_n_hours(date_time=scheduled_date_time, n=24)
            for scheduled_date_time in scheduled_date_times
        ]
        scheduled_date_times = tomorrow_scheduled_date_times


def eat_fruit(fruit: str) -> None:

    print(f"Eating {fruit} at {datetime.datetime.now()}.")


if __name__ == "__main__":

    # The functionality of run_every_one_rounded_hour_everyday
    # could be also be achieved by run_at_fixed_time_everyday.
    # run_every_one_rounded_hour_everyday()

    now_date_time = datetime.datetime.now()
    planned_date_time = now_date_time + datetime.timedelta(minutes=1)

    scheduled_time_1 = ScheduledTime(hour=planned_date_time.hour,
                                     minute=planned_date_time.minute,
                                     second=0)

    scheduled_times = [scheduled_time_1]

    run_at_fixed_time_everyday(scheduled_times=scheduled_times)