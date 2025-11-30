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
from io import StringIO,BytesIO
from flask_cors import CORS
import shutil

# --- 起動時クリーニング ---
def cleanup_startup():
    folders = ["flask_session", "uploads"]

    for folder in folders:
        # フォルダが無ければ作成
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            continue

        # --- 中身を削除（フォルダは残す） ---
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # ファイル削除
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # サブフォルダ削除
                print(f"[CLEAN] removed: {file_path}")
            except Exception as e:
                print(f"[CLEAN] failed to delete {file_path}: {e}")


app =Flask(__name__)

CORS(app, supports_credentials=True)

# ---- Flask-Sessionの設定 ----
app.config["SESSION_TYPE"] = "filesystem"  # サーバー側に保存
app.config["SESSION_PERMANENT"] = False
# backend フォルダを基準に相対パスを指定
session_dir = os.path.join(os.path.dirname(__file__), "flask_session")
app.config["SESSION_FILE_DIR"] = session_dir
app.config["SESSION_USE_SIGNER"] = True  # セキュリティ強化
app.config['DEBUG'] = True

# ---- Sessionを初期化 ----
Session(app)
#uploadsフォルダの設定
# backend フォルダを基準に uploads フォルダのパスを指定
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-for-local")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.after_request
# ---- 動的 CORS ----
def add_cors_headers(response):
    origin = request.headers.get("Origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response

@app.route("/ping", methods=["GET", "OPTIONS"])
def ping():
    return jsonify({"status": "ok"}), 200


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    save_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(save_path)

    # pandasで読み込み
    try:
        df = csv_reader.load_csv(save_path)
        # セッションに保存
        session["df"] = df.to_json(orient="split")
        return jsonify({"message": "ファイルをアップロードしました"}), 200

    except Exception as e:
        return jsonify({"error": f"CSV読み込み失敗: {str(e)}"}), 500

@app.route("/manual_filter", methods=["POST"])
def manual_filter():
        # セッションから DataFrame を取得
    df_json = session.get("df")
    if df_json is None:
        return jsonify({"error": "No DataFrame found in session"}), 400
        
    else:
        df = pd.read_json(StringIO(df_json), orient="split")
        print(df.head(5))


        #コンテナ１に表示させる列名リスト
    columns_name_list_1 = df.columns.tolist()
    for a in columns_name_list_1:
        print(f"・{a}")
    return jsonify({"columns": columns_name_list_1}), 200

@app.route("/selected_cb1", methods=["POST"])
def selected_cb1():
    selected_cb1 = request.json.get("selected_cb1", [])
    print("選択された列名リスト:")
    for col in selected_cb1:
        print(f"・{col}")

    # セッションから DataFrame を取得
    df_json = session.get("df")
    df = pd.read_json(StringIO(df_json), orient="split")

    # 選択された列でフィルタリング
    filtered_df1 = df[selected_cb1]
    print(f"filtered_df1{filtered_df1.head(10)}")

    # フィルタリングした DataFrame をセッションに保存
    session["filtered_df1"] = filtered_df1.to_json(orient="split")

    return jsonify({"message": "選択された列でフィルタリングしました"}), 200

@app.route("/dropdown_value1", methods=["POST"])
def dropdown_value1():
    dropdown_value1= request.json.get("dropdown_value1", "")
    session["dropdown_value1"] = dropdown_value1
    print(f"選択されたドロップダウン1の値: {dropdown_value1}")

    # セッションからフィルタリングされた DataFrame を取得
    filtered_df1_json = session.get("filtered_df1")
    filtered_df1 = pd.read_json(StringIO(filtered_df1_json), orient="split")

    # dropdown_value1列のユニークな値を取得
    unique_values1 = filtered_df1[dropdown_value1].unique().tolist()
    print("dropdown_value1列の固有値リスト:")
    for val in unique_values1:
        print(f"・{val}")
    session["unique_values1"] = unique_values1
    return jsonify({"unique_values1": unique_values1}), 200
    
@app.route("/selected_cb2", methods=["POST"])
def selected_cb2():
    selected_cb2 = request.json.get("selected_cb2", [])
    print("選択された行名リスト2:")
    for row in selected_cb2:
        print(f"・{row}")

    # セッションから DataFrame を取得
    df_json = session.get("filtered_df1")
    filtered_df1 = pd.read_json(StringIO(df_json), orient="split")
    dropdown_value1 = session.get("dropdown_value1")

    # 選択された行名でフィルタリング
    filtered_df2 = filtered_df1[filtered_df1[dropdown_value1].isin(selected_cb2)]
    print(f"filtered_df2{filtered_df2.head(10)}")
    # フィルタリングした DataFrame をセッションに保存
    session["filtered_df2"] = filtered_df2.to_json(orient="split")

    return jsonify({"message": "選択された行名でフィルタリングしました"}), 200

@app.route("/dropdown_value2", methods=["POST"])
def dropdown_value2():
    dropdown_value2= request.json.get("dropdown_value2", "")
    session["dropdown_value2"] = dropdown_value2
    print(f"選択されたドロップダウン2の値: {dropdown_value2}")

    # セッションからフィルタリングされた DataFrame を取得
    filtered_df2_json = session.get("filtered_df2")
    filtered_df2 = pd.read_json(StringIO(filtered_df2_json), orient="split")
    #print("session.get('filtered_df2'):", session.get("filtered_df2"))

    # dropdown_value2列のユニークな値を取得
    unique_values2 = filtered_df2[dropdown_value2].unique().tolist()
    print("dropdown_value2列の固有値リスト:")
    for val in unique_values2:
        print(f"・{val}")
    session["unique_values2"] = unique_values2
    return jsonify({"unique_values2": unique_values2}), 200

@app.route("/selected_cb3", methods=["POST"])
def selected_cb3():
    selected_cb3 = request.json.get("selected_cb3", [])
    print("選択された行名リスト3:")
    for row in selected_cb3:
        print(f"・{row}")

    # セッションから DataFrame を取得
    df_json = session.get("filtered_df2")
    filtered_df2 = pd.read_json(StringIO(df_json), orient="split")
    dropdown_value2 = session.get("dropdown_value2")

    # 選択された行名でフィルタリング
    filtered_df3 = filtered_df2[filtered_df2[dropdown_value2].isin(selected_cb3)]
    print(f"filtered_df3{filtered_df3.head(10)}")
    # フィルタリングした DataFrame をセッションに保存
    session["filtered_df3"] = filtered_df3.to_json(orient="split")

    return jsonify({"message": "選択された行名でフィルタリングしました"}), 200


@app.route("/filtered_df3_pdf", methods=["POST", "OPTIONS"])
def filtered_df3_pdf():
    # OPTIONS に応答（プリフライト用）
    if request.method == "OPTIONS":
        return "", 200

    # セッションからフィルタリングされた DataFrame を取得
    filtered_df3_json = session.get("filtered_df3")
    if not filtered_df3_json:
        print("filtered_df3 is None or empty")
        return "ファイルが存在しません", 400

    filtered_df3 = pd.read_json(StringIO(filtered_df3_json), orient="split")
    print(f"最終的なfiltered_df3:\n{filtered_df3.head(10)}")

    try:
        # 一時ファイルとしてPDFを作成し、そのパスを取得
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            pdf_path = tmp.name

        export_pdf.export_dataframe_to_pdf(
            filtered_df3,
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
        print(f"PDFが正常に保存されました（tempfile）: {pdf_path}")

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
            download_name="filtered_df3.pdf",
            mimetype="application/pdf"
        )

    except Exception as e:
        print(f"PDF生成中にエラー: {e}")
        return "PDFの生成中にエラーが発生しました", 500

@app.route('/central_alarm', methods=['POST'])
def central_alarm():
        # セッションからフィルタリングされた DataFrame を取得
    df_json = session.get("df")
    if not df_json:
        print("df is None or empty")
        return "ファイルが存在しません", 400

    df = pd.read_json(StringIO(df_json), orient="split")
    df_exclude= df[~df["ME.No"].str.contains("貸出",na=False)
                    &~df["現所在地"].str.contains("臨床工学室|手術室|新　ＭＥ室",na=False)
                    ]#特定のデータを除外する

    column_name1="現所在地"
    column_name2="機器名称"
    column_name3="型式"
    column_unique_list1=["新　西2階","新　西4階","新　西5階","新　西6階","新　西7階","新　東3階","HCU","新　東4階(小児科)","新　NICU",
                            "HCU","新　東4階(産婦人科)","新　東5階","新　東6階","新　東7階","新　SCU","新　CCU","新　臨床工学室",
                            "新　ＭＥ室","新　ICU","新　CT室","新　内視鏡室","新　化学療法室","新　運動療法室","新　中央処置室","新　外来A",
                            "血液浄化センター","新　手術室","新　救急外来","新　内視鏡室"]
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

    central_df["現所在地"] = central_df["現所在地"].str.replace(r"新　東4階(小児科)", "東4小児", regex=False)
    central_df["現所在地"] = central_df["現所在地"].str.replace(r"新　東4階(産婦人科)", "東4産", regex=False)
    central_df["現所在地"] = central_df["現所在地"].str.replace("血液浄化センター", "血液浄化センター", regex=True)
    central_df["現所在地"] = central_df["現所在地"].str.replace("新　化学療法室", "化学療法室", regex=True)
    central_df["現所在地"] = central_df["現所在地"].str.replace("新　運動療法室", "運動療法室", regex=True) 
    central_df["現所在地"] = central_df["現所在地"].str.replace("新　|階", "", regex=True)  
    central_df = central_df.reset_index(drop=True)   
    # セッションに保存
    session["central_df"] = central_df.to_json(orient="split")
    # HTMLに渡す（pandas DataFrame → HTMLテーブルに変換）
    print(f"central_df{central_df.head(10)}")

    return jsonify({
        "message": "central_df created",
        "central_df": central_df.to_dict(orient="records")
    }), 200

@app.route('/make_central_alarm_df', methods=['POST' , 'OPTIONS'])
def make_central_alarm_df():
        # OPTIONS に応答（プリフライト用）
    if request.method == "OPTIONS":
        return "", 200
    # セッションから central_df を復元

    central_df_json = session.get("central_df")
    central_df = pd.read_json(StringIO(central_df_json), orient="split")


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
    session["central_alarm_df"] = central_alarm_df.to_json(orient="split")
    print(f"central_alarm_df:\n{central_alarm_df}")

    return export_central_alarm_pdf()


@app.route('/export_central_alarm_pdf', methods=['GET'])
def export_central_alarm_pdf():
    # セッションから central_alarm_df を復元
    central_alarm_df = pd.read_json(session.get("central_alarm_df"), orient="split")
    print(f"export_central_alarm_pdf: central_alarm_df=\n{central_alarm_df}")

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

@app.route('/export_central_alarm_csv', methods=['POST'])
def export_central_alarm_csv():
    # セッションから central_alarm_df を復元
    

    json_str = session.get("central_alarm_df")
    central_alarm_df = pd.read_json(StringIO(json_str), orient="split")

    """
    # フォームから送信された音量データを central_alarm_df に反映
    for i, row in central_alarm_df.iterrows():
        input_name = f"volume_{i}"
        if input_name in request.form:
            central_alarm_df.at[i, "音量"] = request.form[input_name]
    """

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


# ---- ポート設定＆起動 ----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
