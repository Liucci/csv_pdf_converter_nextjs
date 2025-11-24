## pdf_utils/table_builder.py
import pandas as pd
from reportlab.platypus import LongTable, TableStyle, Image, PageBreak, Flowable,Paragraph, Spacer
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from utils.pdf_utils.path_helper import PdfPathHelper
import os
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
#dfをPDFのテーブルに変換するクラス
#PDFテーブルをFlowableやParagraphで配置してPDFを生成する
class PdfTableBuilder:
    def __init__(self,
                 df: pd.DataFrame,
                 fontsize=6,
                 font_name="IPAex Gothic",
                 repeat_headers=True):
        
        self.df = df
        self.fontsize= fontsize
        self.font_name = font_name
        self.repeat_headers = repeat_headers
        
        #dfをtableに変換する際に使用するフォントを登録
        font_path = PdfPathHelper.get_absolute_path("ipaexg.ttf")  # パス解決
        pdfmetrics.registerFont(TTFont("IPAex Gothic", font_path))  # フォント登録

    def build_table(self) -> LongTable:
        #dfからtableを作成
        data = [self.df.columns.tolist()] + self.df.values.tolist()
        table = LongTable(data, repeatRows=1 if self.repeat_headers else 0)
        table.setStyle(self._get_default_style())
        return table

    def build_table_with_images(self,
                                image_column=None,
                                image_folder=None) -> LongTable:
        table_contents = [self.df.columns.tolist()]
        for _, row in self.df.iterrows():
            row_data = []
            for col in self.df.columns:
                val = row[col]
                if col == image_column and isinstance(val, str):
                    path = PdfPathHelper.get_absolute_path(os.path.join(image_folder, val), use_flask_static=True)
                    print(f"path: \n{path}")  # デバッグ用
                    if os.path.exists(path):
                        row_data.append(Image(path, width=80, height=80))
                    else:
                        row_data.append("画像なし")
                else:
                    row_data.append(str(val))
            table_contents.append(row_data)

        table = LongTable(table_contents, repeatRows=1)
        table.setStyle(self._get_default_style())
        return table

    def build_table_each_section(self, 
                                 column_name=None,
                                 note_text=None) :

        styles = getSampleStyleSheet()
      
        styles["Heading2"].fontName = self.font_name
        styles["Normal"].fontName = self.font_name
        tables = []

        for key, group in self.df.groupby(column_name):
            group = group.drop(columns=[column_name])

            # セクションタイトル追加（オプション）
            section_title = Paragraph(f"<b>{key}</b>", styles["Heading2"])
            
            tables.append(Spacer(1, 30))
            tables.append(section_title)
            tables.append(Spacer(1, 6))

            # テーブルデータ作成
            table_contents = [group.columns.tolist()] + group.values.tolist()
            table = LongTable(table_contents, repeatRows=1 if self.repeat_headers else 0)
            table.setStyle(self._get_default_style())

            tables.append(table)
            tables.append(Spacer(1, 12))  # セクション間の余白
            if note_text:
                tables.append(Paragraph(note_text, styles["Normal"]))
            tables.append(PageBreak())
        return tables  # List[Flowable]

    def _get_default_style(self):
        return TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_name),
            ('FONTSIZE', (0, 0), (-1, -1), self.fontsize),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
            ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.grey),
        ])
