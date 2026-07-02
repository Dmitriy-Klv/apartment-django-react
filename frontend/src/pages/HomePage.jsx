import { Features } from '@/components/home/Features'
import { Hero } from '@/components/home/Hero'
import { PopularListings } from '@/components/home/PopularListings'
import { Footer } from '@/components/layout/Footer'
import { Navbar } from '@/components/layout/Navbar'

export function HomePage() {
  return (
    <div className="mx-auto max-w-6xl px-4">
      <Navbar />
      <Hero />
      <Features />
      <PopularListings />
      <Footer />
    </div>
  )
}
