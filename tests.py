
import unittest
from freezegun import freeze_time
from notion import Notion
from datetime import datetime
# from the time writing this - only the days of the week are important
monday = '2023-04-10'
tuesday = '2023-04-11'
wednesday = '2023-04-12'
thursday = '2023-04-13'
friday = '2023-04-14'
saturday = '2023-04-15'
sunday = '2023-04-16'
YMD = '%Y-%m-%d'

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

    # this method is necessary because time isn't frozen until the method is entered
    def setup_frozen(self):
        self.notion.current_habit_datetime = datetime.now()

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

    # cycle end date
    def test_get_cycle_end_date_correct_date(self):
        self.notion.current_habit_datetime = datetime.fromisoformat('2023-04-01')
        self.notion.config.new_cycle_dates = [1]
        result, cycle_num = self.notion.get_cycle_end_date()
        self.assertEqual(cycle_num, 0)
        self.assertEqual(result.strftime(YMD), '2023-05-01')
    
    def test_get_cycle_next_date_wrong_day(self):
        self.notion.current_habit_datetime = datetime.fromisoformat('2023-11-14')
        self.notion.config.new_cycle_dates = [15]
        result, cycle_num = self.notion.get_cycle_end_date()
        self.assertEqual(cycle_num, 0)
        self.assertEqual(result.strftime(YMD), '2023-11-15')

    def test_get_cycle_next_date_wrong_day_next_month(self):
        self.notion.current_habit_datetime = datetime.fromisoformat('2023-11-30')
        self.notion.config.new_cycle_dates = [1]
        result, cycle_num = self.notion.get_cycle_end_date()
        self.assertEqual(cycle_num, 0)
        self.assertEqual(result.strftime(YMD), '2023-12-01')

    def test_get_cycle_end_date_wrong_date(self):
        self.notion.current_habit_datetime = datetime.fromisoformat('2023-04-10')
        self.notion.config.new_cycle_dates = [1]
        result, cycle_num = self.notion.get_cycle_end_date()
        self.assertEqual(cycle_num, 0)
        self.assertEqual(result.strftime(YMD), '2023-05-01')

    def test_get_cycle_end_date_two_new_cycle_dates_wrong(self):
        self.notion.current_habit_datetime = datetime.fromisoformat('2023-04-05')
        self.notion.config.new_cycle_dates = [1, 15]
        result, cycle_num = self.notion.get_cycle_end_date()
        self.assertEqual(cycle_num, 1)
        self.assertEqual(result.strftime(YMD), '2023-04-15')

    def test_get_cycle_end_date_two_new_cycle_dates_wrong(self):
        self.notion.current_habit_datetime = datetime.fromisoformat('2023-04-05')
        self.notion.config.new_cycle_dates = [1, 15]
        result, cycle_num = self.notion.get_cycle_end_date()
        self.assertEqual(cycle_num, 1)
        self.assertEqual(result.strftime(YMD), '2023-04-15')

    def test_get_cycle_end_date_three_new_cycle_dates_wrong(self):
        self.notion.current_habit_datetime = datetime.fromisoformat('2023-04-17')
        self.notion.config.new_cycle_dates = [1, 15, 25]
        result, cycle_num = self.notion.get_cycle_end_date()
        self.assertEqual(result.strftime(YMD), '2023-04-25')
        self.assertEqual(cycle_num, 2)
    
    def test_get_cycle_end_date_three_new_cycle_dates_repeat(self):
        self.notion.current_habit_datetime = datetime.fromisoformat('2023-04-25')
        self.notion.config.new_cycle_dates = [1, 15, 25]
        result, cycle_num = self.notion.get_cycle_end_date()
        self.assertEqual(result.strftime(YMD), '2023-05-01')
        self.assertEqual(cycle_num, 0)

    # date list generators
    @freeze_time(monday)
    def test_get_week_monday(self):
        self.setup_frozen()
        vals = list(self.notion.get_week())
        self.assertListEqual(vals, [monday, tuesday, wednesday, thursday, friday, saturday, sunday])
    
    @freeze_time(tuesday)
    def test_get_week_tuesday(self):
        self.setup_frozen()
        vals = list(self.notion.get_week())
        self.assertListEqual(vals, [tuesday, wednesday, thursday, friday, saturday, sunday, '2023-04-17'])

    @freeze_time(monday)
    def test_get_month_mid_month(self):
        self.setup_frozen()
        vals = list(self.notion.get_month())
        # should contain dates 10 through 30 inclusive
        self.assertEqual(len(vals), 21)
        
    @freeze_time('4-30-2023')
    def test_get_month_end_of_month(self):
        self.setup_frozen()
        vals = list(self.notion.get_month())
        # should contain only 4-30-2023
        self.assertEqual(len(vals), 1)

    @freeze_time('5-1-2023')
    def test_get_weekly_start_of_month(self):
        self.setup_frozen()
        vals = list(self.notion.get_month())
        # should contain dates 1 through 31 inclusive
        self.assertEqual(len(vals), 31)

    @freeze_time('5-01-2023')
    def test_get_cyclic_start_of_month(self):
        self.setup_frozen()
        self.notion.config.new_cycle_dates = [1]
        vals = list(self.notion.get_dates_til_next_cycle())
        # 1 - 31 inclusive
        self.assertEqual(len(vals), 31)
    
    @freeze_time('5-01-2023')
    def test_get_cyclic_mid_month(self):
        self.setup_frozen()
        self.notion.config.new_cycle_dates = [15]
        vals = list(self.notion.get_dates_til_next_cycle())
        # 1 - 14 inclusive
        self.assertEqual(len(vals), 14)

    @freeze_time('5-01-2023')
    def test_get_cyclic_two_dates(self):
        self.setup_frozen()
        self.notion.config.new_cycle_dates = [1, 15]
        vals = list(self.notion.get_dates_til_next_cycle())
        # 1 - 14 inclusive
        self.assertEqual(len(vals), 14)

    @freeze_time('4-15-2023')
    def test_get_cyclic_cross_month(self):
        self.setup_frozen()
        self.notion.config.new_cycle_dates = [15]
        vals = list(self.notion.get_dates_til_next_cycle())
        self.assertEqual(len(vals), 30)

    # frequency
    @freeze_time(monday)
    def test_monday(self):
        self.setup_frozen()
        self.notion.config.habits = self.habits
        valid = set(['3x Week', 'Daily', '5x Week', 'Workday', '4x Week', '3x Week days', '6x Week'])
        habits = list(self.notion.get_filtered_habits())
        test_valid_dates(self, valid, habits)
    
    @freeze_time(tuesday)
    def test_tuesday(self):
        self.setup_frozen()
        self.notion.config.habits = self.habits
        valid = set(['4x Week', 'Daily', '5x Week', 'Workday', '2x Week', '6x Week'])
        habits = list(self.notion.get_filtered_habits())
        test_valid_dates(self, valid, habits)

    @freeze_time(wednesday)
    def test_wednesday(self):
        self.setup_frozen()
        self.notion.config.habits = self.habits
        valid = set(['Daily', '5x Week', 'Workday', '3x Week', '6x Week', '1x Week'])
        habits = list(self.notion.get_filtered_habits())
        test_valid_dates(self, valid, habits)
            
    @freeze_time(thursday)
    def test_thursday(self):
        self.setup_frozen()
        self.notion.config.habits = self.habits
        valid = set(['4x Week', 'Daily', 'Workday', '2x Week', '6x Week', '3x Week days'])
        habits = list(self.notion.get_filtered_habits())
        test_valid_dates(self, valid, habits)
    
    @freeze_time(friday)
    def test_friday(self):
        self.setup_frozen()
        self.notion.config.habits = self.habits
        valid = set(['Daily', 'Workday', '5x Week', '6x Week', '3x Week', '3x Week days'])
        habits = list(self.notion.get_filtered_habits())
        test_valid_dates(self, valid, habits)
        
    @freeze_time(saturday)
    def test_saturday(self):
        self.setup_frozen()
        self.notion.config.habits = self.habits
        valid = set(['Daily', '6x Week', '5x Week', '4x Week'])
        habits = list(self.notion.get_filtered_habits())
        test_valid_dates(self, valid, habits)

    @freeze_time(sunday)
    def test_sunday(self):
        self.setup_frozen()
        self.notion.config.habits = self.habits
        valid = set(['Daily'])
        habits = list(self.notion.get_filtered_habits())
        test_valid_dates(self, valid, habits)
    
    @freeze_time('2022-07-04') # fourth of july fell on a monday in 2022
    def test_holiday(self):
        self.setup_frozen()
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
