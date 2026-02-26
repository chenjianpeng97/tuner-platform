import { createFileRoute } from '@tanstack/react-router'
import { Chats } from '@/features/template/chats'

export const Route = createFileRoute('/_authenticated/chats/')({
  component: Chats,
})
