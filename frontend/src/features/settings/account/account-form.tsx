import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useTranslation } from 'react-i18next'
import { toast } from 'sonner'
import { changePassword } from '@/api/account'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { PasswordInput } from '@/components/password-input'

function createAccountPasswordSchema(t: (key: string) => string) {
  return z
    .object({
      current_password: z.string().min(1, t('account.validation.currentRequired')),
      new_password: z.string().min(7, t('account.validation.newMin7')),
      confirmPassword: z.string().min(1, t('account.validation.confirmRequired')),
    })
    .refine((data) => data.new_password === data.confirmPassword, {
      message: t('account.validation.mismatch'),
      path: ['confirmPassword'],
    })
}

type AccountPasswordValues = z.infer<ReturnType<typeof createAccountPasswordSchema>>

export function AccountForm() {
  const { t } = useTranslation('business')

  const form = useForm<AccountPasswordValues>({
    resolver: zodResolver(createAccountPasswordSchema(t)),
    defaultValues: {
      current_password: '',
      new_password: '',
      confirmPassword: '',
    },
  })

  async function onSubmit(data: AccountPasswordValues) {
    try {
      await changePassword({
        current_password: data.current_password,
        new_password: data.new_password,
      })
      toast.success(t('account.changed'))
      form.reset()
    } catch {
      toast.error(t('account.changeFailed'))
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className='space-y-6'>
        <FormField
          control={form.control}
          name='current_password'
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t('account.currentPassword')}</FormLabel>
              <FormControl>
                <PasswordInput placeholder='******' {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name='new_password'
          render={({ field }) => (
            <FormItem>
              <FormLabel>{t('account.newPassword')}</FormLabel>
              <FormControl>
                <PasswordInput placeholder='******' {...field} />
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
              <FormLabel>{t('account.confirmPassword')}</FormLabel>
              <FormControl>
                <PasswordInput placeholder='******' {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type='submit'>{t('account.submit')}</Button>
      </form>
    </Form>
  )
}
