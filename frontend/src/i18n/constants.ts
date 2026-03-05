export const SUPPORTED_LANGUAGES = ['en', 'zh'] as const

export type SupportedLanguage = (typeof SUPPORTED_LANGUAGES)[number]

export const DEFAULT_LANGUAGE: SupportedLanguage = 'en'
export const LANGUAGE_STORAGE_KEY = 'app.locale'

export function isSupportedLanguage(value: string): value is SupportedLanguage {
    return SUPPORTED_LANGUAGES.includes(value as SupportedLanguage)
}
