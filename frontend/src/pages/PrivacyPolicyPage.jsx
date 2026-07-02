import { Link } from 'react-router-dom'

import { LegalLayout } from '@/components/layout/LegalLayout'

export function PrivacyPolicyPage() {
  return (
    <LegalLayout title="Privacy Policy" updated="July 2026">
      <p>
        SoftStay is a demonstration project built for an educational portfolio. It is not a commercial service. This
        policy describes, honestly and specifically, what data the application actually collects and how it is used
        — the same standard we would apply to a live product.
      </p>

      <section className="space-y-2">
        <h2>1. Who is responsible for your data</h2>
        <p>
          This application is operated by an individual as a non-commercial, educational portfolio project. See our{' '}
          <Link to="/impressum" className="underline underline-offset-4">
            Legal Notice
          </Link>{' '}
          for details on its legal status. If you have questions about your data, use the{' '}
          <Link to="/contact" className="underline underline-offset-4">
            Contact page
          </Link>
          .
        </p>
      </section>

      <section className="space-y-2">
        <h2>2. What data we collect</h2>
        <ul>
          <li>
            <strong>Account data:</strong> email address, a username of your choice, and role (tenant or landlord),
            provided when you register. Your password is hashed before storage and is never stored or transmitted in
            plain text.
          </li>
          <li>
            <strong>Listing data:</strong> if you register as a landlord and publish a listing, its title,
            description, location, price, and property details are stored and shown publicly to all visitors — this
            is the intended purpose of a listing.
          </li>
          <li>
            <strong>Booking data:</strong> if you book a listing, the stay dates and booking status are stored and
            shared only with the landlord responsible for that specific listing — not with any other user.
          </li>
          <li>
            <strong>Reviews:</strong> ratings and comments you submit after a completed stay are stored and shown
            publicly on the listing page, without your email address or other private account information attached.
          </li>
          <li>
            <strong>Usage data:</strong> search keywords and listing views are recorded to power the "trending"
            sections of the site. This is not linked to advertising or shared with anyone outside this application.
          </li>
        </ul>
      </section>

      <section className="space-y-2">
        <h2>3. No real personal data required</h2>
        <p>
          Registration only asks for an email address, a password, and a username — there is no separate "real name"
          field anywhere on this site. Nobody is required or expected to enter their real name, and no part of the
          registration flow forces, hides, or auto-generates data on your behalf: you choose your own username, and a
          nickname or pseudonym is entirely appropriate here, since this is a demonstration project built for a
          software development portfolio rather than a live commercial service.
        </p>
      </section>

      <section className="space-y-2">
        <h2>4. Content you choose to make public</h2>
        <p>
          Listing descriptions and reviews are visible to every visitor of this site. Please do not include personal,
          confidential, or sensitive information — your own or anyone else&apos;s — in reviews, listing descriptions,
          or any other publicly visible content. Anything you submit there may be seen by all visitors, not just
          registered users.
        </p>
      </section>

      <section className="space-y-2">
        <h2>5. Where your data is stored</h2>
        <p>
          For simplicity within this portfolio project, your session token and a small profile summary (id, email,
          username, role) are stored in the browser&apos;s local storage after you log in, so you stay signed in. This
          data stays on your device and is only ever sent back to this application&apos;s own server — never to a
          third party.
        </p>
      </section>

      <section className="space-y-2">
        <h2>6. Cookies and local storage consent</h2>
        <p>
          SoftStay does not use cookies for analytics, advertising, or tracking, and does not show a cookie consent
          banner. Authentication relies on browser local storage instead of cookies. Storing a session token to keep
          you signed in is "strictly necessary" for the service you requested (staying logged in), which is exempt
          from consent requirements under the ePrivacy Directive and the German TDDDG. No non-essential storage is
          used.
        </p>
      </section>

      <section className="space-y-2">
        <h2>7. No third-party sharing</h2>
        <p>
          SoftStay does not intentionally share personal data with third-party advertising or analytics providers.
          The application does not use third-party fonts, CDNs, or tracking scripts — all fonts and images are
          hosted locally. Infrastructure providers required to host and operate the application (for example, a
          hosting or server provider) may process technical data, such as IP addresses in server access logs, as
          necessary to deliver the service.
        </p>
      </section>

      <section className="space-y-2">
        <h2>8. Legal basis for processing</h2>
        <p>
          This project is designed with a German/EU rental market in mind, which is why GDPR is used as the
          reference framework for this policy, regardless of where the application is actually hosted or tested.
          Account and booking data are processed to perform the contract you enter into by registering and using the
          booking feature (Art. 6(1)(b) GDPR). Usage data used for the trending sections is processed on the basis of
          a legitimate interest in operating the service (Art. 6(1)(f) GDPR).
        </p>
      </section>

      <section className="space-y-2">
        <h2>9. How long we keep your data</h2>
        <p>
          Account, listing, booking, and review data is kept for as long as your account exists. Self-service
          account deletion is not available yet in this demo; to request removal of your data, contact us via the{' '}
          <Link to="/contact" className="underline underline-offset-4">
            Contact page
          </Link>
          . As this is a demo environment, its database may also be periodically reset for maintenance or testing,
          which removes accounts and their associated content without individual notice.
        </p>
      </section>

      <section className="space-y-2">
        <h2>10. Your rights</h2>
        <p>Depending on your jurisdiction, you may have the right to:</p>
        <ul>
          <li>Access the personal data we hold about you</li>
          <li>Request correction of inaccurate data</li>
          <li>Request erasure of your data</li>
          <li>Restrict or object to certain processing</li>
          <li>Receive your data in a portable format</li>
          <li>Lodge a complaint with a data protection supervisory authority</li>
        </ul>
      </section>

      <section className="space-y-2">
        <h2>11. Age requirement</h2>
        <p>
          This application is intended for users who are at least 16 years old, or the minimum age required for
          consent to data processing under applicable local law, whichever is higher.
        </p>
      </section>

      <section className="space-y-2">
        <h2>12. Changes to this policy</h2>
        <p>
          As this is an evolving portfolio project, this page may be updated as features change. The "last updated"
          date at the top reflects the most recent revision.
        </p>
      </section>
    </LegalLayout>
  )
}
