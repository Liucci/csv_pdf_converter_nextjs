import React from "react";

export default function CentralAlarmTable({ data }) {
  if (!data || data.length === 0) return null;

  return (
    <div className="card mt-3 p-3">
      <h5>セントラルアラーム一覧</h5>

      <div className="table-container" style={{ maxHeight: "500px", overflow: "auto" }}>
        <table className="table table-striped table-bordered">
          <thead>
            <tr>
              <th>削除</th>
              {Object.keys(data[0]).map((col) => (
                <th key={col}>{col}</th>
              ))}
              <th>音量</th>
            </tr>
          </thead>

          <tbody>
            {data.map((row, idx) => (
              <tr key={idx}>
                <td>
                  <input type="checkbox" name={`delete_${idx}`} />                
                </td>

                {Object.keys(row).map((col) => (
                  <td key={col}>{row[col]}</td>
                ))}

                <td>
                  <input
                    type="text"
                    name={`volume_${idx}`}
                    style={{ width: "80px" }}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
