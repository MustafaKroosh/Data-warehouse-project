import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplays "
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= ("""CREATE TABLE IF NOT EXISTS staging_events
(
artist VARCHAR,
auth VARCHAR,
firstName VARCHAR,
gender VARCHAR,
itemInSession INTEGER,
lastName VARCHAR, 
length FLOAT, 
level VARCHAR, 
location VARCHAR, 
method VARCHAR,
page  VARCHAR,
registration BIGINT, 
sessionId INTEGER,
song VARCHAR,
status INTEGER, 
ts BIGINT,
userAgent VARCHAR,
userId INTEGER
);
""")

staging_songs_table_create = (""" CREATE TABLE IF NOT EXISTS staging_songs
(
song_id VARCHAR,
num_songs INTEGER,
title VARCHAR,
artist_name VARCHAR,
artist_latitude FLOAT,
year INTEGER,
duration FLOAT,
artist_id VARCHAR,
artist_longitude FLOAT,
artist_location VARCHAR
);
""")

songplay_table_create = ("""CREATE TABLE IF NOT EXISTS songplays
(
songplay_id INT IDENTITY(0,1) PRIMARY KEY,
start_time TIMESTAMP NOT NULL,
user_id VARCHAR NOT NULL,
level VARCHAR, 
song_id VARCHAR,
artist_id VARCHAR,
session_id VARCHAR,
location VARCHAR,
user_agent VARCHAR
);
""")

user_table_create = ("""CREATE TABLE IF NOT EXISTS users
(
user_id int PRIMARY KEY NOT NULL,
first_name varchar,
last_name varchar,
gender varchar, 
level varchar);
""")

song_table_create = ("""CREATE TABLE IF NOT EXISTS songs
(
song_id VARCHAR PRIMARY KEY, 
title VARCHAR NOT NULL,
artist_id VARCHAR, 
year INT , 
duration FLOAT NOT NULL); 
""")

artist_table_create = ("""CREATE TABLE IF NOT EXISTS artists
(
artist_id VARCHAR PRIMARY KEY , 
name VARCHAR NOT NULL,
location TEXT,
latitude FLOAT, 
longitude FLOAT);
""")

time_table_create = ("""CREATE TABLE IF NOT EXISTS time
(
start_time time PRIMARY KEY NOT NULL,
hour INT,
day INT,
week INT,
month INT,
year INT,
weekday INT); 
""")

# STAGING TABLES

staging_events_copy = ("""copy staging_events
    from {}
    iam_role {}
    json {};
""").format(config['S3']['log_data'], config['IAM_ROLE']['arn'], config['S3']['log_jsonpath'])

staging_songs_copy = ("""copy staging_songs
    from {}
    iam_role {}
    json 'auto';
""").format(config.get('S3','SONG_DATA'), config.get('IAM_ROLE', 'ARN'))

# FINAL TABLES

songplay_table_insert = ("""INSERT INTO songplays( start_time, user_id,level, song_id,  artist_id, session_id,location, user_agent)
        
SELECT DISTINCT TIMESTAMP 'epoch' + ev.ts/1000 * interval '1 second' AS start_time,       
            ev.userId    AS user_id,
            ev.level     AS level,
            st.song_id   AS song_id,
            st.artist_id AS artist_id,
            ev.sessionId AS session_id,
            ev.location  AS location,
            ev.userAgent AS user_agent
        
        FROM staging_events ev
        JOIN staging_songs st 
        ON ev.song = st.title AND ev.artist = st.artist_name ;
""")

user_table_insert = ("""INSERT INTO users (user_id, first_name, last_name, gender,  level )
    SELECT    DISTINCT(userId) AS user_id,
                    firstName AS first_name,
                    lastName AS last_name,
                    gender AS gender,
                    level AS level
                    
    
    FROM staging_events 
    WHERE userId  IS NOT NULL
""")

song_table_insert = ("""INSERT INTO songs 
    (song_id, title, artist_id, year, duration)
    SELECT DISTINCT(song_id) AS song_id,
           title AS title,
           artist_id AS artist_id,
           year AS year,
           duration AS duration
    
    FROM staging_songs
    WHERE song_id IS NOT NULL
""")

artist_table_insert = ("""INSERT INTO artists (artist_id, name, location, latitude, longitude)
SELECT DISTINCT(artist_id) AS artist_id,
                artist_name AS name,
                artist_location AS location,
                artist_latitude AS latitude,
                artist_longitude AS  longitude
FROM staging_songs
WHERE artist_id IS NOT NULL
                
""")

time_table_insert = ("""INSERT INTO TIME (start_time, hour, day, week, month, year, weekday)

SELECT DISTINCT(e.ts) AS start_time,
       EXTRACT(hour from start_time),
       EXTRACT(day FROM start_time),
       EXTRACT(week FROM start_time),
       EXTRACT(month FROM start_time),
       EXTRACT(year FROM start_time),
       EXTRACT(dayofweek FROM start_time)
FROM songplays
                

""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
