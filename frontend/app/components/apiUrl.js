// apiUrl.js
export async function detectApiUrl() {
  const currentOrigin = window.location.origin;

  // 候補リストを明示的に整理
  const candidates = [
    // ローカル開発用: Next.js が :3000 で動いているときに Flask を :5000 で探す
    currentOrigin.includes("localhost:3000")
      ? currentOrigin.replace(":3000", ":5000")
      : null,

    // 本番用: Render の環境変数で指定した backend サービス URL
    //renderのEnvironment VariablesでNEXT_PUBLIC_API_URLのvalueを　https://csv-pdf-converter-nextjs.onrender.com
    process.env.NEXT_PUBLIC_API_URL,
  ].filter(Boolean);

  for (const api of candidates) {
    try {
      const res = await fetch(`${api}/ping`, { method: "GET" });
      if (res.ok) {
        console.log("API URL detected:", api);
        return api;
      }
    } catch (e) {
      console.warn(`API check failed for ${api}:`, e);
    }
  }

  throw new Error("どの API_URL にも接続できません。NEXT_PUBLIC_API_URL を確認してください。");
}
