import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Customize Resume Generation | AI-Powered Explainable Customizer',
  description:
    'Evidence-grounded and explainable resume customization platform analyzing candidate profiles against job requirements with user-controlled suggestions.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased selection:bg-brand-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
