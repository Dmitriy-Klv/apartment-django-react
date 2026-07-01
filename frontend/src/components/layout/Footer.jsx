export function Footer() {
  return (
    <footer className="flex flex-col gap-4 border-t border-border py-8 text-sm text-muted-foreground md:flex-row md:items-center md:justify-between">
      <p>© {new Date().getFullYear()} SoftStay. All rights reserved.</p>
      <div className="flex gap-6">
        <span>Privacy policy</span>
        <span>Terms of service</span>
        <span>Contact</span>
      </div>
    </footer>
  )
}
