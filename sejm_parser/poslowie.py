from time import sleep

from pdf_extractor import PdfExtractor
from sejm_parser import SejmParser
from generic import create_backup, copy_sqlite_db_to_web
from sqlite_handler import SqliteHandler
from text_summarizer import TxtSummarizer

if __name__ == '__main__':
    print("starting poslowie parser with delay...")
    sleep(5)
    create_backup()
    sql_handler = SqliteHandler()
    sejm_parser = SejmParser()
    poslowie = sejm_parser.get_poslowie()
    sql_handler.insert_poslowie(poslowie)
    copy_sqlite_db_to_web()
    print("Done")
