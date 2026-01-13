import "./styles.css";
import type { Metadata } from "next";

import Header from "../components/Header";

export const metadata: Metadata = {
  title: "Writo",
  description: "Writo is a production-ready, SEO-first publishing platform.",
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"),
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Header />
        <main className="main">{children}</main>
      </body>
    </html>
  );
}
