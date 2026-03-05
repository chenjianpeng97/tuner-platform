## ADDED Requirements

### Requirement: 参与人作答访问控制
系统 SHALL 只允许某任务的被分发参与人读取和提交自己的作答内容。

#### Scenario: 参与人读取自己的提交
- **WHEN** 参与人请求自己被分发任务的 `my-submission`
- **THEN** 系统返回该参与人的最新保存/提交快照

#### Scenario: 非参与人读取提交
- **WHEN** 未被分发该任务的用户请求 `my-submission`
- **THEN** 系统以未授权或无权限拒绝请求

### Requirement: 结束前覆盖式重复提交
系统 SHALL 在任务未完成且未过截止时间时允许参与人重复提交，并 SHALL 以最后一次提交作为有效结果。

#### Scenario: 任务结束前重复提交
- **WHEN** 参与人先提交答案 A，后在任务结束前提交答案 B
- **THEN** 系统将答案 B 作为最新有效结果用于结果查询，且该参与人保持已提交状态

#### Scenario: 首次提交更新进度
- **WHEN** 某参与人首次成功提交
- **THEN** 系统将该任务 `submitted_count` 增加 1

### Requirement: 截止后或完成后禁止提交
系统 SHALL 在任务已 `completed` 或当前时间超过配置 `due_at` 时阻止新提交和覆盖提交。

#### Scenario: 手动结束后提交被拒绝
- **WHEN** 参与人在任务状态已是 `completed` 后继续提交
- **THEN** 系统拒绝该提交请求

#### Scenario: 超过截止时间提交被拒绝
- **WHEN** 参与人在配置的 `due_at` 之后提交
- **THEN** 系统拒绝该提交请求

### Requirement: 实名提交绑定
系统 SHALL 将每次提交绑定到已认证参与人身份，且 V1 SHALL 不支持匿名提交模式。

#### Scenario: 提交身份留痕
- **WHEN** 参与人提交作答
- **THEN** 系统记录提交用户身份与提交时间并与作答内容关联
