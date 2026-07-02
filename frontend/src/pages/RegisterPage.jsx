import { zodResolver } from '@hookform/resolvers/zod'
import { Building2, Loader2, Users } from 'lucide-react'
import { useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { registerUser } from '@/api/auth'
import { AuthLayout } from '@/components/layout/AuthLayout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/context/AuthContext'

const registerSchema = z
  .object({
    username: z
      .string()
      .min(3, 'At least 3 characters')
      .max(150)
      .regex(/^[\w.@+-]+$/, 'Letters, numbers and . @ + - _ only'),
    email: z.string().email('Enter a valid email address'),
    password: z.string().min(8, 'At least 8 characters'),
    confirmPassword: z.string(),
    role: z.enum(['tenant', 'lessor']),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })

const ROLE_OPTIONS = [
  { value: 'tenant', label: 'I want to rent', icon: Users },
  { value: 'lessor', label: 'I want to list a property', icon: Building2 },
]

export function RegisterPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [serverError, setServerError] = useState('')

  const {
    register,
    handleSubmit,
    control,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(registerSchema),
    defaultValues: { role: 'tenant' },
  })

  async function onSubmit(values) {
    setServerError('')
    try {
      const session = await registerUser(values)
      login(session)
      navigate('/')
    } catch (error) {
      const data = error.response?.data
      setServerError(data?.email?.[0] || data?.username?.[0] || data?.detail || 'Something went wrong. Please try again.')
    }
  }

  return (
    <AuthLayout title="Create your account" subtitle="Join SoftStay to rent or list a home in minutes.">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        <Controller
          control={control}
          name="role"
          render={({ field }) => (
            <div className="grid grid-cols-2 gap-3">
              {ROLE_OPTIONS.map(({ value, label, icon: Icon }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => field.onChange(value)}
                  className={`flex flex-col items-center gap-2 rounded-2xl border p-4 text-sm font-medium transition-colors ${
                    field.value === value
                      ? 'border-primary bg-primary text-primary-foreground'
                      : 'border-border text-muted-foreground hover:border-foreground/30'
                  }`}
                >
                  <Icon className="size-5" />
                  {label}
                </button>
              ))}
            </div>
          )}
        />

        <div className="space-y-1.5">
          <Label htmlFor="username">Username</Label>
          <Input id="username" autoComplete="username" {...register('username')} />
          {errors.username && <p className="text-xs text-destructive">{errors.username.message}</p>}
          <p className="text-xs text-muted-foreground">
            This is a portfolio demo — feel free to use a nickname instead of your real name.
          </p>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" autoComplete="email" {...register('email')} />
          {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="password">Password</Label>
          <Input id="password" type="password" autoComplete="new-password" {...register('password')} />
          {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="confirmPassword">Confirm password</Label>
          <Input id="confirmPassword" type="password" autoComplete="new-password" {...register('confirmPassword')} />
          {errors.confirmPassword && <p className="text-xs text-destructive">{errors.confirmPassword.message}</p>}
        </div>

        {serverError && <p className="text-sm text-destructive">{serverError}</p>}

        <Button type="submit" size="lg" className="w-full rounded-full" disabled={isSubmitting}>
          {isSubmitting ? <Loader2 className="size-4 animate-spin" /> : 'Create account'}
        </Button>

        <p className="text-center text-sm text-muted-foreground">
          Already have an account?{' '}
          <Link to="/login" className="font-medium text-foreground underline underline-offset-4">
            Sign in
          </Link>
        </p>
      </form>
    </AuthLayout>
  )
}
