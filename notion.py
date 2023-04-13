from copy import deepcopy
from datetime import datetime
from typing import Generator
from holidays import US
import utils, config
class Notion:
    def __init__(self):
        try:
            self.config = config.ConfigObject()
        except:
            raise Exception('there was an error loading your config. Are you sure you created one?')
        self.bridge = utils.Bridge(self.config.api_key)

    def create_daily_habits(self):
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
                    'date': {'start': datetime.now().strftime('%Y-%m-%d')},
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
        cycle = self.get_active_cycle()
        if datetime.now().day in self.config.new_cycle_dates or not cycle:
            cycle = self.create_new_monthly_cycle(cycle)
        return cycle['id'] if cycle and 'id' in cycle else None

    def get_active_cycle(self):
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
        
    def create_new_monthly_cycle(self, active_cycle = None):
        '''
        creates a new monthly cycle
        '''
        active_cycle = self.get_active_cycle() if not active_cycle else active_cycle
        if active_cycle:
            to_update = {
                'Status':  {
                    'select': {
                        'name': 'Archive',
                    }
                }
            }
            self.bridge.update_db_page(to_update, active_cycle['id'])
        now = datetime.now()
        end_date = deepcopy(now)
        cycle_num = self.config.new_cycle_dates.index(datetime.now().day)
        if cycle_num != len(self.config.new_cycle_dates) - 1:
            end_date.replace(day=self.config.new_cycle_dates[cycle_num + 1])
        else:
            end_date.replace(day=self.config.new_cycle_dates[0], month=1 if end_date.month == 12 else end_date.month + 1)

        
        new_cycle_properties = {
            'Name': {
                'title': [
                    {
                        'text': {
                            'content': now.strftime('%B') + (' (part ' + str(cycle_num + 1)  + ')' if len(self.config.new_cycle_dates) > 1 else ''),
                        }
                    }
                ]
            },
            'Date Range': {
                'date': {
                    'start': now.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d'),
                }
            },
            'Status': {
                'select': {
                    "name": "Active",
                }
            }
        }
        result = self.bridge.create_db_page(self.config.cycles_db_id, new_cycle_properties, utils.get_icon(active_cycle), utils.get_icon_type(active_cycle))
        return result.json() if result else None
        
        
    def get_filtered_habits(self) -> Generator:
        '''
        creates a generator of filtered habits from those provided in self.config \n
        this is the ugliest method i've ever written in my life but I can't think of a clearer way to include all the functionality
        '''
        today = datetime.now()
        holidays = US()
        # define default values
        wd = today.isoweekday()
        is_workday = wd not in [6, 7] and today.strftime('%Y-%m-%d') not in holidays
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
                if today.strftime('%A').lower() in parsed_days:
                    yield habit
                continue
            
            freq = habit['frequency']
            if freq[0] == 'D': # daily
                yield habit
            elif freq[0] == 'W' and is_workday: # workday
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