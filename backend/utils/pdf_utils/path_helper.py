## pdf_utils/path_helper.py
import os
import sys

from flask import current_app

class PdfPathHelper:
    @staticmethod
    def get_absolute_path(relative_path: str, use_flask_static: bool = False) -> str:
        if use_flask_static:
            # Flaskのstaticフォルダを基準に解決
            base_path = os.path.join(current_app.root_path, "static", )
        else:
            try:
                base_path = sys._MEIPASS
            except AttributeError:
                base_path = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(base_path, relative_path).replace("\\", "/")
