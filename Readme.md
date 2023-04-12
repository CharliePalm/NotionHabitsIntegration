# Automating Notion

This is a way of automating the all processes in EllieGons HabitTracker Notion template. I love their work and thought that creating something like to go along with it would be the cherry on top. Check out more of their stuff on their reddit: https://www.reddit.com/user/EllieGons/

The only thing you need to do manually is create your habits. Follow the examples in root -> habits and those DB objects will be used by the script. 

# Usage
Base requirements to use this repo are python and git naturally.
Create a config by running the following in a terminal window:

    git clone https://github.com/CharliePalm/NotionHabitsIntegration
    cd NotionHabitsIntegration
    pip install -r requirements.txt
    python config.py
Then

    python daily_job.py


If you're interested in automating this to run daily, that can be done quite easily through your OSs cron, or uploading to a cloud server. It's made my life a lot easier - would recommend!

# Contributing
Feel free to submit a pull request, and I'll review it. Otherwise you're free to fork this repository and do whatever you like with it. I know my code perhaps isn't a shining example, but please provide unit test coverage if adding new functionality.

# Reporting bugs
Simply add a new issue and I'll check it out.

