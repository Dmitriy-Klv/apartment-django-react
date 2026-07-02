import { Link } from 'react-router-dom'

import { LegalLayout } from '@/components/layout/LegalLayout'

export function ImpressumPage() {
  return (
    <LegalLayout title="Legal Notice (Impressum)" updated="July 2026">
      <p>
        This page exists to document, transparently, the legal status of this project — the same way a live service
        would be required to under German law.
      </p>

      <section className="space-y-2">
        <h2>1. Operator</h2>
        <p>
          SoftStay is developed and operated by an individual as a non-commercial, educational portfolio project. It
          is not a registered business and has no employees, shareholders, or commercial operations.
        </p>
      </section>

      <section className="space-y-2">
        <h2>2. Legal notice status</h2>
        <p>
          Under § 5 DDG (formerly § 5 TMG), a full legal notice — including the operator&apos;s name, postal address,
          and direct contact details — is required for telemedia offered on a "geschäftsmäßig" (business-like) basis.
          The operator currently treats this project as a private, non-commercial educational portfolio. Whether a
          full legal notice is required under § 5 DDG depends on the specific circumstances of how the project is
          made publicly available, and this page does not attempt to make that determination itself.
        </p>
        <p>
          If the project is operated on a continuous public basis or otherwise falls within the scope of § 5 DDG,
          this page will be updated to include the legally required identification and contact details.
        </p>
      </section>

      <section className="space-y-2">
        <h2>3. Contact</h2>
        <p>
          For questions about this project, use the{' '}
          <Link to="/contact" className="underline underline-offset-4">
            Contact page
          </Link>
          .
        </p>
      </section>
    </LegalLayout>
  )
}
