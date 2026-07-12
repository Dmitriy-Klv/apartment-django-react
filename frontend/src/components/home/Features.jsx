import { History, ShieldCheck, Sparkles } from 'lucide-react'

const FEATURES = [
  {
    icon: ShieldCheck,
    title: 'Verified listings',
    description: 'Every listing belongs to a registered landlord and goes through basic verification before it goes live.',
  },
  {
    icon: History,
    title: 'Search history that remembers',
    description: 'Every search and listing you view is saved automatically, so you can always pick up where you left off.',
  },
  {
    icon: Sparkles,
    title: 'Real reviews only',
    description: 'Only tenants with a completed stay can leave a review — no fake ratings, ever.',
  },
]

export function Features() {
  return (
    <section className="grid gap-8 py-24 md:grid-cols-3">
      {FEATURES.map(({ icon: Icon, title, description }) => (
        <div key={title} className="space-y-3">
          <span className="flex size-11 items-center justify-center rounded-2xl bg-accent/10 text-accent">
            <Icon className="size-5" />
          </span>
          <h3 className="text-lg font-semibold">{title}</h3>
          <p className="text-sm leading-relaxed text-muted-foreground">{description}</p>
        </div>
      ))}
    </section>
  )
}
