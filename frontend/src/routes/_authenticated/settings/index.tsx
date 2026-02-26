import { createFileRoute } from '@tanstack/react-router'
import { SettingsProfile } from '@/features/template/settings/profile'

export const Route = createFileRoute('/_authenticated/settings/')({
  component: SettingsProfile,
})
