export function formatCurrencyBRL(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 2,
  }).format(value)
}

export function formatMonthCount(months: number): string {
  return `${months} meses`
}

export function formatSimilarity(score: number): string {
  return `${Math.round(score * 100)}% similar`
}
