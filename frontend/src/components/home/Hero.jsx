import { motion } from 'framer-motion'

import { HeroCarousel } from '@/components/home/HeroCarousel'
import { SearchBar } from '@/components/home/SearchBar'
import { IMAGES } from '@/lib/images'

export function Hero() {
  return (
    <section className="relative">
      <div className="relative h-[560px] overflow-hidden rounded-4xl">
        <HeroCarousel images={IMAGES.heroSlides} intervalMs={5000} />
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/60 via-black/10 to-black/0" />

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: 'easeOut' }}
          className="pointer-events-none absolute inset-x-0 top-16 px-8 md:px-14"
        >
          <h1 className="max-w-xl text-4xl font-semibold leading-tight text-white md:text-6xl">
            Find your next home in Germany
          </h1>
          <p className="mt-4 max-w-md text-base text-white/80 md:text-lg">
            Verified listings, transparent pricing, and a booking flow built for renters and landlords alike.
          </p>
        </motion.div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.15, ease: 'easeOut' }}
        className="relative z-10 -mt-14 px-6 md:px-14"
      >
        <SearchBar />
      </motion.div>
    </section>
  )
}
