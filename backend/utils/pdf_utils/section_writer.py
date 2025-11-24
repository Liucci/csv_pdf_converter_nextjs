## pdf_utils/section_writer.py
import pandas as pd
from reportlab.platypus import Paragraph, PageBreak, Flowable
from reportlab.lib.styles import getSampleStyleSheet
from utils.pdf_utils.table_builder import PdfTableBuilder

class PdfSectionWriter:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def build_elements(self,column_name="column_name",note_text="") -> list[Flowable]:
        styles = getSampleStyleSheet()
        styles["Title"].fontName = "IPAex Gothic"
        styles["Normal"].fontName = "IPAex Gothic"
        elements = []

        for key, group in self.df.groupby(column_name):
            elements.append(Paragraph(f"{key}", styles["Title"]))
            group = group.drop(columns=[column_name])
            builder = PdfTableBuilder(group)
            elements.append(builder.build_table())
            elements.append(Paragraph(note_text, styles["Normal"]))
            elements.append(PageBreak())

        return elements
