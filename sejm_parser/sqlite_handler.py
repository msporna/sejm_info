import base64
import codecs
import datetime
import os
import sqlite3

from generic import get_project_metadata, get_project_hashtags
from sqlite_schema import create_tables


class SqliteHandler:

    def __init__(self):
        create_tables(self.open_connection())
        self.term = 9

    def open_connection(self):
        connection = sqlite3.connect("sejminfo.db")
        return connection

    def close_connection(self, connection):
        connection.close()

    def does_project_exist_in_db(self, project_id):
        select_sql = "SELECT * FROM summary WHERE project_id=:pid"
        connection = self.open_connection()
        cursor = connection.cursor()
        cursor.execute(select_sql, {"pid": project_id})
        rows = cursor.fetchall()
        connection.close()
        if (len(rows)) > 0:
            return True
        else:
            return False

    def insert_processed(self):
        dir = "download/processed"
        for filename in os.listdir(dir):
            project_number = filename.replace(".txt", "")
            if self.does_project_exist_in_db(project_number):
                print(f"project {project_number} already exists in db...")
                continue
            f = os.path.join(dir, filename)
            print(f"will insert {f}")
            if os.path.isfile(f):
                title, process_id = get_project_metadata(project_number)
                hashtags = get_project_hashtags(project_number)
                print(f"inserting file: {f}")
                # long summary
                long_summary = ""
                summary = ""
                with codecs.open(f"download/twitter_lines/{project_number}.txt", "r", "utf-8") as file:
                    long_summary = file.read()
                long_summary = base64.b64encode(bytes(long_summary, 'utf-8'))
                # short summary
                with codecs.open(f, "r", "utf-8") as file:
                    summary = file.read()
                summary = base64.b64encode(bytes(summary, 'utf-8'))

                url = f'https://www.sejm.gov.pl/Sejm{self.term}.nsf/druk.xsp?nr={project_number}'
                url_process = f'https://www.sejm.gov.pl/Sejm{self.term}.nsf/PrzebiegProc.xsp?nr={process_id}'

                sql = "INSERT INTO summary(summary,project_id,date,project_url,title,hashtags,long_summary,process_id,document_date,process_url) VALUES(?,?,?,?,?,?,?,?,?,?)"
                connection = self.open_connection()
                connection.cursor().execute(sql, (
                    summary, project_number, datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), url, title,
                    hashtags, long_summary, process_id, None, url_process))
                connection.commit()
                connection.close()
                print(f"insert of {project_number} done")
        print("done inserting")
