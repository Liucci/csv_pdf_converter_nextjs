// app/layout.js
import "bootstrap/dist/css/bootstrap.min.css";

export const metadata = {
  title: "CSV Header App",
  description: "CSV列選択アプリ",
};

export default function RootLayout({ children }) {
  return (
    <html lang="ja">
      <head />
      <body>{children}</body>
    </html>
  );
}
