#!/usr/bin/env python
# coding: utf-8

# In[1]:


import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


# In[2]:


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')


# In[3]:


# COPY command to load data from S3 bucket into Redshift tables.

def load_staging_tables(cur, conn):
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()
        
LOG_DATA  = config.get("S3", "LOG_DATA")
LOG_PATH  = config.get("S3", "LOG_JSONPATH")
SONG_DATA = config.get("S3", "SONG_DATA")
IAM_ROLE  = config.get("IAM_ROLE","ARN")

staging_events_copy = ("""
copy staging_events from {}
credentials 'aws_iam_role={}'
json {} compupdate on region 'us-west-2' timeformat as 'epochmillisecs';
""").format(LOG_DATA, IAM_ROLE, LOG_PATH)



staging_songs_copy = ("""
copy staging_songs from {}
credentials 'aws_iam_role={}'
json 'auto' region 'us-west-2';
""").format(SONG_DATA, IAM_ROLE)

copy_table_queries = [staging_events_copy, staging_songs_copy]





# In[4]:


def insert_tables(cur, conn):
    for query in insert_table_queries:
        cur.execute(query)
        conn.commit()

# dimention table insert
user_table_insert = ("""
INSERT INTO users (user_id, first_name, last_name, gender, level)
SELECT DISTINCT
userId AS user_id,
FirstName AS first_name,
lastName AS last_name,  
gender,
level
FROM staging_events
WHERE userId IS NOT NULL;
""")

song_table_insert = ("""
INSERT INTO songs (song_id, title, artist_id, year, duration)
SELECT DISTINCT
song_id,
title, 
artist_id, 
CAST(year AS INT), 
duration
FROM staging_songs
WHERE song_id IS NOT NULL;
""")

artist_table_insert = ("""
INSERT INTO artists (artist_id, name, location, latitude, longitude)
SELECT DISTINCT
artist_id,
artist_name AS name,        
artist_location AS location,    
artist_latitude AS latitude,    
artist_longitude AS longitude   
FROM staging_songs
WHERE artist_id IS NOT NULL;
""")

time_table_insert = ("""
INSERT INTO times (start_time, hour, day, week, month, year, weekday)
      SELECT DISTINCT timestamp 'epoch' +  (se.ts / 1000) * INTERVAL '1 second' as start_time,
                      EXTRACT(HOUR from start_time) AS hour,
                      EXTRACT(DAY from start_time) AS day,
                      EXTRACT(WEEK from start_time) AS week,
                      EXTRACT(MONTH from start_time) AS month,
                      EXTRACT(YEAR from start_time) AS year,
                      EXTRACT(DOW from start_time) AS weekday
      FROM  staging_events se;
""")


    

# fact table insert
songplay_table_insert =  ("""
INSERT INTO songplays (start_time, user_id, level, song_id,
artist_id, session_id, location, user_agent)
SELECT DISTINCT
timestamp 'epoch' +  (se.ts / 1000) * INTERVAL '1 second' as start_time,
se.userId AS user_id,
se.level,
ss.song_id,
ss.artist_id,
se.sessionId AS session_id,
ss.artist_location AS location,
se.userAgent AS user_agent
FROM staging_events se
INNER JOIN staging_songs ss 
ON (se.song = ss.title)
AND (se.artist = ss.artist_name)
AND (se.length = ss.duration)
WHERE page = 'NextSong';
""")

insert_table_queries = [user_table_insert, song_table_insert, artist_table_insert, time_table_insert, songplay_table_insert]


# In[5]:


import psycopg2
import configparser


def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    host = config.get('CLUSTER', 'host')
    dbname = config.get('CLUSTER', 'dbname')
    user = config.get('CLUSTER', 'user')
    password = config.get('CLUSTER', 'password')
    port = config.getint('CLUSTER', 'port')  

    conn = psycopg2.connect(
        host=host,
        dbname=dbname,
        user=user,
        password=password,
        port=port
    )
    cur = conn.cursor()
    
    
    
    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()


# In[ ]:




