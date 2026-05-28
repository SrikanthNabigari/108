import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "108 — Life's Operating System",
  description: "Your Vedic chart, decoded. A complete life reading grounded in classical Jyotish.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
