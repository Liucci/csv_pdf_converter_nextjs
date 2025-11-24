from utils.pdf_utils.table_builder import PdfTableBuilder
from utils.pdf_utils.section_writer import PdfSectionWriter
from utils.pdf_utils.document_writer import PdfDocumentWriter
from utils.pdf_utils.path_helper import PdfPathHelper
from reportlab.platypus import PageBreak
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


def export_dataframe_to_pdf(df,
                            file_path,
                            main_title=None,
                            sub_title=None,
                            header_text=None,
                            footer_text=None,
                            fontsize=6,
                            landscape_mode=False,
                            reset_index=True,
                            rows_per_page=0):
    #dfをPDFに出力する関数
    try:

        if reset_index:
            df = df.reset_index()

        builder = PdfTableBuilder(df,
                                fontsize=fontsize,
                                font_name="IPAex Gothic",
                                repeat_headers=True)
        elements = []
        writer = PdfDocumentWriter(file_path,
                                   elements=elements,
                                    main_title=main_title,
                                    sub_title=sub_title,
                                    header_text=header_text,
                                    footer_text=footer_text,
                                    font_name="IPAex Gothic",
                                    landscape_mode=landscape_mode)

        if rows_per_page > 0:
            for start in range(0, len(df), rows_per_page):
                end = start + rows_per_page
                chunk = df.iloc[start:end]
                chunk_table = PdfTableBuilder(
                                                chunk,
                                                fontsize=fontsize,
                                                font_name="IPAex Gothic",
                                                repeat_headers=True
                                                )
                elements.append(chunk_table.build_table())
                if end < len(df):  # 改ページを追加（最後のページ以外）
                    elements.append(PageBreak())
        else:
            table = builder.build_table()
            elements.append(table)

        writer.write()

    except Exception as e:
        print(f"PDFのエクスポート中にエラーが発生しました: {e}")
        return False

def export_datafram_to_pdf_each_section(df,
                                        file_path,
                                        column_name=None,
                                        note_text=None,                                        
                                        main_title=None,
                                        sub_title=None,                             
                                        header_text=None,
                                        footer_text=None,
                                        fontsize=8,
                                        landscape_mode=False,
                                        reset_index=False                                        
                                        ):
    """dfを任意の列名の固有値ごとにページ分けしてPDF出力する関数"""
    try:

        if reset_index:
            df = df.reset_index()

        # テーブル作成ビルダー
        builder = PdfTableBuilder(df,
                                  fontsize=fontsize,
                                  font_name="IPAex Gothic",
                                  repeat_headers=True)
        # セクションごとのテーブル（Flowableのリスト）
        section_tables = builder.build_table_each_section(column_name=column_name, 
                                                          note_text=note_text)
        # PDFライター
        writer = PdfDocumentWriter(file_path=file_path,
                                   elements=section_tables,  
                                   main_title=main_title,
                                    sub_title=sub_title,
                                   header_text=header_text,
                                   footer_text=footer_text,
                                   landscape_mode=landscape_mode)

        writer.write()  

    except Exception as e:
        print(f"PDFのエクスポート中にエラーが発生しました: {e}")
        return False


def build_PDFtables_to_pdf(elements,
                            file_path, 
                            main_title=None,
                            sub_title=None,
                            header_text=None,
                            footer_text=None,
                            landscape_mode=False,
                            ):
    
    try:
        PdfDocumentWriter(file_path,
                        elements=elements,
                        main_title=main_title,
                        sub_title=sub_title,
                        header_text=header_text,
                        footer_text=footer_text,
                        landscape_mode=landscape_mode,
                        font_name="IPAex Gothic").write()

    except Exception as e:
        print(f"PDFのエクスポート中にエラーが発生しました: {e}")
        return False