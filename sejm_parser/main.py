from time import sleep

from pdf_extractor import PdfExtractor
from sejm_parser import SejmParser
from generic import create_backup, copy_sqlite_db_to_web
from sqlite_handler import SqliteHandler
from text_summarizer import TxtSummarizer

if __name__ == '__main__':
    # print("starting sejm parser with delay...")
    # sleep(5)
    create_backup()
    sql_handler = SqliteHandler()
    sejm_parser = SejmParser()
    sejm_parser.get_all_projects_via_web_v2()

    pdf_extractor = PdfExtractor()
    pdf_extractor.extract_text_from_raw_pdfs()

    ai_summarizer = TxtSummarizer()
    ai_summarizer.process_pending_files()

    sql_handler.insert_processed()
    copy_sqlite_db_to_web()
    print("Done")
