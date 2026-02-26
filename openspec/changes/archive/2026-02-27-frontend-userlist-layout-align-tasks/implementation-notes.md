## UserList vs Tasks 布局对齐记录

### 对齐目标
- 参考 `Tasks` 页面的 CRUD 结构分区：标题区 → 操作区 → 数据区。
- 在不改变 `UserList` 数据逻辑与 API 行为前提下完成布局重排。

### 已完成对齐点
- 标题区：`User List` 标题与说明文案保留。
- 主操作区：`Create User` 按钮上移至标题区右侧，与 `Tasks` 页面主操作入口位置一致。
- 操作区：保留创建用户输入区（username/password/role）与排序/分页参数区，作为页面操作区域。
- 数据区：用户表格与分页控制保留，位置处于操作区之后，满足 CRUD 页面信息顺序。

### 行为一致性核对
- 创建用户仍使用原 `onCreateUser` 逻辑与 `createUserMutation`。
- 列表加载、排序、分页、状态/角色操作调用保持不变。
- 已通过 `frontend` 构建校验，未引入编译错误。

### 参考实现
- 参考页面：`frontend/src/features/tasks/index.tsx`
- 调整页面：`frontend/src/features/users/index.tsx`
