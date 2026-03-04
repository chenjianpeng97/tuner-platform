'use client'

import { z } from 'zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { PasswordInput } from '@/components/password-input'
import { SelectDropdown } from '@/components/select-dropdown'
import { roles } from '../data/data'
import { type UsersRowViewModel } from '../model'
import { useUsers } from './users-provider'

const formSchema = z
  .object({
    username: z.string().min(1, 'Username is required.'),
    role: z.enum(['super_admin', 'admin', 'user']),
    password: z.string().optional(),
    confirmPassword: z.string().optional(),
    isEdit: z.boolean(),
  })
  .superRefine((data, ctx) => {
    const password = data.password?.trim() ?? ''
    const confirmPassword = data.confirmPassword?.trim() ?? ''

    if (!data.isEdit) {
      if (password.length < 8) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: 'Password must be at least 8 characters long.',
          path: ['password'],
        })
      }
    }

    if (password.length > 0 && password.length < 8) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Password must be at least 8 characters long.',
        path: ['password'],
      })
    }

    if (password.length > 0 && !/[a-z]/.test(password)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Password must contain at least one lowercase letter.',
        path: ['password'],
      })
    }

    if (password.length > 0 && !/\d/.test(password)) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Password must contain at least one number.',
        path: ['password'],
      })
    }

    if (password !== confirmPassword) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: "Passwords don't match.",
        path: ['confirmPassword'],
      })
    }
  })

type UserForm = z.infer<typeof formSchema>

type UserActionDialogProps = {
  currentRow?: UsersRowViewModel
  open: boolean
  onOpenChange: (open: boolean) => void
}

function toDefaultValues(currentRow?: UsersRowViewModel): UserForm {
  const isEdit = Boolean(currentRow)
  return {
    username: currentRow?.username ?? '',
    role: currentRow?.role ?? 'user',
    password: '',
    confirmPassword: '',
    isEdit,
  }
}

export function UsersActionDialog({
  currentRow,
  open,
  onOpenChange,
}: UserActionDialogProps) {
  const isEdit = !!currentRow
  const { createUser, setPassword, setUserAdmin } = useUsers()
  const roleItems = isEdit
    ? currentRow?.role === 'super_admin'
      ? roles.filter((role) => role.value === 'super_admin')
      : roles.filter((role) => role.value !== 'super_admin')
    : roles

  const form = useForm<UserForm>({
    resolver: zodResolver(formSchema),
    defaultValues: toDefaultValues(currentRow),
  })

  useEffect(() => {
    form.reset(toDefaultValues(currentRow))
  }, [currentRow, form])

  const onSubmit = async (values: UserForm) => {
    const password = values.password?.trim() ?? ''

    if (!isEdit) {
      await toast.promise(
        createUser({
          username: values.username,
          password,
          role: values.role,
        }),
        {
          loading: 'Creating user...',
          success: 'User created',
          error: 'Failed to create user',
        }
      )
      onOpenChange(false)
      return
    }

    if (!currentRow) return

    const jobs: Array<Promise<void>> = []
    if (password.length > 0) {
      jobs.push(setPassword({ userId: currentRow.id, password }))
    }

    const shouldBeAdmin = values.role === 'admin'
    const isAdminNow = currentRow.role === 'admin'
    if (currentRow.role !== 'super_admin' && shouldBeAdmin !== isAdminNow) {
      jobs.push(setUserAdmin({ userId: currentRow.id, isAdmin: shouldBeAdmin }))
    }

    if (jobs.length === 0) {
      toast.info('No changes to apply')
      onOpenChange(false)
      return
    }

    await toast.promise(Promise.all(jobs), {
      loading: 'Updating user...',
      success: 'User updated',
      error: 'Failed to update user',
    })
    onOpenChange(false)
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(state) => {
        form.reset(toDefaultValues(currentRow))
        onOpenChange(state)
      }}
    >
      <DialogContent className='sm:max-w-lg'>
        <DialogHeader className='text-start'>
          <DialogTitle>{isEdit ? 'Edit User' : 'Add New User'}</DialogTitle>
          <DialogDescription>
            {isEdit
              ? 'Update role or reset password for this user.'
              : 'Create a new user account.'}
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form
            id='user-form'
            onSubmit={form.handleSubmit(onSubmit)}
            className='space-y-4'
          >
            <FormField
              control={form.control}
              name='username'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Username</FormLabel>
                  <FormControl>
                    <Input
                      placeholder='john_doe'
                      autoComplete='off'
                      disabled={isEdit}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name='role'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Role</FormLabel>
                  <SelectDropdown
                    defaultValue={field.value}
                    onValueChange={field.onChange}
                    isControlled
                    placeholder='Select a role'
                    items={roleItems.map(({ label, value }) => ({
                      label,
                      value,
                    }))}
                    disabled={currentRow?.role === 'super_admin'}
                  />
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name='password'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    {isEdit ? 'New Password (optional)' : 'Password'}
                  </FormLabel>
                  <FormControl>
                    <PasswordInput
                      placeholder='At least 8 chars, with lowercase and number'
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name='confirmPassword'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Confirm Password</FormLabel>
                  <FormControl>
                    <PasswordInput
                      placeholder='Repeat password'
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </form>
        </Form>
        <DialogFooter>
          <Button type='submit' form='user-form'>
            {isEdit ? 'Save changes' : 'Create user'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
