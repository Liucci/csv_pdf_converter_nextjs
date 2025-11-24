## pdf_utils/document_writer.py
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Flowable
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime
from utils.pdf_utils.path_helper import PdfPathHelper

#PDFテーブルやタイトルやヘッダー・フッターを含むドキュメントを作成し配置するクラス
#ページ設定やtableやタイトル、フッター等の配置を行う
class PdfDocumentWriter:
    def __init__(self, 
                 file_path,
                 elements:list[Flowable], 
                 main_title=None, 
                 sub_title=None,
                 header_text=None,
                 footer_text=None,
                 landscape_mode=False,
                 font_name="IPAex Gothic"):
        
        self.file_path = file_path
        self.elements = elements
        self.main_title = main_title
        self.sub_title = sub_title
        self.header_text = header_text
        self.sub_title = sub_title
        self.header_text= header_text
        self.footer_text = footer_text
        self.pagesize = landscape(A4) if landscape_mode else A4
        self.font_name = font_name

        #table以外のタイトルやヘッダー・フッターに使用するフォントを登録
        font_path = PdfPathHelper.get_absolute_path("ipaexg.ttf")
        pdfmetrics.registerFont(TTFont("IPAex Gothic", font_path))

    def write(self):
        #ページサイズやマージンを設定し、各要素を配置してPDFを生成する
        doc = BaseDocTemplate(self.file_path, 
                            pagesize=self.pagesize,
                            topMargin=100,
                            bottomMargin=25, 
                            leftMargin=15,
                            rightMargin=15)
        
        frame = Frame(doc.leftMargin,
                      doc.bottomMargin,
                      doc.width,
                      doc.height,
                      id='normal')
        
        template = PageTemplate(id='header_footer',
                                frames=[frame],
                                onPage=lambda c, d: self._header_footer(c, d))
        
        doc.addPageTemplates([template])
        doc.build(self.elements)

    def _header_footer(self, canvas, doc):
        #pagesizeの大きさの入れ物に上部にヘッダー、中央にタイトル・サブタイトル、下部にフッターを配置する

        canvas.saveState()
        page_width = doc.pagesize[0]

        # ヘッダー：右上に header_text を表示
        if self.header_text:
            canvas.setFont(self.font_name, 10)
            canvas.drawRightString(page_width - doc.rightMargin, doc.height + doc.topMargin + 5, self.header_text)

        # タイトル・サブタイトル（中央寄せ）
        y = doc.height + doc.topMargin - 40
        if self.main_title:
            canvas.setFont(self.font_name, 18)
            canvas.drawCentredString(page_width / 2, y, self.main_title)
        if self.sub_title:
            canvas.setFont(self.font_name, 12)
            canvas.drawCentredString(page_width / 2, y - 20, self.sub_title)

        # フッター：右下に日付付き
        if  self.footer_text:
            canvas.setFont(self.font_name, 10)
            footer_display = f"{self.footer_text}　　作成日：{datetime.today().strftime('%Y/%m/%d')}"
            canvas.drawRightString(page_width - doc.rightMargin, 10, footer_display)

        canvas.restoreState()
