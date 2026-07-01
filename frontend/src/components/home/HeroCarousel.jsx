import { AnimatePresence, motion } from 'framer-motion'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useEffect, useState } from 'react'

export function HeroCarousel({ images, intervalMs = 5000 }) {
  const [index, setIndex] = useState(0)

  function goTo(nextIndex) {
    setIndex((nextIndex + images.length) % images.length)
  }

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((current) => (current + 1) % images.length)
    }, intervalMs)
    return () => clearInterval(timer)
  }, [images.length, intervalMs, index])

  return (
    <div className="absolute inset-0 overflow-hidden">
      <AnimatePresence mode="sync">
        <motion.img
          key={index}
          src={images[index]}
          alt="Featured property"
          initial={{ opacity: 0, scale: 1.06 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0 }}
          transition={{
            opacity: { duration: 1.4, ease: 'easeInOut' },
            scale: { duration: intervalMs / 1000 + 1.4, ease: 'linear' },
          }}
          className="absolute inset-0 h-full w-full object-cover"
        />
      </AnimatePresence>

      <button
        type="button"
        aria-label="Previous photo"
        onClick={() => goTo(index - 1)}
        className="absolute left-4 top-1/2 z-10 flex size-9 -translate-y-1/2 items-center justify-center rounded-full bg-white/20 text-white backdrop-blur transition-colors hover:bg-white/30"
      >
        <ChevronLeft className="size-5" />
      </button>
      <button
        type="button"
        aria-label="Next photo"
        onClick={() => goTo(index + 1)}
        className="absolute right-4 top-1/2 z-10 flex size-9 -translate-y-1/2 items-center justify-center rounded-full bg-white/20 text-white backdrop-blur transition-colors hover:bg-white/30"
      >
        <ChevronRight className="size-5" />
      </button>

      <div className="absolute bottom-20 left-1/2 z-10 flex -translate-x-1/2 gap-2">
        {images.map((image, dotIndex) => (
          <button
            key={image}
            type="button"
            aria-label={`Go to photo ${dotIndex + 1}`}
            onClick={() => goTo(dotIndex)}
            className={`h-1.5 rounded-full transition-all ${
              dotIndex === index ? 'w-6 bg-white' : 'w-1.5 bg-white/50'
            }`}
          />
        ))}
      </div>
    </div>
  )
}
