"use client";
import { useRef, useEffect } from "react";

export default function ColumnContainer({
  list = [],
  width = "100%",
  height = "400px",
  scroll = true,
  onChange,
  containerId,
  containerName,
  selectedItems = [], // ★ 追加！現在選択されている値を受け取る
}) {
  const checkboxesRef = useRef({});

  function handleCheckbox() {
    const items = [];

    for (const key in checkboxesRef.current) {
      const checkbox = checkboxesRef.current[key];
      if (checkbox?.checked) {
        const index = parseInt(key.split("_").pop(), 10);
        items.push(list[index]);
      }
    }

    onChange && onChange(items);
  }

  // ★ selectedItems が変わったら UI に反映させる
  useEffect(() => {
    for (const key in checkboxesRef.current) {
      const checkbox = checkboxesRef.current[key];
      const index = parseInt(key.split("_").pop(), 10);
      const value = list[index];

      if (checkbox) {
        checkbox.checked = selectedItems.includes(value);
      }
    }
  }, [selectedItems, list]);

  return (
    <div className="mt-4" style={{ width }}>
      <h6 className="mb-3">{containerName}</h6>

      <div
        className="border rounded p-3"
        style={{
          maxHeight: height,
          overflowY: scroll ? "scroll" : "visible",
          backgroundColor: "#f8f9fa",
        }}
      >
        {list.map((col, index) => {
          const uniqueId = `col_${containerId}_${index}`;

          return (
            <div className="form-check" key={uniqueId}>
              <input
                className="form-check-input"
                type="checkbox"
                id={uniqueId}
                ref={(el) => (checkboxesRef.current[uniqueId] = el)}
                onChange={handleCheckbox}
              />
              <label className="form-check-label" htmlFor={uniqueId}>
                {col}
              </label>
            </div>
          );
        })}
      </div>
    </div>
  );
}
