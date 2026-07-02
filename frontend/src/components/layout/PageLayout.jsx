import { Footer } from '@/components/layout/Footer'
import { Navbar } from '@/components/layout/Navbar'

export function PageLayout({ children }) {
  return (
    <div className="mx-auto max-w-6xl px-4">
      <Navbar />
      <main className="py-10">{children}</main>
      <Footer />
    </div>
  )
}
