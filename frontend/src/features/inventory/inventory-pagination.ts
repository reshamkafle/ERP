/** Page numbers to render, with ellipsis when the range is large. */
export function getTablePageNumbers(current: number, total: number): (number | "ellipsis")[] {
  if (total <= 1) return total === 1 ? [1] : []
  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }

  const pages: (number | "ellipsis")[] = [1]
  const windowStart = Math.max(2, current - 1)
  const windowEnd = Math.min(total - 1, current + 1)

  if (windowStart > 2) {
    pages.push("ellipsis")
  }

  for (let p = windowStart; p <= windowEnd; p++) {
    pages.push(p)
  }

  if (windowEnd < total - 1) {
    pages.push("ellipsis")
  }

  pages.push(total)
  return pages
}
