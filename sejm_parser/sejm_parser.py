# author: Michal Sporna
import base64
import codecs
from playwright.sync_api import sync_playwright
import pathlib
import shutil
from datetime import datetime
import requests

from generic import delete_files_in_directory


class SejmParser:

    def __init__(self):
        self.current_term = 10
        self.host = "https://api.sejm.gov.pl"
        self.get_all_projects_url = f"{self.host}/sejm/term{self.current_term}/prints/"

    def get_all_projects_via_web_v2(self):
        uchwaly = 'https://www.sejm.gov.pl/sejm10.nsf/druki.xsp?view=3&typ=projekt%20uchwa%C5%82y'
        ustawy = 'https://www.sejm.gov.pl/sejm10.nsf/druki.xsp?view=3&typ=projekt%20ustawy&page=1'

        with open("last_project_date.txt", "r") as f:
            latest_saved_date = f.read()
            print(f"looking for new projects added after {latest_saved_date}...")
            latest_saved_date = datetime.strptime(latest_saved_date.strip(), "%Y-%m-%d")

        delete_files_in_directory("download/raw_pdf")
        delete_files_in_directory("download/raw_pdf_already_done")
        delete_files_in_directory("metadata")

        table_data = self.parse_and_download_pdf_via_web(uchwaly, latest_saved_date, 'uchwala')
        self.download_pdfs_via_chrome(table_data, "uchwala")

        table_data = self.parse_and_download_pdf_via_web(ustawy, latest_saved_date, 'ustawa')
        self.download_pdfs_via_chrome(table_data, "ustawa")

        print(f'setting last project date to {datetime.now().strftime("%Y-%m-%d")}')
        with open("last_project_date.txt", "w") as f:
            f.write(datetime.now().strftime("%Y-%m-%d"))

    def parse_and_download_pdf_via_web(self, url, latest_saved_date, type):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto(url, timeout=120000)

            # Wait for the results or perform further actions as needed
            page.wait_for_selector('.table.border-bottom')

            table_rows = page.query_selector_all('table.table.border-bottom tbody tr')
            table_data = []

            for row in table_rows:
                columns = row.query_selector_all('td')
                nr_druku = columns[0].text_content().strip()
                data_pisma = datetime.strptime(columns[1].text_content().strip(), "%Y-%m-%d")
                doc_date = datetime.strptime(columns[1].text_content().strip(), "%Y-%m-%d")
                if doc_date > latest_saved_date:
                    tytul = columns[2].text_content().strip()
                    link = f"https://www.sejm.gov.pl/Sejm{self.current_term}.nsf/{columns[2].query_selector('a').get_attribute('href')}"
                    tuple_data = (nr_druku, data_pisma, tytul, link)
                    table_data.append(tuple_data)

                    mode = "w"
                    metadata_filename = f"metadata/project_metadata-{nr_druku}_{type}.txt"
                    if pathlib.Path(metadata_filename).is_file():
                        mode = "a"

                    with codecs.open(metadata_filename, mode, "utf-8") as f:
                        f.write(f"{nr_druku}_{type};{tytul};{data_pisma}")

            print(f"detected the following projects {len(table_data)}:")
            print(table_data)  # Output the extracted data

            browser.close()
        return table_data

    def get_all_projects_via_web(self):

        with open("last_project_date.txt", "r") as f:
            latest_saved_date = f.read()
            print(f"looking for new projects added after {latest_saved_date}...")
            latest_saved_date = datetime.strptime(latest_saved_date.strip(), "%Y-%m-%d")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto(
                f'https://www.sejm.gov.pl/Sejm{self.current_term}.nsf/druki.xsp?view=S')

            # Step 1: Select value 'jest po' in the dropdown
            page.select_option('#view\\:_id1\\:_id2\\:facetMain\\:_id123\\:_id124\\:_id127\\:cdrData\\:cbData',
                               'jest po')

            # Step 2: Fill the date input
            page.fill('#view\\:_id1\\:_id2\\:facetMain\\:_id123\\:_id124\\:_id127\\:cdrData\\:dtpData1',
                      latest_saved_date.strftime('%Y-%m-%d'))

            # Step 3: Select 'projekt ustawy' and 'projekt uchwały' while holding Ctrl
            # JavaScript code to select multiple options in a multi-select dropdown
            select_script = """
                 (selectId) => {
                     const select = document.getElementById(selectId);
                     const options = select.options;
                     for (let i = 0; i < options.length; i++) {
                         if (options[i].value === 'projekt ustawy' || options[i].value === 'projekt uchwały') {
                             options[i].selected = true;
                         }
                     }
                     const event = new Event('change', { bubbles: true });
                     select.dispatchEvent(event);
                 }
                 """

            # Execute the JavaScript code to select 'projekt ustawy' and 'projekt uchwały'
            page.evaluate(select_script, 'view:_id1:_id2:facetMain:_id123:_id124:_id127:lbxrodzaj')

            # Step 4: Click the 'Szukaj' button
            page.click('text=Szukaj')

            # Wait for the results or perform further actions as needed
            page.wait_for_selector('.table.border-bottom')

            table_rows = page.query_selector_all('table.table.border-bottom tbody tr')
            table_data = []

            for row in table_rows:
                columns = row.query_selector_all('td')
                nr_druku = columns[0].text_content().strip()
                data_pisma = columns[1].text_content().strip()
                tytul = columns[2].text_content().strip()
                link = f"https://www.sejm.gov.pl/Sejm{self.current_term}.nsf/{columns[2].query_selector('a').get_attribute('href')}"
                tuple_data = (nr_druku, data_pisma, tytul, link)
                table_data.append(tuple_data)

            print(f"detected the following projects {len(table_data)}:")
            print(table_data)  # Output the extracted data

            browser.close()
        print(f'setting last project date to {datetime.now().strftime("%Y-%m-%d")}')
        with open("last_project_date.txt", "w") as f:
            f.write(datetime.now().strftime("%Y-%m-%d"))
        self.download_pdfs_via_chrome(table_data)

    def download_pdfs_via_chrome(self, data, type):
        print("starting to download the projects...")
        for d in data:
            pdf_filename = f'{d[0]}_{type}.pdf'
            print(f"downloading {pdf_filename}")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                page.goto(d[3], timeout=120000)
                page.wait_for_load_state("load")
                # Extract the URL of the PDF file
                # link = page.locator(f'//a[normalize-space(text()) = "{pdf_filename}"]')
                link = page.locator("a[href$='.pdf']").first
                if link:
                    href = link.get_attribute("href")
                    self.download_pdf(href, f"download/raw_pdf/{pdf_filename}")

                browser.close()

    def download_pdf(self, url, filename):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filename, 'wb') as pdf_file:
                for chunk in response.iter_content(1024):
                    pdf_file.write(chunk)
            print(f"PDF downloaded successfully as '{filename}'.")
        else:
            print("Failed to download PDF.")

    ########################################################################
    #
    # OLD APPROACH VIA API
    #
    ########################################################################

    def get_all_projects(self):
        projects_response = requests.get(self.get_all_projects_url)
        if projects_response.status_code >= 200 and projects_response.status_code < 300:
            return projects_response.json()
        else:
            print(f"response from sejm is {projects_response.status_code}")
            return []

    def get_new_projects(self):
        """
        get all projects where changeDate is > date from last_project_date.txt
        :return:
        """
        print("fetching new projects...")
        with open("last_project_date.txt", "r") as f:
            latest_saved_date = f.read()
            print(f"new projects must have been added after {latest_saved_date}...")
            latest_saved_date = datetime.datetime.strptime(latest_saved_date.strip(), "%Y-%m-%d")
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

    def get_poslowie(self):
        print("getting poslowie...")
        get_all_poslowie_url = f"{self.host}/sejm/term{self.current_term}/MP"
        poslowie_raw = requests.get(get_all_poslowie_url).json()
        poslowie = []
        for p in poslowie_raw:
            if p.get('active'):
                print(f"processing {p.get('firstLastName')}")
                img_url = f"{self.host}/sejm/term{self.current_term}/MP/{p.get('id')}/photo"
                p["photo"] = base64.b64encode(requests.get(img_url).content)
                poslowie.append(p)
        print("done getting poslowie...")
        return poslowie

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
