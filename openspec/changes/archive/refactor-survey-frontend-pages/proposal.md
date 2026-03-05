## Why

Survey 的 Templates 与 Assignments 页面在信息架构和列表交互上与现有 Users 页面不一致，导致学习成本和操作路径不统一。现在需要统一到同一前端交互基线，并同步修复 `features/ui_steps` 以确保行为测试可通过。

## What Changes

- 将 Templates 与 Assignments 页面在侧边栏注册到 Survey 模块 `items` 下，交互形态与当前 “Secured by Clerk” 分组一致（可展开/折叠）。
- 将 templates 与 assignments 列表改造成与 Users 列表一致的结构与交互：Filter 与筛选组件、左侧多选表格选择列、`Actions` 的 `...` 下拉菜单、分页器。
- 对齐上述页面所使用的前端组件使用规则，优先复用 Users 页面已采用的通用组件与模式。
- 重构 `features/ui_steps` 下相关步骤定义，使前两项完成后 UI 场景恢复通过。

## Capabilities

### New Capabilities
- _None._

### Modified Capabilities
- `survey-template-management`: 更新模板列表页的信息架构与列表交互需求，使其与 Users 列表交互基线一致。
- `survey-assignment-management`: 更新任务分配列表页与导航注册需求，并要求对应 UI 行为步骤可通过。

## Impact

- Affected frontend routes and navigation composition under `frontend/src/routes` and related layout/navigation components.
- Affected survey feature list UIs under `frontend/src/features` and shared table/filter/action/pagination components in `frontend/src/components`.
- Affected UI BDD steps under `features/ui_steps` and possibly related `.feature` files if step contracts need alignment.
- No backend API contract changes are expected.