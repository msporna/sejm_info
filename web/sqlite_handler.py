import base64
import datetime
import os
import sqlite3


class SqliteHandler:

    def open_connection(self):
        connection = sqlite3.connect("sejminfo.db")
        print(sqlite3.version)
        return connection

    def close_connection(self, connection):
        connection.close()

    def get_poslowie(self):
        self.delete_images()
        connection = self.open_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM poslowie")
        rows = cursor.fetchall()
        connection.close()
        poslowie_by_club = {}
        poslowie = []

        for r in rows:

            poslowie.append(
                {"id": r[0], "name": r[1], "club": r[2], "dob": r[3], "education": r[4], "district_name": r[5],
                 "number_of_votes": r[6], "place_of_birth": r[7],
                 "photo": base64.b64decode(r[8]).decode("utf-8", "ignore"), "posel_id": r[9]})

            with open(f"static/images/poslowie/{r[0]}.png", "wb") as fh:
                fh.write(base64.decodebytes(r[8]))

            club = r[2]
            district = r[5]
            if poslowie_by_club.get(club):
                if poslowie_by_club[club].get(district):
                    poslowie_by_club[club][district].append(
                        {"id": r[0], "name": r[1], "club": r[2], "dob": r[3], "education": r[4], "district_name": r[5],
                         "number_of_votes": r[6], "place_of_birth": r[7],
                         "photo": base64.b64decode(r[8]).decode("utf-8", "ignore"), "posel_id": r[9]})
                else:
                    poslowie_by_club[club][district] = []
                    poslowie_by_club[club][district].append(
                        {"id": r[0], "name": r[1], "club": r[2], "dob": r[3], "education": r[4], "district_name": r[5],
                         "number_of_votes": r[6], "place_of_birth": r[7],
                         "photo": base64.b64decode(r[8]).decode("utf-8", "ignore"), "posel_id": r[9]})
            else:
                poslowie_by_club[club] = {district: []}
                poslowie_by_club[club][district].append(
                    {"id": r[0], "name": r[1], "club": r[2], "dob": r[3], "education": r[4], "district_name": r[5],
                     "number_of_votes": r[6], "place_of_birth": r[7],
                     "photo": base64.b64decode(r[8]).decode("utf-8", "ignore"), "posel_id": r[9]})

        # sort
        temp = list(poslowie_by_club.keys())
        temp.sort()
        poslowie_by_club = {i: poslowie_by_club[i] for i in temp}

        for k, v in poslowie_by_club.items():
            temp = list(v.keys())
            temp.sort()
            poslowie_by_club[k] = {i: v[i] for i in temp}
        return poslowie_by_club, poslowie

    def delete_images(self):
        dir_path = "static/images/poslowie"
        try:
            files = os.listdir(dir_path)
            for file in files:
                file_path = os.path.join(dir_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print(f"All files from {dir_path} deleted successfully.")
        except:
            print(f"Couldn't delete from {dir_path}. Probably already clean...")

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
                 "process_id": r[8], "document_date": r[9], "process_url": r[10], "submitting_party": r[11]})
            summaries = sorted(summaries, key=lambda d: d["added_date"], reverse=True)
        return summaries
