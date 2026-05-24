import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { useQuery } from "@tanstack/react-query"
import {
  Boxes,
  Building2,
  FileText,
  Factory,
  Handshake,
  MapPin,
  Package,
  Scroll,
  Search,
  ShoppingCart,
  Users,
  Warehouse,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { useNavigate } from "react-router-dom"

import { cn } from "@/lib/utils"
import { useAuth } from "@/context/AuthContext"
import {
  fetchGlobalSearch,
  SEARCH_ENTITY_LABELS,
  type SearchEntityType,
  type SearchHit,
} from "@/features/search/search-api"
import { filterNavByPermissions, type NavItem } from "@/lib/nav-config"
import { api } from "@/lib/api"

type LayoutPrefs = {
  hidden_nav_slugs?: string[]
}

type SpotlightRow =
  | { kind: "page"; key: string; label: string; to: string; icon: LucideIcon }
  | { kind: "record"; key: string; hit: SearchHit; icon: LucideIcon }

const ENTITY_ICONS: Record<SearchEntityType, LucideIcon> = {
  customer: Users,
  sale: ShoppingCart,
  erp_document: FileText,
  purchase: Package,
  production_order: Factory,
  supplier: Building2,
  product: Boxes,
  material_roll: Scroll,
  warehouse: Warehouse,
  storage_location: MapPin,
  module_record: FileText,
  crm_lead: Handshake,
  crm_opportunity: Handshake,
  crm_contact: Users,
}

function flattenNavItems(
  permissions: string[],
  hiddenSlugs: string[],
): NavItem[] {
  return filterNavByPermissions(permissions, hiddenSlugs).flatMap((g) => g.items)
}

function navRows(items: NavItem[]): SpotlightRow[] {
  return items.map((item) => ({
    kind: "page" as const,
    key: `page:${item.to}`,
    label: item.label,
    to: item.to,
    icon: item.icon,
  }))
}

function recordRows(hits: SearchHit[]): SpotlightRow[] {
  return hits.map((hit) => ({
    kind: "record" as const,
    key: `record:${hit.entity_type}:${hit.entity_id}`,
    hit,
    icon: ENTITY_ICONS[hit.entity_type] ?? FileText,
  }))
}

export function SpotlightSearch() {
  const navigate = useNavigate()
  const { permissions } = useAuth()
  const inputRef = useRef<HTMLInputElement>(null)
  const rootRef = useRef<HTMLDivElement>(null)

  const [query, setQuery] = useState("")
  const [focused, setFocused] = useState(false)
  const [highlight, setHighlight] = useState(0)

  const { data: prefs } = useQuery({
    queryKey: ["preferences"],
    queryFn: async () => {
      const res = await api.get<{ layout: LayoutPrefs }>("/v1/users/me/preferences")
      return res.data.layout
    },
  })

  const navItems = useMemo(
    () => flattenNavItems(permissions, prefs?.hidden_nav_slugs ?? []),
    [permissions, prefs?.hidden_nav_slugs],
  )

  const trimmed = query.trim()
  const searchEnabled = trimmed.length >= 2

  const recordsQuery = useQuery({
    queryKey: ["global-search", trimmed],
    queryFn: () => fetchGlobalSearch({ q: trimmed, limit: 20 }),
    enabled: searchEnabled,
    staleTime: 30_000,
  })

  const pageMatches = useMemo(() => {
    if (!trimmed) return navItems.slice(0, 6)
    const q = trimmed.toLowerCase()
    return navItems.filter(
      (item) =>
        item.label.toLowerCase().includes(q) ||
        item.to.toLowerCase().includes(q),
    )
  }, [navItems, trimmed])

  const rows: SpotlightRow[] = useMemo(() => {
    const pages = navRows(pageMatches)
    if (!searchEnabled) return pages
    const records = recordRows(recordsQuery.data?.results ?? [])
    return [...pages, ...records]
  }, [pageMatches, searchEnabled, recordsQuery.data?.results])

  const open = focused && rows.length > 0

  const goTo = useCallback(
    (to: string) => {
      navigate(to)
      setQuery("")
      setFocused(false)
      setHighlight(0)
      inputRef.current?.blur()
    },
    [navigate],
  )

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault()
        inputRef.current?.focus()
        setFocused(true)
      }
    }
    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [])

  useEffect(() => {
    if (!open) return
    const onPointerDown = (e: MouseEvent) => {
      if (!rootRef.current?.contains(e.target as Node)) {
        setFocused(false)
      }
    }
    document.addEventListener("mousedown", onPointerDown)
    return () => document.removeEventListener("mousedown", onPointerDown)
  }, [open])

  const pageRows = rows.filter((r) => r.kind === "page")
  const recordRowsList = rows.filter((r) => r.kind === "record")

  return (
    <div
      ref={rootRef}
      className={cn(
        "relative w-full transition-[max-width] duration-500 ease-out",
        focused ? "max-w-2xl" : "max-w-md",
      )}
      data-testid="spotlight-search"
    >
      <div
        className={cn(
          "spotlight-search-shell flex h-11 items-center gap-2 rounded-full border border-border/80 bg-muted/50 px-4 shadow-sm backdrop-blur-sm",
          focused && "spotlight-search-active border-primary/30 bg-card",
        )}
      >
        <Search
          className={cn(
            "size-4 shrink-0 text-muted-foreground transition-transform duration-300",
            focused && "scale-110 text-primary",
          )}
          aria-hidden
        />
        <input
          ref={inputRef}
          type="search"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setHighlight(0)
          }}
          onFocus={() => setFocused(true)}
          onBlur={() => {
            window.setTimeout(() => setFocused(false), 120)
          }}
          onKeyDown={(e) => {
            if (e.key === "Escape") {
              setQuery("")
              setFocused(false)
              inputRef.current?.blur()
              return
            }
            if (e.key === "ArrowDown") {
              e.preventDefault()
              setHighlight((i) => Math.min(i + 1, rows.length - 1))
              return
            }
            if (e.key === "ArrowUp") {
              e.preventDefault()
              setHighlight((i) => Math.max(i - 1, 0))
              return
            }
            const row = rows[highlight]
            if (e.key === "Enter" && row) {
              e.preventDefault()
              goTo(row.kind === "page" ? row.to : row.hit.route)
            }
          }}
          placeholder="Search pages and records you can access…"
          className="min-w-0 flex-1 bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
          aria-label="Spotlight search"
          aria-expanded={open}
          aria-controls="spotlight-results"
          aria-autocomplete="list"
          role="combobox"
        />
        <kbd
          className={cn(
            "hidden shrink-0 rounded-md border border-border bg-background/80 px-1.5 py-0.5 text-[0.65rem] font-medium text-muted-foreground transition-opacity duration-300 sm:inline",
            focused && "pointer-events-none opacity-0",
          )}
        >
          ⌘K
        </kbd>
      </div>

      {open ? (
        <ul
          id="spotlight-results"
          role="listbox"
          className="spotlight-results-panel absolute top-[calc(100%+0.5rem)] z-50 max-h-80 w-full overflow-y-auto rounded-xl border border-border bg-popover p-1.5 shadow-lg"
        >
          {searchEnabled && recordsQuery.isFetching ? (
            <li className="px-3 py-2 text-xs text-muted-foreground">Searching…</li>
          ) : null}
          {pageRows.length > 0 ? (
            <li>
              <p className="px-3 pt-2 pb-1 text-[0.65rem] font-semibold uppercase tracking-wider text-muted-foreground">
                Pages
              </p>
            </li>
          ) : null}
          {pageRows.map((row) => {
            const index = rows.indexOf(row)
            const selected = index === highlight
            const Icon = row.icon
            return (
              <li key={row.key}>
                <button
                  type="button"
                  role="option"
                  aria-selected={selected}
                  className={cn(
                    "flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-sm transition-colors",
                    selected
                      ? "bg-accent text-accent-foreground"
                      : "text-popover-foreground hover:bg-muted",
                  )}
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => goTo(row.to)}
                  onMouseEnter={() => setHighlight(index)}
                >
                  <Icon className="size-4 shrink-0 opacity-80" aria-hidden />
                  <span className="min-w-0 flex-1 font-medium">{row.label}</span>
                  <span className="ml-1 shrink-0 truncate text-xs text-muted-foreground">
                    {row.to}
                  </span>
                </button>
              </li>
            )
          })}
          {recordRowsList.length > 0 ? (
            <li>
              <p className="px-3 pt-2 pb-1 text-[0.65rem] font-semibold uppercase tracking-wider text-muted-foreground">
                Records
              </p>
            </li>
          ) : null}
          {recordRowsList.map((row) => {
            const index = rows.indexOf(row)
            const selected = index === highlight
            const Icon = row.icon
            return (
              <li key={row.key}>
                <button
                  type="button"
                  role="option"
                  aria-selected={selected}
                  className={cn(
                    "flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-left text-sm transition-colors",
                    selected
                      ? "bg-accent text-accent-foreground"
                      : "text-popover-foreground hover:bg-muted",
                  )}
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => goTo(row.hit.route)}
                  onMouseEnter={() => setHighlight(index)}
                >
                  <Icon className="size-4 shrink-0 opacity-80" aria-hidden />
                  <span className="min-w-0 flex-1">
                    <span className="block truncate font-medium">{row.hit.title}</span>
                    {row.hit.subtitle ? (
                      <span className="block truncate text-xs text-muted-foreground">
                        {SEARCH_ENTITY_LABELS[row.hit.entity_type]} · {row.hit.subtitle}
                      </span>
                    ) : null}
                  </span>
                  <span className="ml-1 shrink-0 truncate text-xs text-muted-foreground">
                    {SEARCH_ENTITY_LABELS[row.hit.entity_type]}
                  </span>
                </button>
              </li>
            )
          })}
          {searchEnabled &&
          !recordsQuery.isFetching &&
          recordsQuery.data?.results.length === 0 &&
          pageMatches.length === 0 ? (
            <li className="px-3 py-3 text-sm text-muted-foreground">
              No results you have access to.
            </li>
          ) : null}
        </ul>
      ) : null}
    </div>
  )
}
