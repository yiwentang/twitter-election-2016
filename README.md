# twitter-election-2016
Follow 2016 Presidential Election Using Twitter Data 

Using twttier streaming api to discover how many people are talking about Trump or Hillary

This program stores the real time twitter data into Sqlite database. Eevry minute, it queries the data in the database and performs analysis. Finally it uses bokeh libaray to visulize the coverage for Trump and Hillary.

0. Install packages in the requirements.txt

1. Go to twitter to aquire token and api key, then input the information into private.py

2. Create a Sqilte Database, name it twitter_election. Run create_db.py to create tables

3. Run 'bokeh serve' in terminal, then run app.py

![bokeh_plot](https://cloud.githubusercontent.com/assets/18508854/19005472/bfc8baca-870f-11e6-8bae-0a833bd898b8.png)


