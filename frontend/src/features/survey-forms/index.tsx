import { ConfigDrawer } from '@/components/config-drawer'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { Search } from '@/components/search'
import { ThemeSwitch } from '@/components/theme-switch'
import { SurveyFormDemo } from './components/survey-form-demo'

export function SurveyForms() {
    return (
        <>
            <Header fixed>
                <Search />
                <div className='ms-auto flex items-center space-x-4'>
                    <ThemeSwitch />
                    <ConfigDrawer />
                    <ProfileDropdown />
                </div>
            </Header>

            <Main className='flex flex-1 flex-col gap-4 sm:gap-6 md:p-8 lg:p-12'>
                <div className='flex flex-wrap items-end justify-between gap-2'>
                    <div>
                        <h2 className='text-2xl font-bold tracking-tight'>Survey Form</h2>
                        <p className='text-muted-foreground'>
                            A comprehensive survey form example using consistent UI components.
                        </p>
                    </div>
                </div>

                <div className='mx-auto w-full max-w-3xl'>
                    <SurveyFormDemo />
                </div>
            </Main>
        </>
    )
}
