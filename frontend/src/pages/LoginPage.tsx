import { zodResolver } from "@hookform/resolvers/zod"
import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { useLocation, useNavigate, type Location } from "react-router-dom"
import { toast } from "sonner"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import { getLoginErrorMessage, useAuth } from "@/context/AuthContext"

const schema = z.object({
  email: z.string().email("Enter a valid email"),
  password: z.string().min(1, "Password is required"),
})

type FormValues = z.infer<typeof schema>

export function LoginPage() {
  const { login, user, permissions } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: Location } | null)?.from?.pathname

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" },
  })

  useEffect(() => {
    if (!user) return
    const defaultHome = permissions.includes("reports.dashboard.read")
      ? "/dashboard"
      : permissions.includes("sales.pos.use")
        ? "/pos"
        : "/settings/profile"
    const target = from && from !== "/login" ? from : defaultHome
    navigate(target, { replace: true })
  }, [user, permissions, navigate, from])

  const onSubmit = form.handleSubmit(async (values) => {
    try {
      await login(values.email, values.password)
      toast.success("Signed in")
    } catch (error) {
      toast.error(getLoginErrorMessage(error))
    }
  })

  return (
    <div className="flex min-h-svh bg-workspace">
      <div className="hidden w-2/5 shrink-0 bg-sidebar lg:flex lg:flex-col lg:justify-center lg:px-10">
        <span className="text-2xl font-semibold text-sidebar-foreground">ERP</span>
        <p className="mt-3 max-w-sm text-sm text-sidebar-foreground/80">
          Modern inventory, sales, and purchasing for your business.
        </p>
      </div>
      <div className="flex flex-1 items-center justify-center px-4 py-10">
        <div className="w-full max-w-md rounded-md border border-border bg-card p-8 shadow-none">
          <h1 className="text-xl font-semibold text-foreground">Sign in</h1>
          {import.meta.env.DEV ? (
            <p className="mt-1 text-sm text-muted-foreground">
              Local dev: use credentials from backend/.env (ADMIN_EMAIL / ADMIN_PASSWORD).
            </p>
          ) : null}
          <form className="mt-6 space-y-4" onSubmit={onSubmit}>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground" htmlFor="email">
                Email
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none ring-ring/50 focus-visible:ring-3"
                {...form.register("email")}
              />
              {form.formState.errors.email ? (
                <p className="text-xs text-destructive">{form.formState.errors.email.message}</p>
              ) : null}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm text-foreground outline-none ring-ring/50 focus-visible:ring-3"
                {...form.register("password")}
              />
              {form.formState.errors.password ? (
                <p className="text-xs text-destructive">{form.formState.errors.password.message}</p>
              ) : null}
            </div>
            <Button className="w-full" type="submit" disabled={form.formState.isSubmitting}>
              {form.formState.isSubmitting ? "Signing in…" : "Sign in"}
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}
