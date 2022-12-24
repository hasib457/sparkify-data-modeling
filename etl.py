import glob
import os

import pandas as pd
import psycopg2

from sql_queries import *


def process_song_file(cur, filepath):
    """
    Process songs data files
    - Load songs file as pandas DataFrame
    - Extract song atrributes and insert in songs table
        - [song_id, title, artist_id, year, duration]
    - Extract artist atrributes and insert in artists table
        - [ artist_id, name, location, latitude, longitude ]
    """
    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert song record
    song_data = df[
        ["song_id", "title", "artist_id", "year", "duration"]
    ].values.tolist()[0]
    cur.execute(song_table_insert, song_data)

    # insert artist record
    artist_data = df[
        [
            "artist_id",
            "artist_name",
            "artist_location",
            "artist_latitude",
            "artist_longitude",
        ]
    ].values.tolist()[0]
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """
    Process user log files
    - Load logs as a pandas DataFrame
    - Extract user time attributes and insert it in time table
        - [start_time, hour, day, week, month, year, weekday]
    - Extract user data and insert it users table
        - [user_id, first_name, last_name, gender, level]
    - Extract user-listing songs attrebutes and insert it in songplays table
        - [songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent]
    """
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df["page"] == "NextSong"]

    # convert timestamp column to datetime
    t = pd.to_datetime(df["ts"], unit="ms")

    # insert time data records
    time_data = [
        t,
        t.dt.hour,
        t.dt.day,
        t.dt.isocalendar().week,
        t.dt.month,
        t.dt.year,
        t.dt.weekday,
    ]
    column_labels = ("start_time", "hour", "day", "week", "month", "year", "weekday")
    time_df = pd.DataFrame(list(zip(*time_data)), columns=column_labels)

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[["userId", "firstName", "lastName", "gender", "level"]]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():

        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()

        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        start_date = pd.to_datetime(row.ts, unit="ms")
        songplay_data = (
            start_date,
            row.userId,
            row.level,
            songid,
            artistid,
            row.sessionId,
            row.location,
            row.userAgent,
        )
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):

    """
    - Traverse file system to get data files
    - Apply the processing function to each file
    - Commit transactions
    - INUPT:
        - Connection cursor
        - Database connection
        - Data path
        - Processing function
    """
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, "*.json"))
        for f in files:
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print("{} files found in {}".format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print("{}/{} files processed.".format(i, num_files))


def main():
    """
    - Establishes connection with the sparkify database and gets
    cursor to it.
    - Process user logs and songs data
    - Finally, closes the connection.
    """
    conn = psycopg2.connect(
        "host=127.0.0.1 dbname=sparkifydb user=student password=student"
    )
    # conn = psycopg2.connect(
    #     "host=172.17.0.2 user=postgres password=postgres dbname=sparkifydb"
    # )

    cur = conn.cursor()

    process_data(cur, conn, filepath="data/song_data", func=process_song_file)
    process_data(cur, conn, filepath="data/log_data", func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()
