import z from 'zod'
import { createFileRoute } from '@tanstack/react-router'
import { Users } from '@/features/users'

const arraySearchSchema = z
  .union([z.string(), z.array(z.string())])
  .optional()
  .transform((value) => {
    if (value === undefined) return undefined
    return Array.isArray(value) ? value : [value]
  })

const usersSearchSchema = z.object({
  page: z.number().optional().catch(1),
  pageSize: z.number().optional().catch(10),
  sortingField: z.string().optional().catch('username'),
  sortingOrder: z.union([z.literal('ASC'), z.literal('DESC')]).optional().catch('ASC'),
  username: z.string().optional(),
  status: arraySearchSchema,
  role: arraySearchSchema,
})

export const Route = createFileRoute('/_authenticated/users/')({
  validateSearch: usersSearchSchema,
  component: Users,
})
