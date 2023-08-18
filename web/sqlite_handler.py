import base64
import datetime
import sqlite3


class SqliteHandler:

    def open_connection(self):
        connection = sqlite3.connect("sejminfo.db")
        print(sqlite3.version)
        return connection

    def close_connection(self, connection):
        connection.close()

    def get_summaries(self):
        connection = self.open_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM summary")
        rows = cursor.fetchall()
        connection.close()
        # wrap it
        summaries = []
        for r in rows:
            summaries.append(
                {"id": r[0], "summary": base64.b64decode(r[1]).decode("utf-8", "ignore"), "project_id": r[2],
                 "added_date_str": r[3].replace("-", "/"),
                 "added_date": datetime.datetime.strptime(r[3], "%Y-%m-%d %H:%M:%S"),
                 "url": r[4],
                 "title": r[5], "hashtags": r[6], "long_summary": base64.b64decode(r[7]).decode("utf-8", "ignore"),
                 "process_id": r[8], "document_date": r[9], "process_url": r[10]})
        summaries = sorted(summaries, key=lambda d: d["added_date"], reverse=True)
        return summaries
