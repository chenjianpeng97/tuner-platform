import { Check, Languages } from 'lucide-react'
import { toast } from 'sonner'
import { useTranslation } from 'react-i18next'
import { cn } from '@/lib/utils'
import { DEFAULT_LANGUAGE, type SupportedLanguage } from '@/i18n/constants'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'

type LanguageSwitchProps = {
    compact?: boolean
}

export function LanguageSwitch({ compact = false }: LanguageSwitchProps) {
    const { i18n, t } = useTranslation('common')

    const activeLanguage =
        (i18n.resolvedLanguage as SupportedLanguage | undefined) ?? DEFAULT_LANGUAGE

    const switchLanguage = async (language: SupportedLanguage) => {
        if (language === activeLanguage) return
        await i18n.changeLanguage(language)
        toast.success(
            t('language.switched', {
                language:
                    language === 'en' ? t('language.english') : t('language.chinese'),
            })
        )
    }

    if (compact) {
        return (
            <DropdownMenu modal={false}>
                <DropdownMenuTrigger asChild>
                    <Button variant='ghost' size='icon' className='scale-95 rounded-full'>
                        <Languages className='size-[1.2rem]' />
                        <span className='sr-only'>{t('language.label')}</span>
                    </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align='end'>
                    <DropdownMenuItem onClick={() => switchLanguage('en')}>
                        {t('language.english')}
                        <Check
                            size={14}
                            className={cn('ms-auto', activeLanguage !== 'en' && 'hidden')}
                        />
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => switchLanguage('zh')}>
                        {t('language.chinese')}
                        <Check
                            size={14}
                            className={cn('ms-auto', activeLanguage !== 'zh' && 'hidden')}
                        />
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
        )
    }

    return (
        <DropdownMenu modal={false}>
            <DropdownMenuTrigger asChild>
                <Button variant='outline' size='sm' className='gap-2'>
                    <Languages className='size-4' />
                    {activeLanguage.toUpperCase()}
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align='end'>
                <DropdownMenuItem onClick={() => switchLanguage('en')}>
                    {t('language.english')}
                    <Check
                        size={14}
                        className={cn('ms-auto', activeLanguage !== 'en' && 'hidden')}
                    />
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => switchLanguage('zh')}>
                    {t('language.chinese')}
                    <Check
                        size={14}
                        className={cn('ms-auto', activeLanguage !== 'zh' && 'hidden')}
                    />
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}
