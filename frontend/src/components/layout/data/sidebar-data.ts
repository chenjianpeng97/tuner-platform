import {
  ClipboardList,
  Construction,
  LayoutDashboard,
  Monitor,
  Bug,
  ListTodo,
  FileX,
  FileText,
  HelpCircle,
  Lock,
  Bell,
  Package,
  Palette,
  ServerOff,
  Settings,
  Wrench,
  UserCog,
  UserX,
  Users,
  MessagesSquare,
  ShieldCheck,
  AudioWaveform,
  Command,
  GalleryVerticalEnd,
} from 'lucide-react'
import { ClerkLogo } from '@/assets/clerk-logo'
import { type SidebarData } from '../types'

type Translate = (key: string) => string

export function getSidebarData(t: Translate): SidebarData {
  return {
    user: {
      name: 'satnaing',
      email: 'satnaingdev@gmail.com',
      avatar: '/avatars/shadcn.jpg',
    },
    teams: [
      {
        name: 'Shadcn Admin',
        logo: Command,
        plan: 'Vite + ShadcnUI',
      },
      {
        name: 'Acme Inc',
        logo: GalleryVerticalEnd,
        plan: 'Enterprise',
      },
      {
        name: 'Acme Corp.',
        logo: AudioWaveform,
        plan: 'Startup',
      },
    ],
    navGroups: [
      {
        title: t('nav.business'),
        items: [
          {
            title: t('nav.survey'),
            icon: ClipboardList,
            items: [
              {
                title: t('nav.templates'),
                url: '/surveys/templates',
                icon: FileText,
              },
              {
                title: t('nav.assignments'),
                url: '/surveys/assignments',
                icon: ClipboardList,
              },
            ],
          },
          {
            title: t('nav.users'),
            url: '/users',
            icon: Users,
          },
          {
            title: t('nav.account'),
            url: '/settings/account',
            icon: Wrench,
          },
        ],
      },
      {
        title: t('nav.template'),
        items: [
          {
            title: 'Dashboard',
            url: '/',
            icon: LayoutDashboard,
          },
          {
            title: 'Tasks',
            url: '/tasks',
            icon: ListTodo,
          },
          {
            title: 'Apps',
            url: '/apps',
            icon: Package,
          },
          {
            title: 'Chats',
            url: '/chats',
            badge: '3',
            icon: MessagesSquare,
          },
          {
            title: 'Secured by Clerk',
            icon: ClerkLogo,
            items: [
              {
                title: 'Sign In',
                url: '/clerk/sign-in',
              },
              {
                title: 'Sign Up',
                url: '/clerk/sign-up',
              },
              {
                title: 'User Management',
                url: '/clerk/user-management',
              },
            ],
          },
          {
            title: 'Auth',
            icon: ShieldCheck,
            items: [
              {
                title: 'Sign In',
                url: '/sign-in',
              },
              {
                title: 'Sign In (2 Col)',
                url: '/sign-in-2',
              },
              {
                title: 'Sign Up',
                url: '/sign-up',
              },
              {
                title: 'Forgot Password',
                url: '/forgot-password',
              },
              {
                title: 'OTP',
                url: '/otp',
              },
            ],
          },
          {
            title: 'Errors',
            icon: Bug,
            items: [
              {
                title: 'Unauthorized',
                url: '/errors/unauthorized',
                icon: Lock,
              },
              {
                title: 'Forbidden',
                url: '/errors/forbidden',
                icon: UserX,
              },
              {
                title: 'Not Found',
                url: '/errors/not-found',
                icon: FileX,
              },
              {
                title: 'Internal Server Error',
                url: '/errors/internal-server-error',
                icon: ServerOff,
              },
              {
                title: 'Maintenance Error',
                url: '/errors/maintenance-error',
                icon: Construction,
              },
            ],
          },
          {
            title: 'Settings',
            icon: Settings,
            items: [
              {
                title: 'Profile',
                url: '/settings',
                icon: UserCog,
              },
              {
                title: 'Appearance',
                url: '/settings/appearance',
                icon: Palette,
              },
              {
                title: 'Notifications',
                url: '/settings/notifications',
                icon: Bell,
              },
              {
                title: 'Display',
                url: '/settings/display',
                icon: Monitor,
              },
            ],
          },
          {
            title: 'Help Center',
            url: '/help-center',
            icon: HelpCircle,
          },
        ],
      },
    ],
  }
}
