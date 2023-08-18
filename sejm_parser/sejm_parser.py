# author: Michal Sporna
import codecs
import datetime
import os
import pathlib
import shutil

import requests

from generic import delete_files_in_directory


class SejmParser:

    def __init__(self):
        self.current_term = 9
        self.host = "https://api.sejm.gov.pl"
        self.get_all_projects_url = f"{self.host}/sejm/term{self.current_term}/prints/"

    def get_all_projects(self):
        projects = requests.get(self.get_all_projects_url)
        return projects.json()

    def get_new_projects(self):
        """
        get all projects where changeDate is > date from last_project_date.txt
        :return:
        """
        print("fetching new projects...")
        with open("last_project_date.txt", "r") as f:
            latest_saved_date = f.read()
            print(f"new projects must have been added after {latest_saved_date}...")
            latest_saved_date = datetime.datetime.strptime(latest_saved_date, "%Y-%m-%d")
        all_projects = self.get_all_projects()
        raw_new_project_dates = []
        new_projects = []
        delete_files_in_directory("download/raw_pdf")
        delete_files_in_directory("download/raw_pdf_already_done")
        for p in all_projects:
            date = datetime.datetime.strptime(p["documentDate"], "%Y-%m-%d")
            if date > latest_saved_date:
                print(f"will download {p['number']} from {p['documentDate']}")
                new_projects.append(p)
                raw_new_project_dates.append(date)
                for a in p["attachments"]:
                    if ".pdf" in a:
                        self.download_attachment(p["number"], a)
                        break
                mode = "w"
                metadata_filename = f"metadata/project_metadata-{p['number']}.txt"
                if pathlib.Path(metadata_filename).is_file():
                    mode = "a"

                with codecs.open(metadata_filename, mode, "utf-8") as f:
                    f.write(f"{p['number']};{p['title']};{p['processPrint'][0]}")

        print(f"got a list of new projects. Length: {len(new_projects)}")
        raw_new_project_dates.sort()
        if len(raw_new_project_dates) > 0:
            latest_new_project_date = raw_new_project_dates[-1]
            with open("last_project_date.txt", "w") as f:
                f.write(latest_new_project_date.strftime("%Y-%m-%d"))
            print("New projects fetched.")
        return new_projects

    def get_project_details(self, project_id):
        get_project_details_url = f"{self.host}/sejm/term{self.current_term}/prints/{project_id}"

    def refresh_metadata(self):
        print("fetching metadata for new projects...")
        delete_files_in_directory("metadata")
        with open("last_project_date.txt", "r") as f:
            latest_saved_date = f.read()
            print(f"new projects must have been added after {latest_saved_date}...")
            latest_saved_date = datetime.datetime.strptime(latest_saved_date, "%Y-%m-%d")
        all_projects = self.get_all_projects()
        for p in all_projects:
            date = datetime.datetime.strptime(p["documentDate"], "%Y-%m-%d")
            if date > latest_saved_date:
                mode = "w"
                metadata_filename = f"metadata/project_metadata-{p['number']}.txt"
                if pathlib.Path(metadata_filename).is_file():
                    mode = "a"
                with codecs.open(metadata_filename, mode, "utf-8") as f:
                    f.write(f"{p['number']};{p['title']};{p['processPrint'][0]}")

    def get_project_status(self):
        """
        [browser]
        get project number
        go to : https://www.sejm.gov.pl/Sejm9.nsf/PrzebiegProc.xsp?nr={project_number} via browser (no api for it!)
        parse the latest status
        :return:
        """
        pass  # todo

    def get_voting_details(self):
        """
        [browser]
        if process already had a vote , get details
        club - vote yay/nay
        https://www.sejm.gov.pl/Sejm9.nsf/agent.xsp?symbol=glosowania&nrkadencji=9&nrposiedzenia=12&nrglosowania=44
        :return:
        """
        pass  # todo

    def get_who_voted_and_how(self):
        """
        [browser]
        https://www.sejm.gov.pl/Sejm9.nsf/agent.xsp?symbol=glosowania&nrkadencji=9&nrposiedzenia=12&nrglosowania=44

        click on each club and get list of yay/nay voters by specific person
        :return:
        """
        pass  # todo

    def download_attachment(self, project_id, attachment_filename):
        """
        download to download/raw_pdf folder
        :return:
        """
        download_project_pdf_url = f"{self.host}/sejm/term{self.current_term}/prints/{project_id}/{attachment_filename}"
        local_filename = f"{project_id}.pdf"
        with requests.get(download_project_pdf_url, stream=True) as r:
            with open(f"download/raw_pdf/{local_filename}", "wb") as f:
                shutil.copyfileobj(r.raw, f)
        print(f"downloaded {local_filename}")
