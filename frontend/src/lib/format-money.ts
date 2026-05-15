export function formatMoney(amount: number | string): string {
  const n = typeof amount === "string" ? Number.parseFloat(amount) : amount
  if (!Number.isFinite(n)) return "$0.00"
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency: "USD",
  }).format(n)
}
