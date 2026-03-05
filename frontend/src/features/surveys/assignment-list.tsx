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
import { useQuery } from '@tanstack/react-query'
import { Link } from '@tanstack/react-router'
import { useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Plus } from 'lucide-react'
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
import {
    Checkbox,
} from '@/components/ui/checkbox'
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
import { listSurveyAssignments, type SurveyAssignmentListItemQM } from '@/api/surveys'

function formatDate(value: string | null | undefined): string {
    if (!value) return '—'
    return new Date(value).toLocaleDateString()
}

type SurveyAssignmentRow = {
    id: string
    templateVersionId: string
    statusLabel: 'in_progress' | 'completed'
    progress: string
    dueAtLabel: string
}

type AssignmentRowActionsProps = {
    row: Row<SurveyAssignmentRow>
}

function AssignmentRowActions({ row }: AssignmentRowActionsProps) {
    const { t } = useTranslation(['business', 'common'])

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
                        to='/surveys/assignments/$assignmentId'
                        params={{ assignmentId: row.original.id }}
                    >
                        {t('surveys.assignments.actions.details')}
                    </Link>
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    )
}

export function SurveyAssignmentList() {
    const { t } = useTranslation(['business', 'common'])
    const [rowSelection, setRowSelection] = useState({})
    const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})
    const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
    const [pagination, setPagination] = useState<PaginationState>({
        pageIndex: 0,
        pageSize: 10,
    })

    const { data: assignments = [], isLoading } = useQuery<SurveyAssignmentListItemQM[]>({
        queryKey: ['surveys', 'assignments'],
        queryFn: listSurveyAssignments,
    })

    const rows = useMemo<SurveyAssignmentRow[]>(
        () =>
            assignments.map((item) => ({
                id: item.id_,
                templateVersionId: item.template_version_id,
                statusLabel: item.status,
                progress: `${item.submitted_count}/${item.assignee_count} (${Math.round(
                    (item.ratio ?? 0) * 100
                )}%)`,
                dueAtLabel: formatDate(item.due_at),
            })),
        [assignments]
    )

    const columns = useMemo<ColumnDef<SurveyAssignmentRow>[]>(
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
                        aria-label={t('common:selection.selectAll')}
                        className='translate-y-[2px]'
                    />
                ),
                cell: ({ row }) => (
                    <Checkbox
                        checked={row.getIsSelected()}
                        onCheckedChange={(value) => row.toggleSelected(!!value)}
                        aria-label={t('common:selection.selectRow')}
                        className='translate-y-[2px]'
                    />
                ),
                enableSorting: false,
                enableHiding: false,
            },
            {
                accessorKey: 'id',
                header: ({ column }) => (
                    <DataTableColumnHeader column={column} title={t('surveys.assignments.columns.id')} />
                ),
                cell: ({ row }) => (
                    <LongText className='max-w-32 font-mono text-xs'>
                        {String(row.getValue('id')).slice(0, 8)}
                    </LongText>
                ),
                enableHiding: false,
            },
            {
                accessorKey: 'statusLabel',
                header: ({ column }) => (
                    <DataTableColumnHeader column={column} title={t('surveys.assignments.columns.status')} />
                ),
                cell: ({ row }) => {
                    const status = row.getValue('statusLabel') as SurveyAssignmentRow['statusLabel']
                    return (
                        <Badge variant={status === 'completed' ? 'default' : 'secondary'}>
                            {status === 'in_progress'
                                ? t('surveys.assignments.status.inProgress')
                                : t('surveys.assignments.status.completed')}
                        </Badge>
                    )
                },
                filterFn: (row, id, value) => value.includes(row.getValue(id)),
                enableSorting: false,
            },
            {
                accessorKey: 'progress',
                header: ({ column }) => (
                    <DataTableColumnHeader column={column} title={t('surveys.assignments.columns.progress')} />
                ),
                cell: ({ row }) => <span>{row.getValue('progress')}</span>,
            },
            {
                accessorKey: 'dueAtLabel',
                header: ({ column }) => (
                    <DataTableColumnHeader column={column} title={t('surveys.assignments.columns.dueDate')} />
                ),
                cell: ({ row }) => (
                    <span className='text-sm text-muted-foreground'>
                        {row.getValue('dueAtLabel')}
                    </span>
                ),
            },
            {
                id: 'actions',
                header: ({ column }) => (
                    <DataTableColumnHeader column={column} title={t('surveys.assignments.columns.actions')} />
                ),
                cell: ({ row }) => <AssignmentRowActions row={row} />,
                enableSorting: false,
                enableHiding: false,
            },
        ],
        [t]
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
                        <h2 className='text-2xl font-bold tracking-tight'>{t('surveys.assignments.title')}</h2>
                        <p className='text-muted-foreground'>{t('surveys.assignments.description')}</p>
                    </div>
                    <Button asChild>
                        <Link to='/surveys/assignments/new'>
                            <Plus className='mr-2 h-4 w-4' />
                            {t('surveys.assignments.new')}
                        </Link>
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
                        searchPlaceholder={t('surveys.assignments.filterPlaceholder')}
                        searchKey='id'
                        filters={[
                            {
                                columnId: 'statusLabel',
                                title: t('surveys.assignments.columns.status'),
                                options: [
                                    { label: t('surveys.assignments.status.inProgress'), value: 'in_progress' },
                                    { label: t('surveys.assignments.status.completed'), value: 'completed' },
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
                                            {isLoading ? t('surveys.assignments.loading') : t('surveys.assignments.noResults')}
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
