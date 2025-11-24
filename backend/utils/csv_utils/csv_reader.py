import pandas as pd
import chardet

#元となるcsvファイルを読み込みもととなるdfを返す関数
def load_csv(file_path):
    try:
        with open(file_path, "rb") as f: #open関数でバイナリモードでファイルを開く
            result= chardet.detect(f.read())#chardet.detectでファイルの文字コードを判定
            encoding = result["encoding"]
            print(encoding)
        df=pd.read_csv(file_path,encoding=encoding)#判定した文字コードでファイルを読み込む
        return df
    except Exception as e:
        print(f"CSVの読み込みに失敗しました:{e}")
        return None

#元ファイルからヘッダー部分だけ返す関数
def read_header(file_path):
    try:
        with open(file_path, "rb") as f:
            result= chardet.detect(f.read())
            encoding = result["encoding"]
            print(encoding)
        df_head=pd.read_csv(file_path,encoding=encoding,nrows=0)
        return df_head.columns.tolist() #ヘッダー項目を取得してリストにして返す
    except Exception as e:
        print(f"CSVのヘッダー部の読み込みに失敗しました:{e}")
        return None
#ファイルの保存先を指定
