# Data Modeling wi Postgres - Sparkify Data Analysis ETL
A startup called Sparkify wants to analyze the data they've been collecting on songs and user activity on their new music streaming app. The purpose of this project is to create an ETL pipeline that can use song and user logs data to create a Postgres database optimized for queries based on song plays.
# Sparkify Data
Sparkify data consist of 2 primary data sources 
songs data and user log data.
1. `Songs data` - consists of log files in JSON format.
 Each file is in JSON format and contains metadata about a song and the artist of that song. 
 The files are partitioned by the first three letters of each song's track ID. 
 For example, here are file paths to two files in this dataset.

        song_data/A/B/C/TRABCEI128F424C983.json
        song_data/A/A/B/TRAABJL12903CDCF1A.json
    And below is an example of what a single song file, `TRAABJL12903CDCF1A.json`, looks like.
        
        {
            "num_songs": 1, 
            "artist_id": "ARD7TVE1187B99BFB1", 
            "artist_latitude": null, 
            "artist_longitude": null, 
            "artist_location": "California - LA", 
            "artist_name": "Casual", 
            "song_id": "SOMZWCG12A8C13C480", 
            "title": "I Didn't Mean To", 
            "duration": 218.93179, 
            "year": 0
        }
2. `User Log Data` - consists of log files in JSON format These simulate activity logs from a music streaming app based on specified configurations. 
The log files in the dataset you'll be working with are partitioned by year and month. For example, here are filepaths to two files in this dataset.

        log_data/2018/11/2018-11-12-events.json
        log_data/2018/11/2018-11-13-events.json

    And below is an example of what the data in a log file, 2018-11-12-events.json, looks like.

        {
            "artist":null,
            "auth":"LoggedIn",
            "firstName":"Walter",
            "gender":"M",
            "itemInSession":0,
            "lastName":"Frye",
            "length":null,
            "level":"free",
            "location":"San Francisco-Oakland-Hayward, CA",
            "method":"GET",
            "page":"Home",
            "registration":1540919166796.0,
            "sessionId":38,
            "song":null,
            "status":200,
            "ts":1541105830796,
            "userAgent":"\"Mozilla\/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit\/537.36 (KHTML, like Gecko) Chrome\/36.0.1985.143 Safari\/537.36\"",
            "userId":"39"
        }


# Data Model
In this project we will use the star schema data model. The star schema is a multi-dimensional data model used to organize data in a database or data warehouse so that it is easy to understand and analyze and it's optimized for querying large data sets.

It uses a single large fact table to store transactional or measured data in this case is `songplays`:

1. `songplays` - records in log data associated with song plays i.e. records with page NextSong

        - songplay_id PRIMARY KEY
        - start_time
        - user_id
        - level
        - song_id
        - artist_id
        - session_id
        - location
        - user_agent   

And one or more smaller dimensional tables that store attributes about the data in this case we have 4 dimensional tables:

1. `users` - users in the app

        user_id PRIMARY KEY, first_name, last_name, gender, level
2. `songs` - songs in music database
        
        song_id PRIMARY KEY, title, artist_id, year, duration
3. `artists` - artists in music database
        
        artist_id PRIMARY KEY, name, location, latitude, longitude
4. `time` - timestamps of records in songplays broken down into specific units

        start_time PRIMARY KEY, hour, day, week, month, year, weekday

# ETL Pipeline
1. **Process `Song Data`:** perform ETL on the first dataset, `song_data`, to create the `songs` and `artists` dimensional tables.

    1. Use the `get_files` function to get a list of all song JSON files in `data/song_data`
    2. `Song` Table

        - Extract columns for song_id, title, artist_id, year, and duration
        - Insert Record into `Song` Table
    3. `artists` Table

        - Extract columns for artist ID, name, location, latitude, and longitude
        -  Insert Record into `Artist` Table
2. **Process `Log Data`:** perform ETL on the second dataset, `log_data`, to create the `time` and `users` dimensional tables, as well as the `songplays` fact table.

    1. Use the `get_files` function provided above to get a list of all log JSON files in `data/log_data`
    2. `time` Table

        - Filter records by `NextSong` action
        - Convert the `ts` timestamp column to datetime
        - Extract the timestamp, hour, day, week of year, month, year, and weekday from the `ts` column and set `time_data` to a list containing these values in order
        -  Create a dataframe, `time_df,` containing the time data
        - Insert Records into `Time` Table
    3. `users` Table

        - Extract columns for user ID, first name, last name, gender and level
        - Insert Records into `users` table
    4. `songplays` Table
        
        - This one is a little more complicated since information from the songs table, artists table, and original log file are all needed for the `songplays` table. 
        - The log file does not specify an ID for either the song or the artist.
        - Get the song ID and artist ID by querying the songs and artists tables to find matches based on song title, artist name, and song duration time.
        - Select the timestamp, user ID, level, song ID, artist ID, session ID, location, and user agent and set to `songplay_data`.
        - Insert Records into `Songplays` Table


# ETL Run Instructions
1. **Setup Postgres Database:**

        $ docker run --name some-postgres -e POSTGRES_PASSWORD=postgres -d postgres
2. **Install pandas and psycopg2:**

        $ pip3 insall pandas
        $ pip3 install psycopg2

3. **Create the Sparkify database and tables:**

        $ python3 create_tables.py
4. **Run the ETL pipeline:** 

        $ python3 etl.py
