import pandas as pd
from utils.csv_utils import csv_reader



def create_pivot_df(df,subject_name1,subject_name2,list_in_subject_name1,list_in_subject_name2):
    if not subject_name1 or not subject_name2:
        print("行または列の選択がありません")
        return
    if not list_in_subject_name1 or not list_in_subject_name2:
        print("行または列内に指定の項目はありません")
        return
    try:
        # クロス集計を実行
        df_filtered=[]
        #list_in_subject_name1=df[subject_name1]
        #list_in_subject_name2=df[subject_name2]
        df_filtered = df[
                        (df[subject_name1].isin(list_in_subject_name1)) & 
                        (df[subject_name2].isin(list_in_subject_name2))
                        ]
        #print(f"df_filtered={df_filtered}")
        #print(f"list_in_subject_name1={list_in_subject_name1}")
        #print(f"list_in_subject_name2={list_in_subject_name2}")
        pivot_df = pd.pivot_table(df_filtered,index=subject_name1,columns=subject_name2,aggfunc='size',fill_value=0)       
        print("\n=== クロス集計表 ===")
        print(pivot_df)
        return pivot_df
        
    except KeyError as e:
        print(f"エラー: {e}")
        print("選択した項目がデータフレームに存在するか確認してください")
        return
    


#ファイルを指定してテスト実行
if __name__ == "__main__":
    file_path = "../PDF_converter不要ファイル/2015日本光電機器リスト生データ.csv"#相対パスでファイルを指定
    
    df=csv_reader.load_csv(file_path)
    
    subject_name1= "現所在地"
    subject_name2="機器名称"
    list_in_subject_name1=["新　ＭＥ室","新　ICU","新　CCU"]
    list_in_subject_name2=["送信機","ベッドサイドモニタ"]
    result=create_pivot_df(df,subject_name1,subject_name2,list_in_subject_name1,list_in_subject_name2)
    #print(result)
    #print(type(result))
