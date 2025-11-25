// apiUrl.js
export async function detectApiUrl() {
    const currentOrigin = window.location.origin; 
    // 例: 
    // ローカル → http://192.168.0.64:3000
    // Vercel → https://yourapp.vercel.app
    // Render → https://yourbackend.onrender.com

    const candidates = [
        currentOrigin.replace(":3000", ":5000"), // ローカル用
        currentOrigin.replace("https://", "https://api."),
        currentOrigin.replace("http://", "http://api."),
        process.env.NEXT_PUBLIC_API_URL, // デプロイ設定
    ].filter(Boolean);

    for (const api of candidates) {
        try {
            const res = await fetch(`${api}/ping`, {
                method: "GET",
                credentials: "include",
            });
            if (res.ok) {
                console.log("API URL detected:", api);
                return api;
            }
        } catch (e) {}
    }

    throw new Error("どの API_URL にも接続できません");
}

