'use client'

import { z } from 'zod'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useTranslation } from 'react-i18next'
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
import { getRoles } from '../data/data'
import { type UsersRowViewModel } from '../model'
import { useUsers } from './users-provider'

function createFormSchema(t: (key: string) => string) {
  return z
    .object({
      username: z.string().min(1, t('users.dialog.validation.usernameRequired')),
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
            message: t('users.dialog.validation.passwordMin8'),
            path: ['password'],
          })
        }
      }

      if (password.length > 0 && password.length < 8) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: t('users.dialog.validation.passwordMin8'),
          path: ['password'],
        })
      }

      if (password.length > 0 && !/[a-z]/.test(password)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: t('users.dialog.validation.passwordLowercase'),
          path: ['password'],
        })
      }

      if (password.length > 0 && !/\d/.test(password)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: t('users.dialog.validation.passwordNumber'),
          path: ['password'],
        })
      }

      if (password !== confirmPassword) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: t('users.dialog.validation.passwordsMismatch'),
          path: ['confirmPassword'],
        })
      }
    })
}

type UserForm = z.infer<ReturnType<typeof createFormSchema>>

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
  const { t } = useTranslation('business')
  const isEdit = !!currentRow
  const { createUser, setPassword, setUserAdmin } = useUsers()
  const roles = getRoles(t)
  const roleItems = isEdit
    ? currentRow?.role === 'super_admin'
      ? roles.filter((role) => role.value === 'super_admin')
      : roles.filter((role) => role.value !== 'super_admin')
    : roles

  const form = useForm<UserForm>({
    resolver: zodResolver(createFormSchema(t)),
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
          loading: t('users.dialog.creatingUser'),
          success: t('users.dialog.userCreated'),
          error: t('users.dialog.createUserFailed'),
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
      toast.info(t('users.dialog.noChanges'))
      onOpenChange(false)
      return
    }

    await toast.promise(Promise.all(jobs), {
      loading: t('users.dialog.updatingUser'),
      success: t('users.dialog.userUpdated'),
      error: t('users.dialog.updateUserFailed'),
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
          <DialogTitle>
            {isEdit ? t('users.dialog.editTitle') : t('users.dialog.addTitle')}
          </DialogTitle>
          <DialogDescription>
            {isEdit
              ? t('users.dialog.editDescription')
              : t('users.dialog.addDescription')}
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
                  <FormLabel>{t('users.dialog.username')}</FormLabel>
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
                  <FormLabel>{t('users.dialog.role')}</FormLabel>
                  <SelectDropdown
                    defaultValue={field.value}
                    onValueChange={field.onChange}
                    isControlled
                    placeholder={t('users.dialog.selectRole')}
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
                    {isEdit
                      ? t('users.dialog.newPasswordOptional')
                      : t('users.dialog.password')}
                  </FormLabel>
                  <FormControl>
                    <PasswordInput
                      placeholder={t('users.dialog.passwordPlaceholder')}
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
                  <FormLabel>{t('users.dialog.confirmPassword')}</FormLabel>
                  <FormControl>
                    <PasswordInput
                      placeholder={t('users.dialog.confirmPasswordPlaceholder')}
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
            {isEdit ? t('users.dialog.saveChanges') : t('users.dialog.createUser')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
