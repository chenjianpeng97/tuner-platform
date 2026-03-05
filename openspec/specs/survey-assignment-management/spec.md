## ADDED Requirements

### Requirement: 问卷填写任务创建
系统 SHALL 允许有权限用户基于已发布的 `template_version_id` 与非空用户 ID 列表创建问卷填写任务。

#### Scenario: 使用合法参数创建任务
- **WHEN** 有权限用户使用合法已发布模板版本和参与人 ID 列表创建任务
- **THEN** 系统创建状态为 `in_progress` 的问卷填写任务

#### Scenario: 拒绝使用未发布模板创建任务
- **WHEN** 有权限用户使用未发布模板版本创建问卷填写任务
- **THEN** 系统以参数校验错误拒绝请求

### Requirement: 任务截止时间模型
系统 SHALL 支持任务截止时间可选，并根据是否设置截止时间应用不同提交约束。

#### Scenario: 创建无截止时间任务
- **WHEN** 有权限用户创建任务时未提供 `due_at`
- **THEN** 系统接受创建，并保持任务可提交直到自动收集完毕或手动结束

#### Scenario: 创建有截止时间任务
- **WHEN** 有权限用户创建任务时提供 `due_at`
- **THEN** 系统保存截止时间并用于后续提交约束

### Requirement: 任务收集完毕生命周期
系统 SHALL 在所有参与人提交后自动将任务状态置为 `completed`，并 SHALL 支持有权限用户手动提前结束任务。

#### Scenario: 自动收集完毕
- **WHEN** 最后一个尚未提交的参与人成功提交
- **THEN** 系统将任务状态从 `in_progress` 更新为 `completed`

#### Scenario: 管理员手动结束
- **WHEN** 有权限用户对 `in_progress` 任务执行结束操作
- **THEN** 系统将任务状态更新为 `completed` 并停止后续提交

### Requirement: 任务进度统计指标
系统 SHALL 对每个任务提供进度计数，包括 `assignee_count`、`submitted_count`、`ratio`。

#### Scenario: 部分提交进度显示
- **WHEN** 12 名参与人中有 10 名已提交
- **THEN** 系统返回 `assignee_count=12`、`submitted_count=10` 及由两者计算出的比例

#### Scenario: 全量提交进度显示
- **WHEN** 全部参与人都已提交
- **THEN** 系统返回 `submitted_count=assignee_count` 且状态为 `completed`
