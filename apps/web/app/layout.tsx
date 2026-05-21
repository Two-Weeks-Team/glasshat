import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "Glasshat",
  description: "Rubric-aware evaluation that audits its own scores.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
