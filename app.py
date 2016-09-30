import pandas as pd
import setting
import sqlite3
import time
from datetime import datetime, timedelta
import tweepy
from textblob import TextBlob
from bokeh.plotting import *
from bokeh.models import Range1d, HoverTool, BoxSelectTool, PanTool, WheelZoomTool, ResetTool, SaveTool
from bokeh.models.sources import ColumnDataSource
from bokeh.client import push_session

db = "../TwitterElection/twitter_election.db"


class StreamListener(tweepy.StreamListener):

    def __init__(self, time_limit=900, conn=None):
        self.start_time = time.time()
        self.limit = time_limit
        self.dbconn = conn
        super(StreamListener, self).__init__()

    def on_status(self, status):
        if (time.time()-self.start_time) <= self.limit:
            if status.retweeted:
                return
            text = status.text
            created = status.created_at
            loc = status.user.location
            id_str = status.id_str
            blob = TextBlob(text)
            senti = blob.sentiment
            polar = senti.polarity
            sub = senti.subjectivity

            try:
                cmd = "INSERT INTO twitter_data(sid, loc, created_at, text, polarity, subjectivity) VALUES(?,?,?,?," \
                       "?,?);"
                c = self.dbconn.cursor()
                c.execute(cmd, (id_str, loc, created, text, polar, sub))
                self.dbconn.commit()

            except Exception as e:
                print e
        else:
            return False

    def on_error(self, status_code):
        if status_code == 402:
            return False


def update_coverage(t1, t2, conn):
    c = conn.cursor()
    h_cmd = "SELECT COUNT(text) FROM twitter_data WHERE (LOWER(text) LIKE '%hillary%' OR  LOWER(text) LIKE " \
            "'%mrs.clinton%') AND created_at >= ? AND created_at <= ?;"
    t_cmd = "SELECT COUNT(text) FROM twitter_data WHERE LOWER(text) LIKE '%trump%' AND created_at >= ? AND " \
            "created_at <= ? ;"
    all_cmd = "SELECT COUNT(*) FROM twitter_data WHERE created_at >= ? AND created_at <=?;"

    c.execute(h_cmd, (t1, t2))
    h_count = c.fetchall()[0][0]

    c.execute(t_cmd, (t1, t2))
    t_count = c.fetchall()[0][0]

    c.execute(all_cmd, (t1, t2))
    total = float(c.fetchall()[0][0])

    insert_cmd = "INSERT INTO coverage(timestamp, hillary, trump) VALUES(?,?,?);"
    if total != 0:
        c.execute(insert_cmd, (t2, h_count/total, t_count/total))
    else:
        c.execute(insert_cmd, (t2, 0, 0))
    conn.commit()


def get_last_15_coverage(m_str, conn):
    c = conn.cursor()
    select_cmd = "SELECT * FROM coverage WHERE timestamp >= (SELECT DATETIME('now', ?));"
    try:
        c.execute(select_cmd, (m_str, ))
    except Exception as e:
        print e
    result = c.fetchall()
    df = pd.DataFrame(result, columns=['timestamp', 'Hillary', 'Trump'])
    return df

time_f = '%Y-%m-%d %H:%M:%S'
tools = [HoverTool(), BoxSelectTool(), PanTool(), WheelZoomTool(), ResetTool(), SaveTool()]
p = figure(plot_width=900, plot_height=400, tools=tools, x_axis_type='datetime', title='Social Media (Twitter) '
                                                                                       'Coverage Comparision')
p.set(y_range=Range1d(0, 1))
p.xaxis.axis_label = 'Date'
p.yaxis.axis_label = 'Twitter Coverage'
data = ColumnDataSource(data=dict(x=[], y1=[], y2=[]))
line1 = p.line("x", "y1", source=data, color='royalblue', legend='Hillary', line_width=2)
line2 = p.line("x", "y2", source=data, color='tomato', legend='Trump', line_width=2)


def event(conn):
    t_start = datetime.utcnow().strftime(time_f)
    t_stop = (datetime.strptime(t_start, time_f) + timedelta(minutes=15)).strftime(time_f)
    auth = tweepy.OAuthHandler(setting.CONSUMER_KEY, setting.CONSUMER_SECRET)
    auth.set_access_token(setting.ACCESS_TOKEN, setting.ACCESS_SECRET)
    api = tweepy.API(auth)

    stream_listener = StreamListener(time_limit=900, conn=conn)
    stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
    stream.filter(track=setting.track_terms, languages=['en'])
    #print "reading finish"

    update_coverage(t_start, t_stop, conn)
    table = get_last_15_coverage("-15 minutes", conn)
    table['timestamp'] = table.timestamp.astype('datetime64[s]')
    #print table.timestamp, table.Hillary

    # PLOTTING

    # p.line(table['timestamp'], table['Hillary'], color='blue', legend='Hillary')
    # p.line(table['timestamp'], table['Trump'], color='red', legend='Trump')

    line1.data_source.data['x'] = table['timestamp']
    line1.data_source.data['y1'] = table.Hillary
    line2.data_source.data['x'] = table['timestamp']
    line2.data_source.data['y2'] = table.Trump


if __name__ == "__main__":
    conn = sqlite3.connect(db)
    table = get_last_15_coverage("-15 minutes", conn)
    # table.columns = ['timestamp', 'Hillary', 'Trump']
    table['timestamp'] = table.timestamp.astype('datetime64[s]')
    line1.data_source.data['x'] = table['timestamp']
    line1.data_source.data['y1'] = table.Hillary
    line2.data_source.data['x'] = table['timestamp']
    line2.data_source.data['y2'] = table.Trump

    session = push_session(curdoc())
    session.show(p)
    while True:
        event(conn)
