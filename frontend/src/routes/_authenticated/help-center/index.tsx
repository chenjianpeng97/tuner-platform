import { createFileRoute } from '@tanstack/react-router'
import { HelpCenterTemplate } from '@/features/template/help-center'

export const Route = createFileRoute('/_authenticated/help-center/')({
  component: HelpCenterTemplate,
})
