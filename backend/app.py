from flask import Flask, request, render_template, redirect, url_for, session,send_from_directory,send_file, jsonify, after_this_request
import os
import pandas as pd
import tempfile
from datetime import datetime, timedelta
from flask_session import Session  # ← 追加
from utils.csv_utils import csv_reader, df_filtered_by_columns, create_pivot_df
from utils.pdf_utils import export_pdf
from utils.pdf_utils.table_builder import PdfTableBuilder
from utils.pdf_utils.table_horizontal import TableHorizontal
from utils.save_files import save_json_file
from io import StringIO,BytesIO
from flask_cors import CORS
import shutil
import uuid


app =Flask(__name__)
# --- CORS 設定 ---
# 本番の Next.js ドメインを指定
CORS(app, supports_credentials=True, origins=[
    "https://csv-pdf-converter-nextjs-1.onrender.com",
    "https://csv-pdf-converter-nextjs.onrender.com",
    "http://localhost:3000",
    "http://10.132.154.86:3000"
     # 開発用
])


#uploadsフォルダの設定
# backend フォルダを基準に uploads フォルダのパスを指定
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-for-local")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['DEBUG'] = True


# --- 起動時クリーニング ---

def cleanup_startup():
    try:
        folder = app.config['UPLOAD_FOLDER']  # 単一フォルダ
        # フォルダがなければ作成
        os.makedirs(folder, exist_ok=True)

        # 中身を削除（フォルダは残す）
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
            print(f"[CLEAN] removed: {file_path}")
    except Exception as e:
            print(f"[CLEAN] failed to delete {file_path}: {e}")

# Flask 起動前に呼ぶ
cleanup_startup()

@app.route("/ping", methods=["GET", "OPTIONS"])
def ping():
    return jsonify({"status": "ok"}), 200


@app.route("/upload", methods=["POST"])
def upload():
    try:
        #Next.jsから送信されたファイルを取得
        file = request.files["file"]
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        #元のCSVファイルをuploadsフォルダに保存
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(save_path)

        # df を uploads フォルダに JSON で保存
        df = csv_reader.load_csv(save_path)
        save_json_file(df, "df", overwrite=True, folder=app.config['UPLOAD_FOLDER'])
        return jsonify({"message": "dfを保存しました"}), 200

    except Exception as e:
        return jsonify({"error": f"Error processing upload: {str(e)}"}), 500

@app.route("/manual_filter", methods=["POST"])
def manual_filter():
    try:
        df_path = os.path.join(app.config['UPLOAD_FOLDER'], "df.json")
        if df_path is None:
            return jsonify({"error": "dfが無い"}), 400
            
        else:
            #pathからdfを取得
            df = pd.read_json(df_path, orient="records")
            print(f"df:{df.head(5)}")

            #コンテナ１に表示させる列名リスト
        columns_name_list_1 = df.columns.tolist()
        print("columns_name_list_1:")
        for a in columns_name_list_1:
            print(f"・{a}")
        return jsonify({"columns": columns_name_list_1}), 200
    except Exception as e:
        return jsonify({"error": f"Error processing manual_filter: {str(e)}"}), 500

@app.route("/selected_cb1", methods=["POST"])
def selected_cb1_route():
    try:
        # uploadsから df.json を取得
        df_path = os.path.join(app.config['UPLOAD_FOLDER'], "df.json")
        if df_path is None:
            return jsonify({"error": "dfが無い"}), 400
        
        df = pd.read_json(df_path, orient="records")

        # Next.jsで選択された列名リストを取得
        selected_cb1 = request.json.get("selected_cb1", [])

        # リストが空の場合
        if not selected_cb1:
            return jsonify({"error": "selected_cb1 が空です"}), 400

        # コンソール出力
        print("selected_cb1:")
        for col in selected_cb1:
            print(f"・{col}")

        # フィルタリング
        filtered_df1 = df[selected_cb1]
        print(f"filtered_df1:\n{filtered_df1.head(5)}")
   
        # filtered_df1をuploadsに保存
        save_json_file(filtered_df1, "filtered_df1", overwrite=True, folder=app.config['UPLOAD_FOLDER'])
        return jsonify({
                            "message": "filtered_df1を保存しました",
                            "selected_cb1": selected_cb1
                        }), 200

    except Exception as e:
        return jsonify({"error": f"Error processing selected_cb1: {str(e)}"}), 500
    
@app.route("/dropdown_value1", methods=["POST"])
def dropdown_value1():
    try:
        dropdown_value1= request.json.get("dropdown_value1", "")
        if not dropdown_value1:
            return jsonify({"error": "dropdown_value1 が空です"}), 400
        # dropdown_value1をuploadsに保存
        save_json_file(dropdown_value1, "dropdown_value1", overwrite=True,folder=app.config['UPLOAD_FOLDER'])

        print(f"選択されたドロップダウン1の値: {dropdown_value1}")
        # uploadsから filtered_df1.json を取得
        filtered_df1_path = os.path.join(app.config['UPLOAD_FOLDER'], "filtered_df1.json")
        if filtered_df1_path is None:
            return jsonify({"error": "filtered_df1が無い"}), 400
        
        filtered_df1 = pd.read_json(filtered_df1_path, orient="records")
        if filtered_df1 is None:
            return jsonify({"error": "filtered_df1 is None"}), 400
        # dropdown_value1列のユニークな値を取得
        unique_values1 = filtered_df1[dropdown_value1].unique().tolist()
        print("unique_values1:")
        for val in unique_values1:
            print(f"・{val}")
        save_json_file(unique_values1, "unique_values1", overwrite=True, folder=app.config['UPLOAD_FOLDER'])
        return jsonify({"message": "unique_values1を保存しました",
            "unique_values1": unique_values1}), 200
    except Exception as e:
        return jsonify({"error": f"Error processing dropdown_value1: {str(e)}"}), 500
    
@app.route("/selected_cb2", methods=["POST"])
def selected_cb2():
    try: 
        #Next.jsで選択された行名リストを取得
        selected_cb2 = request.json.get("selected_cb2", [])
        print("selected_cb2:")
        for row in selected_cb2:
            print(f"・{row}")

        #uploadsからfiltered_df1を取得
        filtered_df1_path = os.path.join(app.config['UPLOAD_FOLDER'], "filtered_df1.json")
        print(f"filtered_df1_path:{filtered_df1_path}")
        if filtered_df1_path is None:
            return jsonify({"error": "filtered_df1が無い"}), 400
        filtered_df1 = pd.read_json(filtered_df1_path, orient="records")
        print(f"filtered_df1:{filtered_df1.head(5)}")
        
        dropdown_value1_path = os.path.join(app.config['UPLOAD_FOLDER'], "dropdown_value1.json")
        if dropdown_value1_path is None:
            return jsonify({"error": "dropdown_value1が無い"}), 400
        dropdown_value1 = pd.read_json(dropdown_value1_path, typ='records')

        # 選択された行名でフィルタリング
        #dropdown_value1はDataFrame型なのでilocで値を取り出す
        filtered_df2 = filtered_df1[filtered_df1[dropdown_value1.iloc[0]].isin(selected_cb2)]
        #print(f"dropdown_value1:{dropdown_value1}")
        #print(f"selected_cb2:{selected_cb2}")
        #print(filtered_df1[dropdown_value1].isin(selected_cb2))
        print(f"filtered_df2{filtered_df2.head(5)}")
        # フィルタリングした DataFrame をuploadsに保存
        save_json_file(filtered_df2, "filtered_df2", overwrite=True, folder=app.config['UPLOAD_FOLDER'])
        return jsonify({"message": "filtered_df2を保存しました"}), 200 
    except Exception as e:
        return jsonify({"error": f"Error processing selected_cb2: {str(e)}"}), 500

@app.route("/dropdown_value2", methods=["POST"])
def dropdown_value2():
    try:
        # Next.jsで選択されたドロップダウン2の値を取得
        dropdown_value2= request.json.get("dropdown_value2", "")
        if not dropdown_value2:
            return jsonify({"error": "dropdown_value2 が空です"}), 400
        # uploadsに保存
        save_json_file(dropdown_value2, "dropdown_value2", overwrite=True, folder=app.config['UPLOAD_FOLDER'])
        print(f"dropdown_value2: {dropdown_value2}")

        # セッションからフィルタリングされた DataFrame を取得
        filtered_df2_path = os.path.join(app.config['UPLOAD_FOLDER'], "filtered_df2.json")
        if filtered_df2_path is None:
            return jsonify({"error": "No filtered_df2 found in session"}), 400
        filtered_df2 = pd.read_json(filtered_df2_path, orient="records")
        print(f"filtered_df2:{filtered_df2}")

        # dropdown_value2列のユニークな値を取得
        unique_values2 = filtered_df2[dropdown_value2].unique().tolist()
        
        if unique_values2:
            print(f"unique_values2:\n")
            for val in unique_values2:
                print(f"・{val}")
            # unique_values2をuploadsに保存
            save_json_file(unique_values2, "unique_values2", overwrite=True, folder=app.config['UPLOAD_FOLDER'])
            return jsonify({"unique_values2": unique_values2}), 200
        else:
            return jsonify({"error": "unique_value2は空です"}), 400
    except Exception as e:
        return jsonify({"error": f"Error processing dropdown_value2: {str(e)}"}), 500
@app.route("/selected_cb3", methods=["POST"])
def selected_cb3():
    try:
        # Next.jsで選択された行名リスト3を取得
        selected_cb3 = request.json.get("selected_cb3", [])
        print("選択された行名リスト3:")
        for row in selected_cb3:
            print(f"・{row}")

        # uploadsからfilteded_df2とdropdown_value2を取得
        filtered_df2_path = os.path.join(app.config['UPLOAD_FOLDER'], "filtered_df2.json")
        if filtered_df2_path is None:
            return jsonify({"error": "filtered_df2が無い"}), 400
        filtered_df2 = pd.read_json(filtered_df2_path, orient="records")
        dropdown_value2_path = os.path.join(app.config['UPLOAD_FOLDER'], "dropdown_value2.json")
        if dropdown_value2_path is None:
            return jsonify({"error": "dropdown_value2が無い"}), 400
        dropdown_value2 = pd.read_json(dropdown_value2_path, typ='records')
        print(f"dropdown_value2:{dropdown_value2}")

        # 選択された行名でフィルタリング
        #dropdown_value2はDataFrame型なのでilocで値を取り出す
        filtered_df3 = filtered_df2[filtered_df2[dropdown_value2.iloc[0]].isin(selected_cb3)]
        print(f"filtered_df3{filtered_df3.head(5)}")
        # フィルタリングした DataFrame をuploadsに保存
        save_json_file(filtered_df3, "filtered_df3", overwrite=True, folder=app.config['UPLOAD_FOLDER'])
        return jsonify({"message": "filtered_df3を保存しました"}), 200
    except Exception as e:
        return jsonify({"error": f"Error processing selected_cb3: {str(e)}"}), 500

@app.route("/set_column_order", methods=["POST"])
def set_column_order():
    data = request.get_json()
    order = data.get("order", [])
    
    filtered_df3_path = os.path.join(app.config['UPLOAD_FOLDER'], "filtered_df3.json")
    if filtered_df3_path is None:
        print("filtered_df3.jsonが無い")
        return jsonify({"error": "filtered_df3が無い"}), 400
    
    filtered_df3 = pd.read_json(filtered_df3_path, orient="records")

    valid_cols = [c for c in order if c in filtered_df3.columns]
    remaining_cols = [c for c in filtered_df3.columns if c not in valid_cols]

    new_order = valid_cols + remaining_cols
    filtered_df3_sorted = filtered_df3[new_order]
    print(f"filtered_df3_sorted:\n{filtered_df3_sorted.head(5)}")
    save_json_file(filtered_df3_sorted, "filtered_df3_sorted", overwrite=True, folder=app.config['UPLOAD_FOLDER'])
    return jsonify({"message": "filtered_df3_sortedを保存しました"}), 200


@app.route("/filtered_df3_sorted_pdf", methods=["POST", "OPTIONS"])
def filtered_df3_sorted_pdf():
    # OPTIONS に応答（プリフライト用）
    if request.method == "OPTIONS":
        return "", 200

    # セッションからフィルタリングされた DataFrame を取得

    filtered_df3_sorted_path = os.path.join(app.config['UPLOAD_FOLDER'], "filtered_df3_sorted.json")
    if filtered_df3_sorted_path is None:
        print("filtered_df3_sorted.jsonが無い")
        return jsonify({"error": "filtered_df_sorted3が無い"}), 400
    filtered_df3_sorted = pd.read_json(filtered_df3_sorted_path, orient="records")

    try:
        # 一時ファイルとしてPDFを作成し、そのパスを取得
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            pdf_path = tmp.name

        export_pdf.export_dataframe_to_pdf(
            filtered_df3_sorted,
            pdf_path,
            reset_index=False,
            fontsize=9,
            main_title="抽出結果一覧表",
            sub_title=None,
            header_text=None,
            footer_text="集中管理部",
            landscape_mode=True,
            rows_per_page=20
        )
        print(f"PDFが正常に作成されました（tempfile）: {pdf_path}")

        # 送信中のファイルを同じタイミングで削除すると問題が発生するため、後で削除するように設定
        # ファイルをメモリに読み込む
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        # 一時ファイルを削除
        os.remove(pdf_path)
        # BytesIO を使って送信
        #JS側でもBytesIOで受け取るようにする
        return send_file(
            BytesIO(pdf_bytes),
            as_attachment=True,
            download_name="filtered_df3_sorted.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print(f"PDF生成中にエラー: {e}")
        return "PDFの生成中にエラーが発生しました", 500

@app.route("/central_alarm", methods=["POST"])
def central_alarm():
    try:
        # uploadsからdfを取得
        df_path = os.path.join(app.config['UPLOAD_FOLDER'], "df.json")
        if df_path is None:
            return jsonify({"error": "dfが無い"}), 400
        df=pd.read_json(df_path, orient="records")
        print(f"df:{df.head(1)}")
        #特定のデータを除外する
        df_exclude= df[~df["ME.No"].str.contains("貸出",na=False)
                        &~df["現所在地"].str.contains("臨床工学室|手術室|新　ＭＥ室",na=False)
                        ]
        print(f"df_exclude:{df_exclude.head(1)}")

        column_name1="現所在地"
        column_name2="機器名称"
        column_name3="型式"
        column_unique_list1=["新　西2階","新　西4階","新　西5階","新　西6階","新　西7階","新　東3階","新　東3階(救急)","HCU","新　東4階(小児科)","新　NICU",
                                "HCU","新　東4階(産婦人科)","新　東5階","新　東6階","新　東7階","新　SCU","新　CCU","新　臨床工学室",
                                "新　ＭＥ室","新　ICU","新　CT室","新　内視鏡室","新　化学療法室","新　運動療法室","新　中央処置室","新　外来A","新　外来B","新　外来C","新　外来D",
                                "血液浄化センター","新　手術室","新　救急外来","初療室","新　内視鏡室"]
        #column_unique_list2=["送信機","ベッドサイドモニタ","セントラルモニタ","医用テレメータ"]
        column_unique_list3=["セントラルモニタ","セントラルモニター","医用テレメータ","医用テレメーター"]
        column_unique_list4=["現所在地","型式"]

        central_df = df_filtered_by_columns.df_filtered_by_columns(df_exclude, column_name1, 
                                                                    column_name2, column_name3, 
                                                                    column_unique_list1, 
                                                                    column_unique_list3, 
                                                                    column_unique_list4,
                                                                    doubling_col1_and_col3= False,
                                                                    marge_column3=False)
        
        print(f"central_df before cleaning:\n{central_df.head(1)}")

        central_df["現所在地"] = central_df["現所在地"].str.replace(r"新　東4階(小児科)", "東4小児", regex=False)
        central_df["現所在地"] = central_df["現所在地"].str.replace(r"新　東4階(産婦人科)", "東4産", regex=False)
        central_df["現所在地"] = central_df["現所在地"].str.replace(r"新　東3階(救急)", "東3", regex=False)
        central_df["現所在地"] = central_df["現所在地"].str.replace("血液浄化センター", "血液浄化センター", regex=True)
        central_df["現所在地"] = central_df["現所在地"].str.replace("新　化学療法室", "化学療法室", regex=True)
        central_df["現所在地"] = central_df["現所在地"].str.replace("新　運動療法室", "運動療法室", regex=True) 
        central_df["現所在地"] = central_df["現所在地"].str.replace("新　|階", "", regex=True)  
        #行の並び替え
        central_df = central_df.sort_values(by=["現所在地", "型式"])
        #indexのリセット
        central_df = central_df.reset_index(drop=True)   
        # uploadsにcentral_dfを保存
        save_json_file(central_df, "central_df", overwrite=True, folder=app.config['UPLOAD_FOLDER'])
        print(f"central_df{central_df.head(5)}")

        return jsonify({
            "message": "central_df created",
            "central_df": central_df.to_dict(orient="records")
        }), 200
    except Exception as e:
        return jsonify({"error": f"Error processing central_alarm: {str(e)}"}), 500

@app.route('/make_central_alarm_df', methods=['POST' , 'OPTIONS'])
def make_central_alarm_df():
    try:
            # OPTIONS に応答（プリフライト用）
        if request.method == "OPTIONS":
            return "", 200
        # central_df をuploadsから取得
        central_df_path= os.path.join(app.config['UPLOAD_FOLDER'], "central_df.json")
        if central_df_path is None:
            return jsonify({"error": "central_dfが無い"}), 400
        central_df= pd.read_json(central_df_path, orient="records")


        data = request.get_json()
        volume_list = data.get("volume")
        delete_rows = data.get("delete_rows")
        print(f"Received volume_list: {volume_list}")
        print(f"Received delete_rows: {delete_rows}")

        # 2. 音量を反映
        if volume_list:
            central_df["音量"] = volume_list
        else:
            central_df["音量"] = ""

        # 3. 削除行
        if delete_rows:
            central_df = central_df.drop(delete_rows)

        # 4. 画像列追加
        image_dict = {
                'MU-960R': 'MU-960R.jpg',
                'PU-621R': 'PU-600R.jpg',
                'PU-611R': 'PU-600R.jpg',
                'CNS-2101': 'CNS-2101.jpg',
                'CNS-9701': 'CNS-9701.jpg',
                'WEP-4204': 'WEP-4000.jpg',
                'WEP-4202': 'WEP-4000.jpg',
                'WEP-5204': 'WEP-5000.jpg',
                'WEP-5208': 'WEP-5000.jpg',
                'WEP-1450': 'WEP-1400.jpg',
                'WEP-1200': 'WEP-1200.jpg',
                'BSM-3400': 'BSM-3400.jpg',
                'PIC iX': 'PIC-iX.jpg',
                'Safty net': 'Safty-net.jpg',
            }
        # 型式ごとの画像ファイル名を取得し、DataFrameに追加
        central_df['画像'] = central_df['型式'].map(image_dict).fillna('')

        # --- ここで central_alarm_df が完成 ---
        central_alarm_df = central_df.copy()
        # uploadsにcentral_alarm_dfを保存
        save_json_file(central_alarm_df, "central_alarm_df", overwrite=True, folder=app.config['UPLOAD_FOLDER'])
        print(f"central_alarm_df:\n{central_alarm_df.head(5)}")

        return export_central_alarm_pdf()
    except Exception as e:
        return jsonify({"error": f"Error processing make_central_alarm_df: {str(e)}"}), 500

@app.route('/export_central_alarm_pdf', methods=['GET'])
def export_central_alarm_pdf():
    # セッションから central_alarm_df を復元
    central_alarm_df_path = os.path.join(app.config['UPLOAD_FOLDER'], "central_alarm_df.json")
    if central_alarm_df_path is None:
        return jsonify({"error": "central_alarm_dfが無い"}), 400
    central_alarm_df = pd.read_json(central_alarm_df_path, orient="records")
    
    # 中間点で2分割（奇数対応）
    mid = len(central_alarm_df) // 2 + (len(central_alarm_df) % 2)
    df_left = central_alarm_df.iloc[:mid].reset_index(drop=True)
    df_right = central_alarm_df.iloc[mid:].reset_index(drop=True)
    print(f"df_left:\n{df_left}")
    print(f"df_right:\n{df_right}")
    
    # メモリ上にPDFを生成
    buffer = BytesIO()

    left_table_contents=PdfTableBuilder(df_left,
                                        fontsize=10,
                                        font_name="IPAex Gothic",
                                        repeat_headers=True
                                        ).build_table_with_images(image_column="画像",
                                                                    image_folder="images")
    
    print(f"left_table_contents:\n{left_table_contents}")
    print(f"left_table_contents:{type(left_table_contents)}")
    
    right_table_contents=PdfTableBuilder(df_right,
                                        fontsize=10,
                                        font_name="IPAex Gothic",
                                        repeat_headers=True
                                        ).build_table_with_images(image_column="画像",
                                                                    image_folder="images")
    

    # left_table_contentsとright_table_contentsがwrap() 可能かテスト
    try:
        left_table_contents.wrap(0, 0)
        print("✅ left_table_contents is valid")
    except Exception as e:
        print("❌ left_table_contents error:", e)

    try:
        right_table_contents.wrap(0, 0)
        print("✅ right_table_contents is valid")
    except Exception as e:
        print("❌ right_table_contents error:", e)

    horizontal_table = TableHorizontal(left_table_contents, right_table_contents)
    pdf_table_list = [horizontal_table]
    width, height = horizontal_table.wrap(0, 0) 
    print(f"TableHorizontal width: {width}, height: {height}")
    
    print(f"pdf_table_list:{pdf_table_list}")
    print(type(pdf_table_list))
    
    export_pdf.build_PDFtables_to_pdf(pdf_table_list,
                                                buffer,
                                                main_title="セントラルモニタアラーム一覧",
                                                sub_title=None,
                                                header_text=None,
                                                footer_text="集中管理部",                                                                            
                                                landscape_mode=False,                                                                            
                                                )
    buffer.seek(0)  # 先頭に戻す

        # クライアントにダウンロードさせる
    return send_file(
        buffer,
        as_attachment=True,   # ← これで「保存ダイアログ」が出る
        download_name="central_alarm.pdf",  # ダウンロード時のファイル名
        mimetype="application/pdf"
    )

@app.route('/export_central_alarm_csv', methods=['POST', 'OPTIONS'])
def export_central_alarm_csv():
    try:
        # セッションから central_alarm_df を復元
        central_alarm_df_path = os.path.join(app.config['UPLOAD_FOLDER'], "central_alarm_df.json")
        if not os.path.exists(central_alarm_df_path):
            return jsonify({"error": "central_alarm_df.json が存在しません"}), 400
        central_alarm_df = pd.read_json(central_alarm_df_path, orient="records")
        print(f"central_alarm_df:\n{central_alarm_df.head(5)}")

        # CSV 出力
        buffer = BytesIO()
        central_alarm_df.to_csv(buffer, index=False, encoding='utf-8-sig')
        buffer.seek(0)  # 先頭に戻す

        return send_file(
            buffer,
            as_attachment=True,
            download_name="central_alarm.csv",
            mimetype="text/csv"
        )
    except Exception as e:
        return jsonify({"error": f"Error processing export_central_alarm_csv: {str(e)}"}), 500


# ---- ポート設定＆起動 ----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
