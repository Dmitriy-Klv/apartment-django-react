import { PageLayout } from '@/components/layout/PageLayout'

export function LegalLayout({ title, updated, children }) {
  return (
    <PageLayout>
      <div className="mx-auto max-w-3xl space-y-8">
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold">{title}</h1>
          {updated && <p className="text-sm text-muted-foreground">Last updated: {updated}</p>}
        </div>

        <div className="space-y-6 text-sm leading-relaxed text-foreground/90 [&_h2]:pt-2 [&_h2]:text-base [&_h2]:font-semibold [&_h2]:text-foreground [&_p]:text-foreground/80 [&_ul]:list-disc [&_ul]:space-y-1 [&_ul]:pl-5 [&_ul]:text-foreground/80">
          {children}
        </div>
      </div>
    </PageLayout>
  )
}
