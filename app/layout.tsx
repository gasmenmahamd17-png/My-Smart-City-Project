import "./globals.css"

export const metadata = {
  title: 'Smart City 3D',
  description: 'Interactive 3D virtual smart city visualization',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ar" dir="rtl">
      <body className="font-sans antialiased overflow-hidden">
        {children}
      </body>
    </html>
  )
}
