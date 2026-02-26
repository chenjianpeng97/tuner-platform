## ADDED Requirements

### Requirement: Users 管理页面 SHALL 使用已导出的 users 契约接口
前端 users 管理实现 SHALL 调用当前已导出的 users 接口，而不是本地 demo 数据集。

#### Scenario: Users 列表使用后端契约参数
- **WHEN** users 页面请求列表数据
- **THEN** 调用 `docs/api_doc.json` 定义的 users 列表接口
- **THEN** 请求参数遵循已导出契约中的分页与排序字段

#### Scenario: Users 写操作使用导出契约动作
- **WHEN** users 管理触发创建、激活、停用、授予/撤销管理员或重置密码
- **THEN** 前端调用对应已导出的 users 接口
- **THEN** 成功与错误路径通过 API 响应处理，而非本地假 mutation

### Requirement: Users 筛选范围 SHALL 受当前导出契约边界约束
本次迭代 SHALL 不引入超出当前导出契约之外的 users 额外筛选要求。

#### Scenario: 延后未来筛选扩展
- **WHEN** 干系方提出当前契约未包含的 users 额外筛选组合
- **THEN** 这些筛选被记录为后续增强项
- **THEN** 当前迭代实现保持在已导出契约边界内

### Requirement: Account 流程 SHALL 对齐 username 契约字段
前端 account 流程 SHALL 使用已导出的 account 接口，并采用 username 凭证字段。

#### Scenario: 登录与注册契约对齐
- **WHEN** 用户提交 account 注册或登录表单
- **THEN** 请求使用导出 account 契约定义的 `username` 与 `password` 字段
- **THEN** 前端不再依赖历史 email-only mock 登录行为

#### Scenario: 登出与改密契约对齐
- **WHEN** 用户触发登出或修改密码
- **THEN** 前端调用已导出的 account 登出与改密接口
- **THEN** 响应按契约驱动的 API 结果处理

### Requirement: Account 状态 SHALL 支持 `/account/me` 之前的过渡策略
在后端提供 `GET /api/v1/account/me` 之前，前端 SHALL 使用最小代价的过渡方案，保障业务流程可用并可平滑迁移到 `/account/me`。

#### Scenario: 无 `/account/me` 时的过渡用户态
- **WHEN** 当前后端契约尚未提供 `/api/v1/account/me`
- **THEN** 前端可使用保障 UI 连续性的最小固定 fallback 返回值
- **THEN** fallback 行为被隔离封装，可在不重构页面流程的前提下替换为 `/account/me`
