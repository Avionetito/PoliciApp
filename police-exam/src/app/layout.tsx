import { Providers } from './providers';

export const metadata = { title: 'Tests Policía Nacional' };

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-gray-50 text-gray-900">
        {/* Providers is a *client* island that survives route changes */}
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
