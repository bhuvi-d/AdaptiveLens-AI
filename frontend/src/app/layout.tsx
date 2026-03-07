import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AdaptiveLens AI — Adaptive Learning System",
  description:
    "RAG-based adaptive learning system that simplifies academic content with personalized complexity levels. Upload PDFs and get explanations tailored to your knowledge level.",
  keywords: [
    "adaptive learning",
    "RAG",
    "AI tutor",
    "academic",
    "PDF",
    "study",
    "education",
  ],
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
