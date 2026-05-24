import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"

import { Button } from "@/components/ui/button"
import { api } from "@/lib/api"

type LayoutPrefs = {
  theme: "light" | "dark"
  sidebar_collapsed: boolean
  hidden_nav_slugs: string[]
}

type PrefsResponse = { layout: LayoutPrefs }

const NAV_OPTIONS = [
  { slug: "dashboard", label: "Dashboard" },
  { slug: "reports", label: "Reports" },
  { slug: "inventory", label: "Inventory" },
  { slug: "bom", label: "BOM" },
  { slug: "customers", label: "Customers" },
  { slug: "sales", label: "Sales" },
  { slug: "pos", label: "POS" },
  { slug: "suppliers", label: "Suppliers" },
  { slug: "purchases", label: "Purchases" },
  { slug: "promotions", label: "Promotions" },
]

export function SettingsLayoutPage() {
  const queryClient = useQueryClient()
  const { data } = useQuery({
    queryKey: ["preferences"],
    queryFn: async () => {
      const res = await api.get<PrefsResponse>("/v1/users/me/preferences")
      return res.data.layout
    },
  })

  const [theme, setTheme] = useState<"light" | "dark">("light")
  const [collapsed, setCollapsed] = useState(false)
  const [hidden, setHidden] = useState<string[]>([])

  useEffect(() => {
    if (data) {
      setTheme(data.theme)
      setCollapsed(data.sidebar_collapsed)
      setHidden(data.hidden_nav_slugs)
    }
  }, [data])

  const save = useMutation({
    mutationFn: async () => {
      await api.patch("/v1/users/me/preferences", {
        layout: { theme, sidebar_collapsed: collapsed, hidden_nav_slugs: hidden },
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["preferences"] })
      document.documentElement.classList.toggle("dark", theme === "dark")
    },
  })

  function toggleHidden(slug: string) {
    setHidden((prev) =>
      prev.includes(slug) ? prev.filter((s) => s !== slug) : [...prev, slug],
    )
  }

  return (
    <div className="mx-auto max-w-lg space-y-6 p-6">
      <div>
        <h1 className="text-lg font-semibold">Layout settings</h1>
        <p className="text-sm text-muted-foreground">
          Customize your sidebar and appearance. Changes apply to your account only.
        </p>
      </div>

      <section className="space-y-2">
        <label className="text-sm font-medium">Theme</label>
        <select
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          value={theme}
          onChange={(e) => setTheme(e.target.value as "light" | "dark")}
        >
          <option value="light">Light</option>
          <option value="dark">Dark</option>
        </select>
      </section>

      <section className="flex items-center gap-2">
        <input
          id="collapsed"
          type="checkbox"
          checked={collapsed}
          onChange={(e) => setCollapsed(e.target.checked)}
        />
        <label htmlFor="collapsed" className="text-sm">
          Collapse sidebar
        </label>
      </section>

      <section className="space-y-2">
        <p className="text-sm font-medium">Hide navigation items</p>
        <ul className="space-y-1">
          {NAV_OPTIONS.map((opt) => (
            <li key={opt.slug} className="flex items-center gap-2">
              <input
                id={`hide-${opt.slug}`}
                type="checkbox"
                checked={hidden.includes(opt.slug)}
                onChange={() => toggleHidden(opt.slug)}
              />
              <label htmlFor={`hide-${opt.slug}`} className="text-sm">
                {opt.label}
              </label>
            </li>
          ))}
        </ul>
      </section>

      <Button onClick={() => save.mutate()} disabled={save.isPending}>
        {save.isPending ? "Saving…" : "Save layout"}
      </Button>
    </div>
  )
}
