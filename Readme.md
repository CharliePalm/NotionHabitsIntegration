# Automating Notion

This is a way of automating all processes in EllieGons HabitTracker Notion template. I love their work and thought that creating something like this to go along with it would be the cherry on top. Check out more of their stuff on their reddit profile: https://www.reddit.com/user/EllieGons/

The only thing you need to do manually is create your habits. Follow the examples in root -> habits and those DB objects will be used by the script. 

Optionally, you can add a "Days" property and add weekdays as a comma separated list (ex: Monday, Wednesday, Saturday) to override the habit's frequency. The script also uses the habit's icon as the daily habit's icon.

# Usage and Requirements
Base requirements to use this repo are python and git naturally.
You'll need to create a Notion integration and give it access to your habit's page. Tutorial here: https://www.notion.so/help/create-integrations-with-the-notion-api

Create a config by running the following in a terminal window:

    git clone https://github.com/CharliePalm/NotionHabitsIntegration
    cd NotionHabitsIntegration
    pip install -r requirements.txt
    python config.py
(When creating your config, the script will ask you for several entity IDs. If you're unfamiliar with how to find them, you simply copy the link of the page and cut out the first ID string. Basically, the link will look like:

    https://www.notion.so/{{user name}}/{{ID YOU WANT}}?v={{ID YOU DONT WANT}}
Just cut out {{ID YOU WANT}} and feed it to the script when prompted. It checks every ID you give it so you'll know if you make a mistake.

Then

    python daily_job.py


If you're interested in automating this to run daily, that can be done quite easily through your OSs cron, or uploading to a cloud server. It's made my life a lot easier - would recommend!

# Contributing
Feel free to submit a pull request, and I'll review it. Otherwise you're free to fork this repository and do whatever you like with it. I know my code perhaps isn't a shining example, but please provide unit test coverage if adding new functionality.

# Reporting bugs
Simply add a new issue and I'll check it out.

