import os
import json
import pandas as pd

def save_json_file(data, filename: str, overwrite: bool = False, folder: str = None) -> str:
    """
    DataFrame / list / dict / str を JSON 形式で指定フォルダに保存する
    """
    if folder is None:
        folder = os.path.join(os.path.dirname(__file__), "uploads")

    os.makedirs(folder, exist_ok=True)

    if not filename.lower().endswith(".json"):
        filename += ".json"

    file_path = os.path.join(folder, filename)

    if os.path.exists(file_path) and not overwrite:
        raise FileExistsError(f"File already exists: {file_path}")

    # DataFrameの場合
    if isinstance(data, pd.DataFrame):
        data.to_json(file_path, orient="records", force_ascii=False, indent=2)
        return file_path

    # list / dict / str の場合
        # list / dict / str の場合は json.dump
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return file_path
