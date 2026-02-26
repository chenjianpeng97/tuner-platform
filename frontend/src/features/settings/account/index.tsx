import { ContentSection } from '../components/content-section'
import { AccountForm } from './account-form'

export function SettingsAccount() {
  return (
    <ContentSection
      title='Account'
      desc='Manage account security with contract-driven password update.'
    >
      <AccountForm />
    </ContentSection>
  )
}
