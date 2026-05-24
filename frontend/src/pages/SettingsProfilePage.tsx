import { useAuth } from "@/context/AuthContext"

export function SettingsProfilePage() {
  const { user } = useAuth()

  return (
    <div className="mx-auto max-w-lg space-y-4 p-6">
      <h1 className="text-lg font-semibold">Profile</h1>
      <dl className="space-y-2 text-sm">
        <div>
          <dt className="text-muted-foreground">Email</dt>
          <dd className="font-medium">{user?.email}</dd>
        </div>
        <div>
          <dt className="text-muted-foreground">Legacy role</dt>
          <dd className="font-medium">{user?.role}</dd>
        </div>
      </dl>
    </div>
  )
}
