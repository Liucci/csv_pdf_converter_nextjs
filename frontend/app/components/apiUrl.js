// apiUrl.js
export async function detectApiUrl() {
  const currentOrigin = window.location.origin;

  const candidates = [
    currentOrigin.replace(":3000", ":5000"),        // ローカル用
    process.env.NEXT_PUBLIC_API_URL,               // デプロイ用 Render API
  ].filter(Boolean);

  for (const api of candidates) {
    try {
      const res = await fetch(`${api}/ping`, { method: "GET" });
      if (res.ok) {
        console.log("API URL detected:", api);
        return api;
      }
    } catch (e) {}
  }

  throw new Error("どの API_URL にも接続できません");
}

