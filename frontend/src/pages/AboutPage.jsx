import { Code2, GraduationCap, ShieldCheck } from 'lucide-react'

import { PageLayout } from '@/components/layout/PageLayout'

const POINTS = [
  {
    icon: GraduationCap,
    title: 'A portfolio project',
    description:
      'SoftStay was built as the final project of a full-stack Python development course. It is not a real business and does not process real bookings or payments.',
  },
  {
    icon: Code2,
    title: 'Full-stack, end to end',
    description:
      'Django REST Framework on the backend, React on the frontend, JWT authentication, role-based permissions, and a booking and review flow modeled on real rental platforms.',
  },
  {
    icon: ShieldCheck,
    title: 'Built with privacy in mind',
    description:
      'No third-party trackers, analytics, or CDNs. Fonts and images are self-hosted, and the app was designed with GDPR principles in mind from the start — see our Privacy Policy for details.',
  },
]

export function AboutPage() {
  return (
    <PageLayout>
      <div className="mx-auto max-w-3xl space-y-10">
        <div className="space-y-3">
          <h1 className="text-2xl font-semibold">About SoftStay</h1>
          <p className="text-foreground/80">
            SoftStay is a demonstration apartment rental platform, created as a portfolio project. It showcases a
            complete booking flow — listings, search and filtering, reservations, and reviews — built with a
            production-style architecture on both the backend and the frontend.
          </p>
          <p className="text-foreground/80">
            Any listings, bookings, or accounts created here are for demonstration purposes only. Nothing on this
            site is a real offer to rent property, and no real payments are ever processed.
          </p>
        </div>

        <div className="grid gap-6 sm:grid-cols-3">
          {POINTS.map(({ icon: Icon, title, description }) => (
            <div key={title} className="space-y-3 rounded-2xl border border-border bg-card p-5">
              <span className="flex size-10 items-center justify-center rounded-xl bg-accent/10 text-accent">
                <Icon className="size-5" />
              </span>
              <h2 className="font-semibold">{title}</h2>
              <p className="text-sm text-muted-foreground">{description}</p>
            </div>
          ))}
        </div>
      </div>
    </PageLayout>
  )
}
