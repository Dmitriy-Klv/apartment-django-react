import { LegalLayout } from '@/components/layout/LegalLayout'

export function TermsOfServicePage() {
  return (
    <LegalLayout title="Terms of Service" updated="July 2026">
      <p>
        These terms explain how SoftStay works. SoftStay is a demonstration project built for an educational
        software development portfolio — by using it, you agree that it is not a commercial service, and these terms
        do not create a binding commercial agreement.
      </p>

      <section className="space-y-2">
        <h2>1. Nature of the service</h2>
        <p>
          SoftStay simulates an apartment rental platform: creating listings, searching and filtering them, making
          bookings, and leaving reviews. No real money changes hands anywhere in this application, and no listing on
          this site represents a real, available property. Images, addresses, prices, reviews, and other listing
          information are fictional or used solely for demonstration purposes and should not be relied upon for
          real-world decisions.
        </p>
      </section>

      <section className="space-y-2">
        <h2>2. Eligibility and accounts</h2>
        <p>
          You may register as a tenant or a landlord using an email address, a password, and a username, if you are
          at least 16 years old, or the minimum age required for consent under applicable local law. Registration
          does not ask for your real name, and nobody is required or expected to enter one — a nickname or pseudonym
          is fine for the username, since this is a demonstration project built for a portfolio rather than a live
          commercial service. You are responsible for the accuracy of the information you provide and for keeping
          your password confidential. Accounts are for demonstration and testing purposes only.
        </p>
      </section>

      <section className="space-y-2">
        <h2>3. Listings and bookings</h2>
        <p>
          Landlord accounts may publish listings; tenant accounts may request bookings against those listings.
          Booking status changes (confirmation, rejection, cancellation, check-in) follow the rules described on the
          listing and booking pages. Because this is a demo, we ask that you don&apos;t submit real personal data of
          other people or misleading listing content.
        </p>
      </section>

      <section className="space-y-2">
        <h2>4. Reviews and public content</h2>
        <p>
          Reviews may only be left after a booking has been marked as checked in, to keep them tied to a genuine
          interaction within the app. Review content should be honest and relevant to the demonstrated stay. Reviews
          and listing descriptions are visible to every visitor of this site — do not include personal, confidential,
          or sensitive information about yourself or anyone else in this content.
        </p>
      </section>

      <section className="space-y-2">
        <h2>5. Acceptable use</h2>
        <p>
          You agree not to use SoftStay to store or transmit real sensitive personal data, upload malicious code or
          spam, post copyrighted material without permission or content that infringes the rights of others, attempt
          to disrupt or gain unauthorized access to the application, or use the platform for any unlawful purpose.
        </p>
      </section>

      <section className="space-y-2">
        <h2>6. Intellectual property</h2>
        <p>
          Unless otherwise stated, the source code, design, branding, and interface of SoftStay remain the
          intellectual property of the project creator. Content you submit (such as listing text or reviews) remains
          yours, and is displayed within the application solely to demonstrate its functionality.
        </p>
      </section>

      <section className="space-y-2">
        <h2>7. No warranty</h2>
        <p>
          SoftStay is provided "as is", without warranties of any kind, express or implied, including — but not
          limited to — availability, accuracy, or fitness for a particular purpose. As a portfolio project, its
          features, data, and demo content may change, be reset, or be taken offline at any time without notice.
        </p>
      </section>

      <section className="space-y-2">
        <h2>8. Limitation of liability</h2>
        <p>
          To the fullest extent permitted by law, the creator of this project is not liable for any damages arising
          from the use of, or inability to use, this application, since it does not process real transactions or
          real property listings. You should not rely on this application for travel planning, accommodation
          decisions, or storage of important information.
        </p>
      </section>

      <section className="space-y-2">
        <h2>9. Availability</h2>
        <p>
          The application may be unavailable from time to time due to maintenance, development, hosting issues, or
          other technical reasons outside our control.
        </p>
      </section>

      <section className="space-y-2">
        <h2>10. Termination</h2>
        <p>
          You may delete your own account at any time from your profile page, after confirming your password. This
          anonymizes your email and username and signs you out everywhere; bookings and reviews tied to your account
          remain visible to other users without your identity attached, since they are also linked to other users'
          own history. Accounts and their associated data may also be removed at any time by us, for example during
          routine cleanup of demo and test data on this project.
        </p>
      </section>

      <section className="space-y-2">
        <h2>11. Changes to these terms</h2>
        <p>
          These terms may be updated as the project evolves. The "last updated" date at the top reflects the most
          recent revision. Questions can be sent through the Contact page.
        </p>
      </section>
    </LegalLayout>
  )
}
