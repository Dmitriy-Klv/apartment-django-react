import { CheckCircle2, Code2, Mail, MessageCircle } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'

import { PageLayout } from '@/components/layout/PageLayout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'

const CHANNELS = [
  {
    icon: Mail,
    title: 'Email',
    description: 'hello@softstay.example',
  },
  {
    icon: Code2,
    title: 'Source code',
    description: 'This project is open for review as part of a course portfolio.',
  },
]

export function ContactPage() {
  const [submitted, setSubmitted] = useState(false)

  function handleSubmit(event) {
    event.preventDefault()
    event.target.reset()
    setSubmitted(true)
  }

  return (
    <PageLayout>
      <div className="mx-auto grid max-w-4xl gap-10 md:grid-cols-[1fr_1.2fr]">
        <div className="space-y-6">
          <div className="space-y-2">
            <h1 className="text-2xl font-semibold">Get in touch</h1>
            <p className="text-sm text-foreground/80">
              SoftStay is a demonstration project run by a single project owner, so this page is a working example
              of a contact form rather than a live support channel. Nothing you enter below is sent anywhere or
              stored.
            </p>
          </div>

          <div className="space-y-4">
            {CHANNELS.map(({ icon: Icon, title, description }) => (
              <div key={title} className="flex items-start gap-3">
                <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-accent/10 text-accent">
                  <Icon className="size-4" />
                </span>
                <div>
                  <p className="text-sm font-semibold">{title}</p>
                  <p className="text-sm text-muted-foreground">{description}</p>
                </div>
              </div>
            ))}
          </div>

          <p className="text-xs text-muted-foreground">
            Have questions about how this project was built? See the{' '}
            <Link to="/about" className="underline underline-offset-4">
              About page
            </Link>
            .
          </p>
        </div>

        <div className="rounded-3xl border border-border bg-card p-6">
          {submitted ? (
            <div className="flex h-full flex-col items-center justify-center gap-3 py-12 text-center">
              <span className="flex size-12 items-center justify-center rounded-full bg-accent/10 text-accent">
                <CheckCircle2 className="size-6" />
              </span>
              <p className="font-semibold">Message ready to send</p>
              <p className="max-w-xs text-sm text-muted-foreground">
                In a production app, this would now land in a support inbox. This demo doesn&apos;t transmit or store
                the message anywhere.
              </p>
              <Button variant="outline" size="sm" onClick={() => setSubmitted(false)}>
                Send another
              </Button>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                <MessageCircle className="size-4" />
                Send a message
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="contact-name">Name</Label>
                <Input id="contact-name" name="name" required />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="contact-email">Email</Label>
                <Input id="contact-email" name="email" type="email" required />
              </div>

              <div className="space-y-1.5">
                <Label htmlFor="contact-message">Message</Label>
                <Textarea id="contact-message" name="message" rows={5} required />
              </div>

              <Button type="submit" size="lg" className="w-full rounded-full">
                Send message
              </Button>
            </form>
          )}
        </div>
      </div>
    </PageLayout>
  )
}
