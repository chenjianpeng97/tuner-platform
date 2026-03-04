import { UsersActionDialog } from './users-action-dialog'
import { useUsers } from './users-provider'

export function UsersDialogs() {
  const { open, setOpen, currentRow, setCurrentRow } = useUsers()
  return (
    <>
      <UsersActionDialog
        key='user-add'
        open={open === 'add'}
        onOpenChange={(state) => setOpen(state ? 'add' : null)}
      />

      {currentRow && (
        <UsersActionDialog
          key={`user-edit-${currentRow.id}`}
          open={open === 'edit'}
          onOpenChange={(state) => {
            setOpen(state ? 'edit' : null)
            if (!state) {
              setTimeout(() => {
                setCurrentRow(null)
              }, 300)
            }
          }}
          currentRow={currentRow}
        />
      )}
    </>
  )
}
