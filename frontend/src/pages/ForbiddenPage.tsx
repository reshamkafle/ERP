import { Link } from "react-router-dom"

import { Button } from "@/components/ui/button"

export function ForbiddenPage() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-4 p-8 text-center">
      <h1 className="text-lg font-semibold">Access denied</h1>
      <p className="max-w-md text-sm text-muted-foreground">
        You do not have permission to view this page. Contact your administrator if you need
        access.
      </p>
      <Link to="/">
        <Button variant="outline" size="sm" type="button">
          Go home
        </Button>
      </Link>
    </div>
  )
}
