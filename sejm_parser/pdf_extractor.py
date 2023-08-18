import codecs
import concurrent.futures
import datetime

import os
import pathlib
import shutil
import uuid

import pytesseract
import pdfplumber

from generic import delete_files_in_directory


class PdfExtractor:

    def __init__(self):
        self.extracted_text = ""

    def extract_text_from_raw_pdfs(self):
        print(f"starting text extraction process [{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}]")
        print("starting text extracting from the raw pdf files...")
        dir = "download/raw_pdf"
        for filename in os.listdir(dir):
            project_number = filename.replace(".pdf", "")
            f = os.path.join(dir, filename)
            if os.path.isfile(f):
                print(f"[{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] processing file: {f}")
                delete_files_in_directory("img_ocr_temp")
                # pdf = pdfplumber.open(f, laparams={"line_overlap": 0.7}, strict_metadata=True)
                with pdfplumber.open(f, laparams={"line_overlap": 0.7}, strict_metadata=True) as pdf:
                    pages = pdf.pages
                    self.extracted_text = ""
                    print(f"detected {len(pages)} pages")
                    print(f"processing pages...")
                    ct = 1
                    for p in pages:
                        self.process_page(p, ct)
                        print(f"processed page {ct}/{len(pages)} [{(ct / len(pages)) * 100}%]")
                        ct += 1
                    pdf.close()

                print(self.extracted_text)
                with codecs.open(f"download/pending/{project_number}.txt", "w", "utf-8") as f:
                    f.write(self.extracted_text)
                    print(
                        f"[{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] extracted text from {filename}")
                shutil.copy(f"download/raw_pdf/{project_number}.pdf",
                            f"download/raw_pdf_already_done/{project_number}.pdf")

        print("text has been extracted from all raw pdf files")

    def process_page(self, page, page_num):
        img_filename = f"img_ocr_temp/pdf_{str(page_num)}.png"
        img = page.to_image(resolution=300)
        img.save(img_filename)

        text = self.extract_text(img_filename)
        self.extracted_text += text + " "

    def save_image_to_list_of_images_file(self, img_path):
        images_filename = "images.txt"
        mode = "w"
        if pathlib.Path(images_filename).is_file():
            mode = "a"

        with codecs.open(images_filename, mode, "utf-8") as f:
            f.write(f"{img_path}\n")

    def extract_text(self, input_filename):
        """
        extract with use of pytesseract

                how to install tesseract on windows:
        https://stackoverflow.com/questions/46140485/tesseract-installation-in-windows
        https://codetoprosper.com/tesseract-ocr-for-windows/
        https://github.com/UB-Mannheim/tesseract/wiki
        :param input_filename:
        :return:
        """
        from encodings import cp1252
        original_decode = cp1252.Codec.decode
        cp1252.Codec.decode = lambda self, input, errors="replace": original_decode(self, input, errors)
        text = pytesseract.image_to_string(input_filename, lang='pol')
        return text
