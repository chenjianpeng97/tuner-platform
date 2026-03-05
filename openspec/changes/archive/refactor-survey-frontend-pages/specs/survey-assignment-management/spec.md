## ADDED Requirements

### Requirement: Survey 模块导航包含任务入口
系统 SHALL 在 Survey 侧边栏分组的 `items` 中注册 Assignments 页面入口，并与分组展开/折叠交互保持一致。

#### Scenario: 展开 Survey 分组后可见任务入口
- **WHEN** 用户在侧边栏展开 Survey 分组
- **THEN** 用户可以看到 Assignments 入口并可点击进入任务列表页面

### Requirement: 任务列表交互与 Users 列表一致
系统 SHALL 使任务列表页遵循 Users 列表的组件与交互规则，至少包含筛选组件、表格左侧多选列、`Actions` 三点菜单和分页器。

#### Scenario: 任务列表显示一致性控件
- **WHEN** 用户进入任务列表页面
- **THEN** 页面显示筛选区、可多选表格行、`Actions` 菜单和分页控件

#### Scenario: 用户执行筛选后保持分页与选择语义
- **WHEN** 用户应用筛选条件并进行行选择与分页切换
- **THEN** 系统在筛选结果内维持一致的选择与分页交互语义

### Requirement: Survey UI 步骤在重构后可通过
系统 SHALL 在导航与列表交互重构后，保持 `features/ui_steps` 中 survey 相关步骤与页面行为一致并可通过执行。

#### Scenario: Survey assignment UI 场景通过
- **WHEN** 运行 survey assignment 相关 UI 场景
- **THEN** 相关步骤执行成功且不因导航层级或列表组件重构而失败
