import utils
import json
import os

class ConfigGenerator:
    headers = {}
    config = {}
    habits = []
    def __init__(self):
        self.options = [
            self.configure_api_key,
            self.configure_habit_tracker_db_id,
            self.configure_cycle_db_id,
            self.configure_cycle_dates,
            self.configure_habits_db_id,
            self.load_habits,
        ]
        try:
            with open('./config.json', 'r') as fp:
                self.config = json.load(fp)
                self.bridge = utils.Bridge(self.config['api_key']) if 'api_key' in self.config else None
                done = self.with_config_setup()
                if not done:
                    print('cool, let\'s get started!')
                else:
                    self.done()
                    return
        except Exception as e:
            pass
        
        for option in self.options:
            option()
        
        self.done()
        
    def done(self):
        with open('./config.json', 'w') as fp:
            json.dump(self.config, fp, indent=1)
        
    def with_config_setup(self):
        print('looks like you already have a config setup. Would you like to start fresh or correct some details?')
        print('0 - create brand new config')
        print('1 - correct old data')
        r = input('')
        while r not in ['0', '1']:
            r = input('please input either 0 or 1 from the above options')
            
        if r == '0':
            return False
        
        print('okay, which fields would you like to correct?')
        print('0 - api key')
        print('1 - habit tracker database id (root -> Planner -> Habit Tracker)')
        print('2 - cycles database id (root -> Cycles -> Habits Review)')
        print('3 - days of the month to create new cycles')
        print('4 - habit database id (root -> Habits)')
        print('5 - update habits (use if you changed the frequency or tracking status of a habit and want it updated in your config)')
        while 1:
            r = input('enter your selections as a comma separated list please (ex: 1, 2, 4): ')
            try:
                to_do = [self.options[int(selection)] for selection in r.replace(' ', '').split(',')]
            except:
                print('error parsing your input, please try again')
                continue
            break
        for task in to_do:
            task()
        return True
                
                
    def configure_api_key(self):
        self.config['api_key'] = input('What is your integration key? it should look like secret_ followed by a lot of numbers and letters: ')
        while self.config['api_key'][0:7] != 'secret_':
            self.config['api_key'] = input('That doesn\'t look quite right. Are you sure that\'s your api key? Please try again: ')

        self.bridge = utils.Bridge(self.config['api_key'])

    def configure_habit_tracker_db_id(self):
        r = None
        while r == None:
            self.config['habit_tracker_db_id'] = input('\nPlease provide the ID to the habit tracking DB. This is usually found under root -> Planner -> Habit Tracker: ')

            print('...testing your ID and api key...')
            r = self.test_db(self.config['habit_tracker_db_id'])
        print('\nall good!\n')
        
    def configure_cycle_db_id(self):
        r = None
        while r == None:
            self.config['cycles_db_id'] = input('\nPlease provide the ID to your cycles DB: ')

            print('...testing your ID and api key...')
            r = self.test_db(self.config['cycles_db_id'])
        print('\nall good!\n')
    
    def configure_cycle_dates(self):
        print('On what days of the month would you like new cycles to be created?')
        while 1:
            try:
                cycle_dates = input('please input your days as numbers followed by commas (ex: 1, 7, 14, 21): ')
                self.config['new_cycle_dates'] = [int(date) for date in cycle_dates.replace(' ', '').split(',')]
                if max(self.config['new_cycle_dates']) > 28:
                    print('no days of the month greater than 28 plz')
            except:
                print('couldn\'t parse input - please try again\n')
                continue
            return
            
    def configure_habits_db_id(self):
        r = None
        while r == None:
            self.config['habits_db'] = input('\nPlease provide the ID to the habits DB. This is usually found under root -> Habits: ')

            print('...testing your ID and api key...')
            r = self.habits = self.test_db(self.config['habits_db'])
        print('\nall good!\n')
        
    def load_habits(self):
        print('loading your habits into the config file. This could take a few seconds.')

        self.config['habits'] = []
        if not self.habits:
            if 'habits_db' not in self.config or not self.config['habits_db']:
                print('you don\'t currently have any habits loaded and don\'t have your daily habits db ID stored. Please add your Habits DB ID and try again')
            try:
                resp = self.bridge.query(self.config['habits_db'], {})
            except Exception as e:
                print('error getting habits: ')
                print(e)
                return
            self.habits = resp.json()['results']
        for habit in self.habits:
            self.config['habits'].append({
                'name': habit['properties']['Name']['title'][0]['plain_text'],
                'frequency': habit['properties']['Frequency']['select']['name'],
                'id': habit['id'],
                'icon': habit['icon']['emoji'],
                'status': habit['properties']['Status']['select']['name'],
                'days': habit['properties']['Days']['rich_text'][0]['text']['content'] if 'Days' in habit['properties'] and habit['properties']['Days']['rich_text'] else None,
            })

    def test_db(self, db_id):
        r = self.bridge.query(db_id, {})
        if r.status_code != 200 or not r.json()['results']:
            print('error encountered when querying db with id: ' + db_id)
            print('response received from notion: ')
            print(r.json())
            return None
        return r.json()['results']
    

class ConfigObject:
    habits = []
    cycles_db_id = ''
    new_cycle_dates = []
    api_key = ''
    habit_tracker_db_id = ''
    habits_db = ''
    def __init__(self):
        try:
            my_file = os.path.realpath(__file__)
            with open(my_file[0:-9] + 'config.json', 'r') as fp:
                self.config = json.load(fp)
                for key in self.config:
                    setattr(self, key, self.config[key])
        except Exception as e:
            print('error encountered creating conf obj')
            raise e

if __name__ == '__main__':    
    print('\nhello! let\'s get you set up!\n')
    print('for future reference, "root" refers to the root directory of the habit tracker')

    config = ConfigGenerator()

    print('here\'s what I have for your config! Saving it to notion/config.json - you can edit it anytime you need to or run this script again!')
    print(config.config)
