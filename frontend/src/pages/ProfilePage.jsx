import { useMutation, useQuery } from '@tanstack/react-query'
import { AlertTriangle, Building2, Loader2, LogOut, Mail, Trash2, User, Users } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { deleteAccount, getMe } from '@/api/auth'
import { PageLayout } from '@/components/layout/PageLayout'
import { Banner } from '@/components/ui/banner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/context/AuthContext'

export function ProfilePage() {
  const navigate = useNavigate()
  const { logout } = useAuth()
  const { data: me, isLoading } = useQuery({ queryKey: ['me'], queryFn: getMe })
  const [showDeleteForm, setShowDeleteForm] = useState(false)
  const [password, setPassword] = useState('')
  const [deleteError, setDeleteError] = useState('')

  async function handleLogout() {
    await logout()
    navigate('/')
  }

  const deleteMutation = useMutation({
    mutationFn: () => deleteAccount(password),
    onSuccess: async () => {
      await logout()
      navigate('/')
    },
    onError: (error) => {
      const data = error.response?.data
      setDeleteError(data?.password?.[0] || data?.detail || 'Could not delete account. Please try again.')
    },
  })

  function handleDeleteSubmit(event) {
    event.preventDefault()
    setDeleteError('')
    deleteMutation.mutate()
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
                    {me.username}
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

        <div className="space-y-3 rounded-3xl border border-destructive/20 bg-destructive/5 p-6">
          <div className="flex items-center gap-2 font-semibold text-destructive">
            <AlertTriangle className="size-4" />
            Danger zone
          </div>
          <p className="text-sm text-muted-foreground">
            Deleting your account anonymizes your email and username and signs you out everywhere. Your bookings and
            reviews stay visible to other users, without your identity attached, so a landlord or tenant on the
            other side of a booking doesn&apos;t lose their own history. This cannot be undone.
          </p>

          {!showDeleteForm ? (
            <Button variant="destructive" size="sm" className="gap-2" onClick={() => setShowDeleteForm(true)}>
              <Trash2 className="size-3.5" />
              Delete account
            </Button>
          ) : (
            <form onSubmit={handleDeleteSubmit} className="space-y-3">
              <div className="space-y-1.5">
                <Label htmlFor="delete-password">Confirm your password</Label>
                <Input
                  id="delete-password"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                />
              </div>

              <Banner variant="error">{deleteError}</Banner>

              <div className="flex gap-2">
                <Button type="submit" variant="destructive" size="sm" disabled={deleteMutation.isPending}>
                  {deleteMutation.isPending ? <Loader2 className="size-4 animate-spin" /> : 'Permanently delete'}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setShowDeleteForm(false)
                    setPassword('')
                    setDeleteError('')
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          )}
        </div>
      </div>
    </PageLayout>
  )
}
