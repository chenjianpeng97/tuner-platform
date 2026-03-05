import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import {
    DEFAULT_LANGUAGE,
    isSupportedLanguage,
    LANGUAGE_STORAGE_KEY,
} from './constants'
import commonEn from './resources/en/common'
import businessEn from './resources/en/business'
import commonZh from './resources/zh/common'
import businessZh from './resources/zh/business'

const persistedLanguage = localStorage.getItem(LANGUAGE_STORAGE_KEY)
const initialLanguage =
    persistedLanguage && isSupportedLanguage(persistedLanguage)
        ? persistedLanguage
        : DEFAULT_LANGUAGE

void i18n.use(initReactI18next).init({
    resources: {
        en: {
            common: commonEn,
            business: businessEn,
        },
        zh: {
            common: commonZh,
            business: businessZh,
        },
    },
    lng: initialLanguage,
    fallbackLng: DEFAULT_LANGUAGE,
    supportedLngs: ['en', 'zh'],
    ns: ['common', 'business'],
    defaultNS: 'common',
    interpolation: {
        escapeValue: false,
    },
})

i18n.on('languageChanged', (language) => {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, language)
})

export default i18n
