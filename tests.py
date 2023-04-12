
import unittest
from freezegun import freeze_time
from notion import Notion
# from the time writing this - only the days of the week are important
monday = '2023-04-10'
tuesday = '2023-04-11'
wednesday = '2023-04-12'
thursday = '2023-04-13'
friday = '2023-04-14'
saturday = '2023-04-15'
sunday = '2023-04-16'

class TestNotion(unittest.TestCase):
    notion = Notion()
    dow_types = ['6x Week', '5x Week', '4x Week', '3x Week', '2x Week', '1x Week', 'Daily', 'Workday']
    habits = [
        {
            'name': dow_type,
            'frequency': dow_type,
            'status': 'On',
            'days': None
        } for dow_type in dow_types
    ]
    habits.append({
        'name': '3x Week days',
        'frequency': '3x Week',
        'status': 'On',
        'days': 'Monday, Thursday, Friday'
    })
    
    def test_filter_habits_by_status(self):
        test_habits = [
            {
                'name': 'Wake up Early',
                'frequency': 'Daily',
                'status': 'Off'
            },
        ]
        self.notion.config.habits = test_habits
        for habit in self.notion.get_filtered_habits():
            print(habit)
            self.assertFalse(True)
    
    @freeze_time(monday)
    def test_monday(self):
        self.notion.config.habits = self.habits
        valid = set(['3x Week', 'Daily', '5x Week', 'Workday', '4x Week', '3x Week days', '6x Week'])
        habits = list(self.notion.get_filtered_habits())
        test_valid_dates(self, valid, habits) 
    
    @freeze_time(tuesday)
    def test_tuesday(self):
        self.notion.config.habits = self.habits
        valid = set(['4x Week', 'Daily', '5x Week', 'Workday', '2x Week', '6x Week'])
        habits = list(self.notion.get_filtered_habits())
        test_valid_dates(self, valid, habits) 

    @freeze_time(wednesday)
    def test_wednesday(self):
        self.notion.config.habits = self.habits
        valid = set(['Daily', '5x Week', 'Workday', '3x Week', '6x Week', '1x Week'])
        habits = list(self.notion.get_filtered_habits())
        test_valid_dates(self, valid, habits) 
            
    @freeze_time(thursday)
    def test_thursday(self):
        self.notion.config.habits = self.habits
        valid = set(['4x Week', 'Daily', 'Workday', '2x Week', '6x Week', '3x Week days'])
        habits = list(self.notion.get_filtered_habits())
        test_valid_dates(self, valid, habits) 
    
    @freeze_time(friday)
    def test_friday(self):
        self.notion.config.habits = self.habits
        valid = set(['Daily', 'Workday', '5x Week', '6x Week', '3x Week', '3x Week days'])
        habits = list(self.notion.get_filtered_habits())
        test_valid_dates(self, valid, habits) 
        
    @freeze_time(saturday)
    def test_saturday(self):
        self.notion.config.habits = self.habits
        valid = set(['Daily', '6x Week', '5x Week', '4x Week'])
        habits = list(self.notion.get_filtered_habits())
        test_valid_dates(self, valid, habits) 

    @freeze_time(sunday)
    def test_sunday(self):
        self.notion.config.habits = self.habits
        valid = set(['Daily'])
        habits = list(self.notion.get_filtered_habits())
        test_valid_dates(self, valid, habits) 
    
    @freeze_time('2022-07-04') # fourth of july fell on a monday in 2022
    def test_holiday(self):
        self.notion.config.habits = self.habits
        # same as monday with no workday
        valid = set(['3x Week', 'Daily', '5x Week', '4x Week', '3x Week days', '6x Week'])
        habits = list(self.notion.get_filtered_habits())
        test_valid_dates(self, valid, habits) 

def test_valid_dates(tester, valid, habits):
    expected = [habit for habit in tester.habits if habit['name'] in valid]
    invalid = [habit for habit in tester.habits if habit['name'] not in valid]
    for entry in expected:
        tester.assertIn(entry, habits)
    for entry in invalid:
        tester.assertNotIn(entry, habits)  
                    
            
    
if __name__ == '__main__':
    unittest.main()
