import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from '@tanstack/react-router'
import { Plus } from 'lucide-react'
import { toast } from 'sonner'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { ThemeSwitch } from '@/components/theme-switch'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import {
    createSurveyTemplate,
    listSurveyTemplates,
    publishSurveyTemplate,
    type SurveyTemplateListItemQM,
} from '@/api/surveys'

export function SurveyTemplateList() {
    const queryClient = useQueryClient()

    const { data: templates = [], isLoading } = useQuery<SurveyTemplateListItemQM[]>({
        queryKey: ['surveys', 'templates'],
        queryFn: listSurveyTemplates,
    })

    const createMutation = useMutation({
        mutationFn: () =>
            createSurveyTemplate({
                name: 'New Template',
                questions: [],
            }),
        onSuccess: () => {
            toast.success('Template created')
            queryClient.invalidateQueries({ queryKey: ['surveys', 'templates'] })
        },
        onError: () => toast.error('Failed to create template'),
    })

    const publishMutation = useMutation({
        mutationFn: (templateId: string) => publishSurveyTemplate(templateId),
        onSuccess: () => {
            toast.success('Template published')
            queryClient.invalidateQueries({ queryKey: ['surveys', 'templates'] })
        },
        onError: () => toast.error('Failed to publish template'),
    })

    return (
        <>
            <Header>
                <div className='flex items-center gap-2 ml-auto'>
                    <ThemeSwitch />
                    <ProfileDropdown />
                </div>
            </Header>

            <Main>
                <div className='mb-6 flex items-center justify-between'>
                    <div>
                        <h1 className='text-2xl font-bold'>Survey Templates</h1>
                        <p className='text-muted-foreground text-sm'>Manage and publish survey templates</p>
                    </div>
                    <Button onClick={() => createMutation.mutate()} disabled={createMutation.isPending}>
                        <Plus className='mr-2 h-4 w-4' />
                        New Template
                    </Button>
                </div>

                {isLoading ? (
                    <p className='text-muted-foreground text-sm'>Loading...</p>
                ) : templates.length === 0 ? (
                    <p className='text-muted-foreground text-sm'>No templates yet.</p>
                ) : (
                    <div className='rounded-md border'>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Name</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Version</TableHead>
                                    <TableHead className='text-right'>Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {templates.map((tpl) => {
                                    const isDraft = !tpl.latest_published_version_id
                                    return (
                                        <TableRow key={tpl.id_}>
                                            <TableCell className='font-medium'>{tpl.name}</TableCell>
                                            <TableCell>
                                                <Badge variant={isDraft ? 'outline' : 'default'}>
                                                    {isDraft ? 'Draft' : 'Published'}
                                                </Badge>
                                            </TableCell>
                                            <TableCell>
                                                {tpl.latest_published_version_id
                                                    ? tpl.latest_published_version_id.slice(0, 8)
                                                    : '—'}
                                            </TableCell>
                                            <TableCell className='text-right'>
                                                <div className='flex justify-end gap-2'>
                                                    <Button variant='outline' size='sm' asChild>
                                                        <Link to='/surveys/templates/$templateId/edit' params={{ templateId: tpl.id_ }}>
                                                            Edit
                                                        </Link>
                                                    </Button>
                                                    {isDraft && (
                                                        <Button
                                                            size='sm'
                                                            onClick={() => publishMutation.mutate(tpl.id_)}
                                                            disabled={publishMutation.isPending}
                                                        >
                                                            Publish
                                                        </Button>
                                                    )}
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    )
                                })}
                            </TableBody>
                        </Table>
                    </div>
                )}
            </Main>
        </>
    )
}
