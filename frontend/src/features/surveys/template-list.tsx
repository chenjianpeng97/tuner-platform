import { DotsHorizontalIcon } from '@radix-ui/react-icons'
import {
    type ColumnFiltersState,
    type ColumnDef,
    type PaginationState,
    type Row,
    type VisibilityState,
    flexRender,
    getCoreRowModel,
    getFacetedRowModel,
    getFacetedUniqueValues,
    getFilteredRowModel,
    getPaginationRowModel,
    useReactTable,
} from '@tanstack/react-table'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from '@tanstack/react-router'
import { useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus } from 'lucide-react'
import { toast } from 'sonner'
import { ConfigDrawer } from '@/components/config-drawer'
import {
    DataTableColumnHeader,
    DataTablePagination,
    DataTableToolbar,
} from '@/components/data-table'
import { Header } from '@/components/layout/header'
import { Main } from '@/components/layout/main'
import { LongText } from '@/components/long-text'
import { ProfileDropdown } from '@/components/profile-dropdown'
import { Search } from '@/components/search'
import { ThemeSwitch } from '@/components/theme-switch'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table'
import { cn } from '@/lib/utils'
import {
    createSurveyTemplate,
    listSurveyTemplates,
    publishSurveyTemplate,
    type SurveyTemplateListItemQM,
} from '@/api/surveys'

type SurveyTemplateRow = {
    id: string
    name: string
    statusLabel: 'draft' | 'published'
    version: string
}

type TemplateRowActionsProps = {
    row: Row<SurveyTemplateRow>
    onPublish: (templateId: string) => void
    publishing: boolean
}

function TemplateRowActions({
    row,
    onPublish,
    publishing,
}: TemplateRowActionsProps) {
    const { t } = useTranslation(['business', 'common'])
    const isDraft = row.original.statusLabel === 'draft'

    return (
        <DropdownMenu modal={false}>
            <DropdownMenuTrigger asChild>
                <Button
                    variant='ghost'
                    className='flex h-8 w-8 p-0 data-[state=open]:bg-muted'
                >
                    <DotsHorizontalIcon className='h-4 w-4' />
                    <span className='sr-only'>{t('common:menu.openActionsMenu')}</span>
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align='end' className='w-[160px]'>
                <DropdownMenuItem asChild>
                    <Link
                        to='/surveys/templates/$templateId/edit'
                        params={{ templateId: row.original.id }}
                    >
                        {t('surveys.templates.actions.edit')}
                    </Link>
                </DropdownMenuItem>
                <DropdownMenuItem
                    disabled={!isDraft || publishing}
                    onClick={() => onPublish(row.original.id)}
                >
                    {t('surveys.templates.actions.publish')}
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}

export function SurveyTemplateList() {
    const { t } = useTranslation(['business', 'common'])
    const queryClient = useQueryClient()
    const [rowSelection, setRowSelection] = useState({})
    const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
    const [pagination, setPagination] = useState<PaginationState>({
        pageIndex: 0,
        pageSize: 10,
    })

    const { data: templates = [], isLoading } = useQuery<SurveyTemplateListItemQM[]>({
        queryKey: ['surveys', 'templates'],
        queryFn: listSurveyTemplates,
    })

    const createMutation = useMutation({
        mutationFn: () =>
            createSurveyTemplate({
                name: t('surveys.templates.new'),
                questions: [],
            }),
        onSuccess: () => {
            toast.success(t('surveys.templates.createSuccess'))
            queryClient.invalidateQueries({ queryKey: ['surveys', 'templates'] })
        },
        onError: () => toast.error(t('surveys.templates.createFailed')),
    })

    const publishMutation = useMutation({
        mutationFn: (templateId: string) => publishSurveyTemplate(templateId),
        onSuccess: () => {
            toast.success(t('surveys.templates.publishSuccess'))
            queryClient.invalidateQueries({ queryKey: ['surveys', 'templates'] })
        },
        onError: () => toast.error(t('surveys.templates.publishFailed')),
    })

    const publishTemplate = publishMutation.mutate
    const isPublishing = publishMutation.isPending

    const rows = useMemo<SurveyTemplateRow[]>(
        () =>
            templates.map((item) => ({
                id: item.id_,
                name: item.name,
                statusLabel: item.latest_published_version_id ? 'published' : 'draft',
                version: item.latest_published_version_id
                    ? item.latest_published_version_id.slice(0, 8)
                    : '—',
            })),
        [templates]
    )

    const columns = useMemo<ColumnDef<SurveyTemplateRow>[]>(
        () => [
            {
                id: 'select',
                header: ({ table }) => (
                    <Checkbox
                        checked={
                            table.getIsAllPageRowsSelected() ||
                            (table.getIsSomePageRowsSelected() && 'indeterminate')
                        }
                        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
                        aria-label='Select all'
                        className='translate-y-[2px]'
                    />
                ),
                cell: ({ row }) => (
                    <Checkbox
                        checked={row.getIsSelected()}
                        onCheckedChange={(value) => row.toggleSelected(!!value)}
                        aria-label='Select row'
                        className='translate-y-[2px]'
                    />
                ),
                enableSorting: false,
                enableHiding: false,
            },
            {
                accessorKey: 'name',
                header: ({ column }) => (
                    <DataTableColumnHeader column={column} title={t('surveys.templates.columns.name')} />
                ),
                cell: ({ row }) => (
                    <LongText className='max-w-72'>{row.getValue('name')}</LongText>
                ),
                enableHiding: false,
            },
            {
                accessorKey: 'statusLabel',
                header: ({ column }) => (
                    <DataTableColumnHeader column={column} title={t('surveys.templates.columns.status')} />
                ),
                cell: ({ row }) => {
                    const status = row.getValue('statusLabel') as SurveyTemplateRow['statusLabel']
                    return (
                        <Badge variant={status === 'draft' ? 'outline' : 'default'}>
                            {status === 'draft'
                                ? t('surveys.templates.status.draft')
                                : t('surveys.templates.status.published')}
                        </Badge>
                    )
                },
                filterFn: (row, id, value) => value.includes(row.getValue(id)),
                enableSorting: false,
            },
            {
                accessorKey: 'version',
                header: ({ column }) => (
                    <DataTableColumnHeader column={column} title={t('surveys.templates.columns.version')} />
                ),
                cell: ({ row }) => (
                    <span className='font-mono text-xs'>{row.getValue('version')}</span>
                ),
            },
            {
                id: 'actions',
                header: ({ column }) => (
                    <DataTableColumnHeader column={column} title={t('surveys.templates.columns.actions')} />
                ),
                cell: ({ row }) => (
                    <TemplateRowActions
                        row={row}
                        onPublish={publishTemplate}
                        publishing={isPublishing}
                    />
                ),
                enableSorting: false,
                enableHiding: false,
            },
        ],
        [isPublishing, publishTemplate, t]
    )

    const table = useReactTable({
        data: rows,
        columns,
        state: {
            rowSelection,
            columnVisibility,
            columnFilters,
            pagination,
        },
        onRowSelectionChange: setRowSelection,
        onColumnVisibilityChange: setColumnVisibility,
        onColumnFiltersChange: setColumnFilters,
        onPaginationChange: setPagination,
        getCoreRowModel: getCoreRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        getFacetedRowModel: getFacetedRowModel(),
        getFacetedUniqueValues: getFacetedUniqueValues(),
        getPaginationRowModel: getPaginationRowModel(),
        enableRowSelection: true,
    })

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

            <Main className='flex flex-1 flex-col gap-4 sm:gap-6'>
                <div className='flex flex-wrap items-end justify-between gap-2'>
                    <div>
                        <h2 className='text-2xl font-bold tracking-tight'>{t('surveys.templates.title')}</h2>
                        <p className='text-muted-foreground'>{t('surveys.templates.description')}</p>
                    </div>
                    <Button
                        onClick={() => createMutation.mutate()}
                        disabled={createMutation.isPending}
                    >
                        <Plus className='mr-2 h-4 w-4' />
                        {t('surveys.templates.new')}
                    </Button>
                </div>

                <div
                    className={cn(
                        'max-sm:has-[div[role="toolbar"]]:mb-16',
                        'flex flex-1 flex-col gap-4'
                    )}
                >
                    <DataTableToolbar
                        table={table}
                        searchPlaceholder={t('surveys.templates.filterPlaceholder')}
                        searchKey='name'
                        filters={[
                            {
                                columnId: 'statusLabel',
                                title: t('surveys.templates.columns.status'),
                                options: [
                                    { label: t('surveys.templates.status.draft'), value: 'draft' },
                                    { label: t('surveys.templates.status.published'), value: 'published' },
                                ],
                            },
                        ]}
                    />

                    <div className='overflow-hidden rounded-md border'>
                        <Table>
                            <TableHeader>
                                {table.getHeaderGroups().map((headerGroup) => (
                                    <TableRow key={headerGroup.id} className='group/row'>
                                        {headerGroup.headers.map((header) => (
                                            <TableHead
                                                key={header.id}
                                                colSpan={header.colSpan}
                                                className={cn(
                                                    'bg-background group-hover/row:bg-muted group-data-[state=selected]/row:bg-muted',
                                                    header.column.columnDef.meta?.className,
                                                    header.column.columnDef.meta?.thClassName
                                                )}
                                            >
                                                {header.isPlaceholder
                                                    ? null
                                                    : flexRender(
                                                        header.column.columnDef.header,
                                                        header.getContext()
                                                    )}
                                            </TableHead>
                                        ))}
                                    </TableRow>
                                ))}
                            </TableHeader>
                            <TableBody>
                                {table.getRowModel().rows.length ? (
                                    table.getRowModel().rows.map((row) => (
                                        <TableRow
                                            key={row.id}
                                            data-state={row.getIsSelected() && 'selected'}
                                            className='group/row'
                                        >
                                            {row.getVisibleCells().map((cell) => (
                                                <TableCell
                                                    key={cell.id}
                                                    className={cn(
                                                        'bg-background group-hover/row:bg-muted group-data-[state=selected]/row:bg-muted',
                                                        cell.column.columnDef.meta?.className,
                                                        cell.column.columnDef.meta?.tdClassName
                                                    )}
                                                >
                                                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                                </TableCell>
                                            ))}
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow>
                                        <TableCell colSpan={columns.length} className='h-24 text-center'>
                                            {isLoading ? t('surveys.templates.loading') : t('surveys.templates.noResults')}
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </div>

                    <DataTablePagination table={table} className='mt-auto' />
                </div>
            </Main>
        </>
    )
}
