## ADDED Requirements

### Requirement: Survey 模块导航包含模板入口
系统 SHALL 在 Survey 侧边栏分组的 `items` 中注册 Templates 页面入口，并提供可展开/折叠的分组导航交互。

#### Scenario: 展开 Survey 分组后可见模板入口
- **WHEN** 用户在侧边栏展开 Survey 分组
- **THEN** 用户可以看到 Templates 入口并可点击进入模板页面

### Requirement: 模板列表交互与 Users 列表一致
系统 SHALL 使模板列表页遵循 Users 列表的组件与交互规则，至少包含筛选组件、表格左侧多选列、`Actions` 三点菜单和分页器。

#### Scenario: 模板列表显示一致性控件
- **WHEN** 用户进入模板列表页面
- **THEN** 页面显示筛选区、可多选表格行、`Actions` 菜单和分页控件

#### Scenario: 用户执行批量选择并打开 Actions
- **WHEN** 用户在模板列表勾选一条或多条记录并点击 `Actions` 三点菜单
- **THEN** 系统展示与 Users 列表一致的动作菜单触发方式与交互反馈
