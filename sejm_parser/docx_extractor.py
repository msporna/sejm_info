import docx2txt

def extract_text_from_docx():
    text = docx2txt.process("download/raw_pdf/3081.docx")
    print(text)