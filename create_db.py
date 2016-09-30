import sqlite3

db = "../TwitterElection/twitter_election.db"

conn = sqlite3.connect(db)
c = conn.cursor()

try:
    c.execute("DROP TABLE election_data")
    c.execute("DROP TABLE coverage")
    c.execute("DROP TABLE twitter_data")
except:
    pass

cmd = "CREATE TABLE election_data (timestamp DATETIME, num_tweet INTEGER);"
c.execute(cmd)

cmd = "CREATE TABLE coverage(timestamp DATETIME, hillary REAL, trump REAL);"
c.execute(cmd)

cmd = "CREATE TABLE twitter_data(sid INTEGER, loc TEXT, created_at DATETIME, text TEXT, polarity INTEGER, " \
      "subjectivity INTEGER);"
c.execute(cmd)

conn.commit()
conn.close()
