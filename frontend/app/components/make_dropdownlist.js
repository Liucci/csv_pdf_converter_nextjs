"use client";  
import { useRef } from "react";

export default function MakeDropdownList({ list = [], width = "200px", onChange }) {
  const selectRef = useRef(null);

  // ✅ 選択が変わったときに親へ返す
  const handleSelectChange = () => {
    const selectedValue = selectRef.current.value;
    if (onChange) {
      onChange(selectedValue);
    }
  };

  return (
    <div style={{ width }}>
      <select
        ref={selectRef}
        className="form-select"
        onChange={handleSelectChange}
        style={{ width: "100%" }}
      >
        <option value="">-- 選択してください --</option>
        {list.map((item, index) => (
          <option key={index} value={item}>
            {item}
          </option>
        ))}
      </select>
    </div>
  );
}
