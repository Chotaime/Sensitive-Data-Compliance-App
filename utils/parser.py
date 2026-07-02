from pypdf import PdfReader
import pandas as pd

def read_pdf(file):
    reader = PdfReader(file)

    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    return text


def read_txt(file):
    return file.read().decode("utf-8")


def read_csv(file):
    df = pd.read_csv(file)

    return df.to_string(index=False)