import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RaceLive Ranking",
  description: "อันดับคะแนนสะสมนักกีฬาและทีม จากผลการแข่งขัน RaceLive",
  other: { "codex-preview": "development" },
  icons: { icon: "/favicon.svg", shortcut: "/favicon.svg" },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="th">
      <body>{children}</body>
    </html>
  );
}
