import pandas as pd
from utils.csv_utils import csv_reader

#dfから複数の条件を指定してフィルタリングする関数
def df_filtered_by_columns(df, column_name1, column_name2, column_name3,column_unique_list1, column_unique_list2,column_unique_list3,doubling_col1_and_col3=True,marge_column3=True):
    #列名を2つ指定して、各々の列に対して、リスト内の値が含まれる行を抽出する
    df_filtered = df[
        df[column_name1].isin(column_unique_list1) & 
        df[column_name2].isin(column_unique_list2)
    ]
    """   #部分一致のパターン
    df_filtered = df[
    df[column_name1].str.contains("|".join(column_unique_list1), na=False) & 
    df[column_name2].str.contains("|".join(column_unique_list2), na=False)
    ] """


    if doubling_col1_and_col3: #doubling_col1_and_col3=trueのときはcolumn_name1とcolumn_name3の両方に重複がある場合は、重複を削除
        df_filtered=df_filtered[[column_name1, column_name3]].drop_duplicates()
    
    
    #抽出したdfから、指定した列名のデータを持つdata frameを返す
    df_filtered=df_filtered[column_unique_list3]

    if marge_column3:   #marge_column3=Trueの時は複数個ある場合１つの行にまとめる
        #column_name3が複数個ある場合は１つの行にまとめる
        df_filtered = df_filtered.groupby(column_name1)[column_name3].apply(lambda x: ', '.join(sorted(x.unique()))).reset_index()
    
    
    #df_filteredをcolumn_name1で並び替えする
    df_filtered = df_filtered.sort_values(by=column_name1, ascending=True)
    
    #print(f"df_filtered={df_filtered}")
    return df_filtered


#ファイルを指定してテスト実行
if __name__ == "__main__":
    file_path = "../PDF_converter不要ファイル/2015日本光電機器リスト生データ.csv"#相対パスでファイルを指定
    
    df=csv_reader.load_csv(file_path)
    
    column_name1= "現所在地"
    column_name2="機器名称"
    column_name3="型式"
    column_unique_list1=["新　ＭＥ室","新　ICU","新　CCU"]
    column_unique_list2=["セントラルモニタ","医用テレメータ"]
    column_unique_list3=["現所在地","型式"]
    result=df_filtered_by_columns(df, column_name1, column_name2,column_name3, column_unique_list1, column_unique_list2,column_unique_list3,doubling_col1_and_col3=True,marge_column3=True)
    print(result)