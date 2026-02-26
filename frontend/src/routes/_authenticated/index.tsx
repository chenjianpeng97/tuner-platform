import { createFileRoute } from '@tanstack/react-router'
import { Dashboard } from '@/features/template/dashboard'

export const Route = createFileRoute('/_authenticated/')({
  component: Dashboard,
})
