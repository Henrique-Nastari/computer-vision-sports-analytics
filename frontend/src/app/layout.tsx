import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SoccerCV Analytics - Premium Dashboard",
  description: "Advanced Sports Computer Vision Analytics",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
