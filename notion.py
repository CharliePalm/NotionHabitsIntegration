from copy import deepcopy
from datetime import datetime, timedelta
from typing import Generator
from holidays import US
import utils, config
from model import Frequency, DEFAULT_CYCLE_ICON
YMD = '%Y-%m-%d'

class Notion:
    current_habit_datetime: datetime = datetime.now()
    def __init__(self):
        try:
            self.config = config.ConfigObject()
            self.generator = config.ConfigGenerator()
        except:
            raise Exception('there was an error loading your config. Are you sure you created one?')
        self.bridge = utils.Bridge(self.config.api_key)
        self.current_cycle = None

    def run(self):
        if not self.config:
            raise Exception('config not initialized before running')
        self.generator.load_habits()
        if self.config.job_frequency == Frequency.Daily.value:
            self.create_daily_habits()
        elif self.config.job_frequency == Frequency.Weekly.value:
            self.create_weekly_habits()
        elif self.config.job_frequency == Frequency.Monthly.value:
            self.create_monthly_habits()
        elif self.config.job_frequency == Frequency.Cyclic.value:
            self.create_cyclic_habits()
        
    def create_cyclic_habits(self):
        for date in self.get_week():
            self.get_dates_til_next_cycle(date)
        
    def create_weekly_habits(self):
        '''creates habits for 1 week, not necessarily Sunday - Sunday'''
        for date in self.get_week():
            self.create_daily_habits(date)
    
    def create_monthly_habits(self):
        for date in self.get_month():
            self.create_daily_habits(date)

        
    def get_week(self) -> Generator[str, None, None]:
        '''
        a generator of week dates in format YMD used when creating weekly habits
        '''
        today = datetime.now()
        for i in range(7):
            yield (today + timedelta(days=i)).strftime(YMD)

    def get_month(self) -> Generator[str, None, None]:
        '''
        generates a list of days from today -> end of month inclusive
        '''
        today = date = datetime.now()
        curr_month = today.month
        i = 1
        while curr_month == date.month:
            yield date.strftime(YMD)
            date = today + timedelta(days=i)
            i += 1
    
    def get_dates_til_next_cycle(self):
        date = datetime.now()
        end_date, _ = self.get_cycle_end_date()
        end_date = end_date.strftime(YMD)
        formatted_date = date.strftime(YMD)
        while formatted_date != end_date:
            yield formatted_date
            date = date + timedelta(days=1)
            formatted_date = date.strftime(YMD)
    
    def create_daily_habits(self, date = None):
        '''
        creates daily habits for a provided date, otherwise today if none is provided
        '''
        if date:
            self.current_habit_datetime = datetime.fromisoformat(date)
        current_cycle_id = self.get_current_cycle_id()
        if not current_cycle_id:
            raise Exception('failed to get current_cycle_id')
        filtered_habits = self.get_filtered_habits()
        for habit in filtered_habits:
            properties = {
                'Name': {
                    'title': [{'type': 'text', 'text': {'content': habit['name']}}],
                },
                'Date': {
                    'date': {'start': self.current_habit_datetime.strftime(YMD)},
                },
                'Cycle': {
                    'relation': [{'id': current_cycle_id}],
                },
                'Progress': {
                    'checkbox': False,
                },
                'Neutral': {
                    'checkbox': False,
                },
                'Missed': {
                    'checkbox': True,
                },
                'Setback Notes': {
                    'rich_text': [{'type': 'text', 'text': {'content': ''}}],
                },
                'Habit': {
                    'select': {'name': habit['name']},
                },
                'Habit (Relation)': {
                    'relation': [{
                        'id': habit['id'],
                    }],
                },
            }
            self.bridge.create_db_page(self.config.habit_tracker_db_id, properties, habit['icon'], habit['icon_type'])
            
    def get_current_cycle_id(self):
        # create new cycle if we need to, either in upcoming or active state
        if self.current_habit_datetime.day in self.config.new_cycle_dates:
            self.create_cycle()
            return self.current_cycle['id']
        
        if not self.current_cycle:
            self.current_cycle = self.get_period_cycle()
        # otherwise if we have a cycle stored in current_cycle and its dates are valid, use it
        if self.current_cycle and self.current_cycle['properties']['Date Range']['date']['start'] <= self.current_habit_datetime.strftime(YMD) and self.current_cycle['properties']['Date Range']['date']['end'] > self.current_habit_datetime.strftime(YMD): return self.current_cycle['id']
        
        # dates are not valid on current_cycle or it doesn't exist, create new one or pull from API
        self.create_cycle()
        return self.current_cycle['id']

    def get_active_cycle(self):
        '''
        gets cycle in active state, regardless of its dates
        '''
        if self.current_cycle and self.current_cycle['properties']['Status']['select']['name'] == 'Active': return self.active_cycle
        response = self.bridge.query(self.config.cycles_db_id, {
                'filter': {
                    'property': 'Status',
                    'select': {
                        'equals': 'Active'
                    }
                }
            })
        r = response.json()
        return r['results'][0] if 'results' in r and r['results'] else None

    def get_period_cycle(self):
        '''
        gets the cycle that contains self.current_habit_datetime
        '''
        habit_dt_formatted = self.current_habit_datetime.strftime(YMD)
        # notion doesn't let us filter by end date for some reason
        response = self.bridge.query(self.config.cycles_db_id, {
                'filter': {
                    'and': [
                        {
                            'property': 'Date Range',
                            'date': {
                                'on_or_before': habit_dt_formatted
                            }
                        },
                        {
                            'or': [
                                {
                                    'property': 'Status',
                                    'select': {
                                        'does_not_equal': 'Archive'
                                    }
                                },
                                {
                                    'property': 'Status',
                                    'select': {
                                        'does_not_equal': 'Error'
                                    }
                                }
                            ]
                        }
                    ]
                }
            })
        r = response.json()
        results = r['results'] if 'results' in r and r['results'] else None
        if not results: return results

        for r in results:
            cycle = r['properties']
            if cycle['Date Range']['date']['end'] > habit_dt_formatted:
                return r

        
    def create_cycle(self):
        '''
        creates a new monthly cycle or activates an upcoming cycle, setting in the class property current_cycle
        '''
        active_cycle = None
        end_date, next_cycle_idx = self.get_cycle_end_date()
        end_date_formatted = end_date.strftime(YMD)
        now_formatted = datetime.now().strftime(YMD)
        habit_datetime_formatted = self.current_habit_datetime.strftime(YMD)
        needs_new_cycle_today = now_formatted == habit_datetime_formatted

        if needs_new_cycle_today:
            active_cycle = self.get_active_cycle()
            if active_cycle:
                self.update_cycle_state('Archive', active_cycle['id'])
        
        cycles_resp = self.get_upcoming_cycles() or []
        # error any cycles with conflicting dates
        for cycle in cycles_resp:
            if cycle['properties']['Date Range']['date']['start'] == habit_datetime_formatted and cycle['properties']['Date Range']['date']['end'] != end_date_formatted:
                self.update_cycle_state('Error', cycle['id'])
        
        # activate valid cycle if it exists and we need it, otherwise find existing valid upcoming cycle
        for cycle in cycles_resp:
            if needs_new_cycle_today and cycle['properties']['Date Range']['date']['start'] == now_formatted and cycle['properties']['Date Range']['date']['end'] == end_date_formatted:
                self.update_cycle_state('Active', cycle['id'])
                self.current_cycle = cycle
                return cycle # returning the cycle here with no update as its id may be used in the future, current state will not
            elif not needs_new_cycle_today and cycle['properties']['Date Range']['date']['start'] == habit_datetime_formatted and cycle['properties']['Date Range']['date']['end'] == end_date_formatted:
                self.current_cycle = cycle
                return cycle

        # no cycle to activate means we create a new one
        new_cycle_properties = {
            'Name': {
                'title': [
                    {
                        'text': {
                            'content': self.current_habit_datetime.strftime('%B') + (' (part ' + str(next_cycle_idx + 1)  + ')' if len(self.config.new_cycle_dates) > 1 else ''),
                        }
                    }
                ]
            },
            'Date Range': {
                'date': {
                    'start': habit_datetime_formatted,
                    'end': end_date_formatted,
                }
            },
            'Status': {
                'select': {
                    "name": "Active" if needs_new_cycle_today else 'Upcoming',
                }
            }
        }
        result = self.bridge.create_db_page(self.config.cycles_db_id, new_cycle_properties, utils.get_icon(active_cycle or self.current_cycle) or DEFAULT_CYCLE_ICON, utils.get_icon_type(active_cycle or self.current_cycle) or 'emoji')
        self.current_cycle = result
    
    def update_cycle_state(self, state, id):
        to_update = {
            'Status':  {
                'select': {
                    'name': state,
                }
            }
        }
        return self.bridge.update_db_page(to_update, id)
    
    def get_upcoming_cycles(self):
        response = self.bridge.query(self.config.cycles_db_id, {
                'filter': {
                    'property': 'Status',
                    'select': {
                        'equals': 'Upcoming'
                    }
                }
            })
        r = response.json()
        if not ('results' in r and r['results']):
            return None
        
        r = r['results']
        return r
        
    def get_cycle_end_date(self) -> tuple[datetime, int]:
        next_cycle_idx = ((self.config.new_cycle_dates.index(self.current_habit_datetime.day) + 1) % len(self.config.new_cycle_dates)) if self.current_habit_datetime.day in self.config.new_cycle_dates else None
        end_date = deepcopy(self.current_habit_datetime)
        min_dif = 32
        if next_cycle_idx is None:
            for idx, date in enumerate(self.config.new_cycle_dates):
                if date - end_date.day < min_dif and date - end_date.day > 0:
                    min_dif = date - end_date.day
                    next_cycle_idx = idx
                    
        if next_cycle_idx or min_dif < 32:
            end_date = end_date.replace(day=self.config.new_cycle_dates[next_cycle_idx])
        else:
            next_cycle_idx = 0
            end_date = end_date.replace(day=self.config.new_cycle_dates[0], month=(1 if end_date.month == 12 else end_date.month + 1))
        return end_date, next_cycle_idx
        
    def get_filtered_habits(self) -> Generator:
        '''
        creates a generator of filtered habits from those provided in self.config \n
        this is the ugliest method i've ever written in my life but I can't think of a clearer way to include all the functionality
        '''
        holidays = US()
        # define default values
        wd = self.current_habit_datetime.isoweekday()
        is_workday = wd not in [6, 7] and self.current_habit_datetime.strftime(YMD) not in holidays
        is_1x_week = wd == 3 # W
        is_2x_week = wd in [2, 4] #  T R
        is_3x_week = wd in [1, 3, 5] # M W F
        is_4x_week = wd in [1, 2, 4, 6] # M T R S
        is_5x_week = wd in [1, 2, 3, 5, 6] # M T W F S
        is_6x_week = wd != 7 # M T W F S

        for habit in self.config.habits:
            if habit['status'] != 'On':
                continue
            # users can manually set the dates they want otherwise we just use the defaults
            if 'days' in habit and habit['days']:
                days: str = habit['days']
                # this is way more loops than we need but it's pretty and will never have more than 7 members
                parsed_days = [day.lower() for day in days.replace(' ', '').split(',')]
                if self.current_habit_datetime.strftime('%A').lower() in parsed_days:
                    yield habit
                continue
            
            freq = habit['frequency']
            if freq[0] == 'D': # daily
                yield habit
            elif freq[0] == 'W' and is_workday:
                yield habit
            elif freq[0] == '1' and is_1x_week:
                yield habit
            elif freq[0] == '2' and is_2x_week:
                yield habit
            elif freq[0] == '3' and is_3x_week:
                yield habit
            elif freq[0] == '4' and is_4x_week:
                yield habit
            elif freq[0] == '5' and is_5x_week:
                yield habit
            elif freq[0] == '6' and is_6x_week:
                yield habit
