import pendulum
from datetime import datetime
from datetime import timedelta
from pandas import date_range
from airflow.timetables.events import EventsTimetable
import pickle

class ScheduleCustom():

    def __init__(self, hours:list, 
                 description:str,
                 start_date:datetime, 
                 end_date=datetime(2024,12,31)) -> None:
        self.hours = hours
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        
        self.events_dates_list = self.__define_dates()

    def __define_dates(self):
        events_dates_list = []
        for days in date_range(self.start_date, self.end_date, freq='D'):
            for hour in self.hours:
                date = pendulum.datetime(
                    year=days.year,
                    month=days.month,
                    day=days.day,
                    hour=hour.hour,
                    minute=hour.minute,
                    second=hour.second,
                    tz='Europe/Lisbon'
                )
                events_dates_list.append(date)
        
        return events_dates_list

    def events_dates(self) -> EventsTimetable:
        timetable = EventsTimetable(
            event_dates=self.events_dates_list,
            description=self.description,
            restrict_to_events=True
        )

        return timetable
