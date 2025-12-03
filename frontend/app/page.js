"use client";

import 'bootstrap/dist/css/bootstrap.min.css'; // Bootstrap
import { useState,useRef,useEffect } from "react";
import ColumnContainer from "./components/container";
import MakeDropdownList from "./components/make_dropdownlist";
import { detectApiUrl } from "./components/apiUrl";
import CentralAlarmTable from "./components/CentralAlarmTable";

export default function Home() {
  const [filename, setFilename] = useState("");
  const [columns, setColumns] = useState([]);
  const [selected1, setSelected1] = useState([]);
  const [selected2, setSelected2] = useState([]);
  const [selected3, setSelected3] = useState([]);
  const tempSelected1Ref = useRef([]);
  const tempSelected2Ref = useRef([]);
  const tempSelected3Ref = useRef([]);
  const [tempSelected1, setTempSelected1] = useState([]);
  const [tempSelected2, setTempSelected2] = useState([]);
  const [tempSelected3, setTempSelected3] = useState([]);
  const [isDirty1, setIsDirty1] = useState(false);//チェックボックス変更検知フラグ
  const [isDirty2, setIsDirty2] = useState(false);//チェックボックス変更検知フラグ
  const [isDirty3, setIsDirty3] = useState(false);//チェックボックス変更検知フラグ
  const [error, setError] = useState("");
  const [showContainer1, setShowContainer1] = useState(false);
  const [showContainer2, setShowContainer2] = useState(false);
  const [showContainer3, setShowContainer3] = useState(false);
  const [showCSV, setShowCSV] = useState(false);

  const [showDropdown1, setShowDropdown1] = useState(false);
  const [showDropdown2, setShowDropdown2] = useState(false);
  const [dropdownValue1, setDropdownValue1] = useState("");
  const [dropdownValue2, setDropdownValue2] = useState("");

  const [unique_values1, setUniqueValues1] = useState([]);
  const [unique_values2, setUniqueValues2] = useState([]);

  const [showPdfButton, setShowPdfButton] = useState(false);

  const [centralData, setCentralData] = useState([]); // セントラルアラームデータ保存用

  const [apiUrl, setApiUrl] = useState("");

  //const apiUrl = "http://localhost:5000";
  useEffect(() => {
    async function initApiUrl() {
      try {
        const url = await detectApiUrl();
        setApiUrl(url);
        console.log("接続可能な apiUrl:", url);
      } catch (err) {
        console.error(err);
      }
    }

    initApiUrl();
  }, []);

  // CSVアップロード
  const handleUpload = async (e) => {
    e.preventDefault();
    setError("");
    setColumns([]);
    setShowContainer1(false);
    setShowDropdown1(false);
    
    const formData = new FormData(e.target);

    try {
      const res = await fetch(`${apiUrl}/upload`, {
        method: "POST",
        body: formData,
        credentials: "include",
      });

      const data = await res.json();

      if (res.ok) {
        setFilename(formData.get("file").name);
        console.log("アップロード成功:", data);
      } else {
        setError(data.error || "アップロードに失敗しました");
      }
    } catch (err) {
      setError("通信エラーが発生しました");
    }
  };

  // ヘッダー抽出
  const handleExtract = async () => {
    try {
      const res = await fetch(`${apiUrl}/manual_filter`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ }),
      });

      const data = await res.json();

      if (res.ok) {
        setColumns(data.columns);
        setShowContainer1(true);
        console.log("抽出成功:", data.columns);
      } else {
        setError(data.error || "ヘッダー取得に失敗しました");
      }
    } catch (err) {
      setError("通信エラーが発生しました");
    }
  };

/*   // チェックボックス選択
  const handleCheckboxChange1 = (list) => setSelected1(list);
  const handleCheckboxChange2 = (list) => setSelected2(list);
  const handleCheckboxChange3 = (list) => setSelected3(list);
 */  
//再レンダリングが起きないようにuseRefで一時保存
  const handleCheckboxTempChange1 = (list) => {
    tempSelected1Ref.current = list;
    setIsDirty1(true);  // ← 適用ボタンを光らせるトリガー
  };

  const handleCheckboxTempChange2 = (list) => {
    tempSelected2Ref.current = list;
    setIsDirty2(true);
  };

  const handleCheckboxTempChange3 = (list) => {
    tempSelected3Ref.current = list;
    setIsDirty3(true);
  };

  // 全選択・全解除ボタン
  const handleSelectAll1 = () => {
    tempSelected1Ref.current = [...columns];  // ref 更新
    setTempSelected1([...columns]);         // UI 更新
    setIsDirty1(true);
  };
  const handleClear1 = () => {
    tempSelected1Ref.current = [];
    setTempSelected1([]);
    setIsDirty1(true);
  };
  const handleSelectAll2 = () => {
    tempSelected2Ref.current = [...unique_values1];  // ref 更新
    setTempSelected2([...unique_values1]);         // UI 更新
    setIsDirty2(true);
  };
  const handleClear2 = () => {
    tempSelected2Ref.current = [];
    setTempSelected2([]);
    setIsDirty2(true);
  };
  const handleSelectAll3 = () => {
    tempSelected3Ref.current = [...unique_values2];  // ref 更新
    setTempSelected3([...unique_values2]);         // UI 更新
    setIsDirty3(true);
  };
  const handleClear3 = () => {
    tempSelected3Ref.current = [];
    setTempSelected3([]);
    setIsDirty3(true);
  };




    // 適用ボタン：選択列をバックエンドへ送信
  const handleApply1 = async () => {
    const finalList = tempSelected1Ref.current;
    setSelected1(finalList);
    console.log("/selected_cb1へ渡す:", finalList);
    setShowDropdown1(true);
    setIsDirty1(false); // ボタンを元の色に戻す

    try {
      const res = await fetch(`${apiUrl}/selected_cb1`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ selected_cb1: finalList }),
      });

      const data = await res.json();
      if (!res.ok) console.error("サーバーエラー:", data.error);
      else console.log("バックエンド応答:", data);
    } catch (err) {
      console.error("送信エラー:", err);
    }
  };

  const handleApply2 = async () => {
    const finalList = tempSelected2Ref.current;
    setSelected2(finalList);
    console.log("/selected_cb2へ渡す:", finalList);
    setShowDropdown2(true);
    setIsDirty2(false); // ボタンを元の色に戻す

    try {
      const res = await fetch(`${apiUrl}/selected_cb2`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ selected_cb2: finalList }),
      });

      const data = await res.json();
      if (!res.ok) console.error("サーバーエラー:", data.error);
      else console.log("バックエンド応答:", data);
    } catch (err) {
      console.error("送信エラー:", err);
    }
  };
  
  const handleApply3 = async () => {
    const finalList = tempSelected3Ref.current;
    setSelected3(finalList);
    setIsDirty3(false); // ボタンを元の色に戻す
    setShowPdfButton(true);    // ← PDFボタンを表示
    console.log("/selected_cb3へ渡す:", finalList);
    
    try {
      const res = await fetch(`${apiUrl}/selected_cb3`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ selected_cb3: finalList }),
      });

      const data = await res.json();
      if (!res.ok) console.error("サーバーエラー:", data.error);
      else console.log("バックエンド応答:", data);
    } catch (err) {
      console.error("送信エラー:", err);
    }
  };


  //dropwdownで選択した値を/dropdown_value1に送信してunique_value1を取得しcontainerに表示する
  const handleDropdownChange1 = async (dropdownvalue1) => {
    setDropdownValue1(dropdownvalue1); // ← まずローカルstateも更新
    console.log("dropdown1で選択された値:", dropdownvalue1);

    try {
      const res = await fetch(`${apiUrl}/dropdown_value1`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ dropdown_value1: dropdownvalue1 }), // ← valueを送る
      });
      const data = await res.json();
      if (!res.ok) console.error("サーバーエラー:", data.error);
      else console.log("バックエンド応答:", data);
      //unique_values1 を受け取って state に保存
      console.log("受け取った unique_values1:", data.unique_values1);
      setUniqueValues1(data.unique_values1 || []);
    } 
    catch (err) {
      console.error("送信エラー:", err);
    }
  };

  //dropwdownで選択した値を/dropdown_value1に送信してunique_value1を取得しcontainerに表示する
  const handleDropdownChange2 = async (value) => {
    console.log("dropdown2で選択された値:", value);
    setDropdownValue2(value); // ← まずローカルstateも更新

    try {
      const res = await fetch(`${apiUrl}/dropdown_value2`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ dropdown_value2: value }), // ← valueを送る
      });
      const data = await res.json();
      if (!res.ok) console.error("サーバーエラー:", data.error);
      else console.log("バックエンド応答:", data);
      //unique_values2 を受け取って state に保存
      console.log("受け取った unique_values2:", data.unique_values2);
      setUniqueValues2(data.unique_values2 || []);
    } 
    catch (err) {
      console.error("送信エラー:", err);
    }
  };

  const handleCreatePDF = async () => {
  try {
    const res = await fetch(`${apiUrl}/filtered_df3_pdf`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({})
    });
    setShowPdfButton(false);
    if (!res.ok) {
      console.error("PDF作成失敗:", await res.text());
      return;
    }
    // PDFファイルを取得できるようにblobとして受け取る
    const blob = await res.blob();               // ← PDF を受け取る
    const url = window.URL.createObjectURL(blob);

/*     // ブラウザでダウンロード
    const a = document.createElement("a");
    a.href = url;
    a.download = "filtered_df3.pdf";             
    a.click();
    window.URL.revokeObjectURL(url);
 */  
        // ★ PDF プレビュー用に新しいタブで開く
    window.open(url, "_blank");
  } catch (err) {
    console.error("送信エラー:", err);
  }
  };

  const handleCentralAlarm = async () => {
    try {
      const res = await fetch(`${apiUrl}/central_alarm`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ }),
      });

       const data = await res.json();

    if (data.central_df) {
      setCentralData(data.central_df);  // ← central_df を保持
    }
    }

    catch (err) {
      console.error("送信エラー:", err);
    }
  };
// セントラルアラーム PDF 作成
  const handleCreateCentralAlarmPDF = async () => {
  try {
    // 現在表示されているテーブルの情報を収集
    const rows = document.querySelectorAll("tbody tr");

    let deleteRows = [];
    let volumeList = [];

    rows.forEach((tr, index) => {
      const checkbox = tr.querySelector("input[type='checkbox']");
      const volumeInput = tr.querySelector("input[name^='volume_']");

      if (checkbox && checkbox.checked) {
        deleteRows.push(index);
        
      }

      if (volumeInput) {
        volumeList.push(volumeInput.value);
        
      }
    });
    console.log("削除行:", deleteRows);
    console.log("音量リスト:", volumeList);

    const res = await fetch(`${apiUrl}/make_central_alarm_df`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        volume: volumeList,
        delete_rows: deleteRows,
      }),
    });

    if (!res.ok) {
      console.error("PDF生成エラー");
      return;
    }

      const blob = await res.blob();
    const pdfUrl = window.URL.createObjectURL(blob);

    // ←↓↓ これが PDF プレビューを開くコード
    window.open(pdfUrl, "_blank");
  } 
  catch (err) {
    console.error(err);
  }
  setShowCSV(true);  // ← ここで CSV ボタンを表示
};
  
// セントラルアラーム CSV 作成
const handleCreateCentralAlarmCSV = async () => {
  try {
    const res = await fetch(`${apiUrl}/export_central_alarm_csv`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({}),
    });

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    // CSV を Blob として受け取る
    const blob = await res.blob();

    // ダウンロードリンクを作成してクリック
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "central_alarm.csv";
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error("送信エラー:", err);
  }
};
  return (
    <div className="container py-5">
      <div className="card shadow-sm">
        <div className="card-body">
          <h5 className="card-title mb-3">CSVヘッダー抽出</h5>

          {/* ファイルアップロード */}
          <form onSubmit={handleUpload} encType="multipart/form-data">
            <div className="mb-3">
              <input
                className="form-control"
                style={{ width: "500px" }}
                type="file"
                name="file"
                accept=".csv"
                required
              />
            </div>
            <button type="submit" className="btn btn-primary">
              アップロード
            </button>
          </form>

          {error && <p className="text-danger mt-3">{error}</p>}
          {filename && <p className="mt-3">アップロード済み: {filename}</p>}

          {/* 抽出ボタン */}
          {filename && (
            <div className="mt-3 d-flex gap-2">
              <button className="btn btn-success" onClick={handleExtract}>
                抽出
              </button>

              <button className="btn btn-primary" onClick={handleCentralAlarm}>
                セントラルアラーム一覧
              </button>
            </div>

          )}
          <CentralAlarmTable data={centralData} />
          {/* centralData があるときだけ PDF / CSV ボタンを表示 */}
          {centralData.length > 0 && (
            <div className="mt-3 d-flex gap-2">
              <button
                className="btn btn-outline-primary"
                onClick={handleCreateCentralAlarmPDF}
              >
                PDF作成
              </button>
              {/* CSVボタンはPDF作成後に表示 */}
              {showCSV && (
              <button
                className="btn btn-outline-primary"
                onClick={handleCreateCentralAlarmCSV}
              >
                CSV作成
              </button>
              )}
            </div>
          )}


          {showContainer1 && (
            <div
              style={{
                display: "flex",
                gap: "20px",
                alignItems: "flex-start",
                marginTop: "30px",
              }}
            >
              {/* ▼ 左ブロック */}
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "10px",
                  width: "30%",
                  marginTop: "28px",
                }}
              >
                <ColumnContainer
                  list={columns}
                  onChange={handleCheckboxTempChange1}
                  width="100%"
                  height="300px"
                  scroll="auto"
                  containerId="c1" 
                  containerName="抽出列選択"
                  selectedItems={tempSelected1Ref.current}
                />

                <div className="mt-3" style={{ display: "flex", gap: "10px" }}>
                  <button
                    className={`btn ${isDirty1 ? "btn-warning" : "btn-primary"}`}
                    onClick={handleApply1}
                  >
                    適用
                  </button>

                  <button className="btn btn-secondary" onClick={handleSelectAll1}>
                    全選択
                  </button>

                  <button className="btn btn-secondary" onClick={handleClear1}>
                    解除
                  </button>
                </div>
              </div>

              {/* ▼ コンテナ２ブロック */}
              {showDropdown1 && (
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "10px",
                    width: "30%",
                    marginTop: "-20px",
                  }}
                >
                  {selected1.length > 0 && (
                    <MakeDropdownList
                      list={selected1}
                      width="200px"
                      onChange={handleDropdownChange1}
                    />
                  )}

{/*                   {dropdownValue1 && (
                    <p style={{ marginTop: "10px" }}>選択中: {dropdownValue1}</p>
                  )}
 */}
                  <ColumnContainer
                    list={unique_values1}
                    onChange={handleCheckboxTempChange2}
                    width="100%"
                    height="300px"
                    scroll="auto"
                    containerId="c2" 
                    containerName="抽出行第1条件選択"
                    selectedItems={tempSelected2Ref.current}
                  />

                  <div className="mt-3" style={{ display: "flex", gap: "10px" }}>
                    <button
                      className={`btn ${isDirty2 ? "btn-warning" : "btn-primary"}`}
                      onClick={handleApply2}
                    >
                      適用
                    </button>

                    <button className="btn btn-secondary" onClick={handleSelectAll2}>
                      全選択
                    </button>

                    <button className="btn btn-secondary" onClick={handleClear2}>
                      解除
                    </button>
                  </div>
                </div>
              )}
                {/* ▼ コンテナ３ブロック */}
              {showDropdown2 && (
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "10px",
                    width: "30%",
                    marginTop: "-20px",
                  }}
                >
                  {selected1.length > 0 && (
                    <MakeDropdownList
                      list={selected1}
                      width="200px"
                      onChange={handleDropdownChange2}
                    />
                  )}

{/*                   {dropdownValue2 && (
                    <p style={{ marginTop: "10px" }}>選択中: {dropdownValue2}</p>
                  )}
 */}
                  <ColumnContainer
                    list={unique_values2}
                    onChange={handleCheckboxTempChange3}
                    width="100%"
                    height="300px"
                    scroll="auto"
                    containerId="c3" 
                    containerName="抽出行第2条件選択"
                    selectedItems={tempSelected3Ref.current}
                  />

                  <div className="mt-3" style={{ display: "flex", gap: "10px" }}>
                    <button
                      className={`btn ${isDirty3 ? "btn-warning" : "btn-primary"}`}
                      onClick={handleApply3}
                    >
                      適用
                    </button>

                    <button className="btn btn-secondary" onClick={handleSelectAll3}>
                      全選択
                    </button>

                    <button className="btn btn-secondary" onClick={handleClear3}>
                      解除
                    </button>
                  </div>
                  {showPdfButton && (
                    <div className="mt-3">
                      <button className="btn btn-primary" onClick={handleCreatePDF}>
                        PDF作成
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
              
          
        </div>
      </div>
    </div>
  );
}
