import { useQuery } from '@tanstack/react-query'
import { Building2, Loader2, LogOut, Mail, User, Users } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { getMe } from '@/api/auth'
import { PageLayout } from '@/components/layout/PageLayout'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/context/AuthContext'

export function ProfilePage() {
  const navigate = useNavigate()
  const { logout } = useAuth()
  const { data: me, isLoading } = useQuery({ queryKey: ['me'], queryFn: getMe })

  async function handleLogout() {
    await logout()
    navigate('/')
  }

  return (
    <PageLayout>
      <div className="mx-auto max-w-lg space-y-8">
        <h1 className="text-2xl font-semibold">Your profile</h1>

        {isLoading ? (
          <Loader2 className="size-6 animate-spin text-muted-foreground" />
        ) : (
          me && (
            <div className="space-y-4 rounded-3xl border border-border bg-card p-6">
              <div className="flex items-center gap-3">
                <span className="flex size-11 items-center justify-center rounded-full bg-accent/10 text-accent">
                  <User className="size-5" />
                </span>
                <div>
                  <p className="font-semibold">
                    {me.first_name} {me.last_name}
                  </p>
                  <p className="text-sm text-muted-foreground capitalize">{me.role}</p>
                </div>
              </div>

              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <Mail className="size-4" />
                {me.email}
              </div>

              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                {me.role === 'lessor' ? <Building2 className="size-4" /> : <Users className="size-4" />}
                {me.role === 'lessor' ? 'Landlord account' : 'Tenant account'}
              </div>

              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                Member since {new Date(me.created_at).toLocaleDateString('en-GB')}
              </div>
            </div>
          )
        )}

        <Button variant="outline" size="lg" className="gap-2 rounded-full" onClick={handleLogout}>
          <LogOut className="size-4" />
          Log out
        </Button>

        <p className="text-xs leading-relaxed text-muted-foreground">
          Your data is only used to operate your account and is never shared with third parties. To request account
          deletion, contact support — this feature is not yet available for self-service.
        </p>
      </div>
    </PageLayout>
  )
}
