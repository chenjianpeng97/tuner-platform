# frontend-msw-mock-runtime Specification

## Purpose
TBD - created by archiving change refactor-frontend-orval-msw. Update Purpose after archive.
## Requirements
### Requirement: 前端 SHALL 支持可切换的 mock 运行模式
前端 SHALL 提供运行时开关，以在不修改页面层业务逻辑的前提下启用或关闭 mock 拦截。

#### Scenario: 运行在 mock 模式
- **WHEN** 通过环境配置启用 mock 运行时
- **THEN** 前端 API 请求被 mock handlers 拦截
- **THEN** 页面可在无需真实后端服务时运行

#### Scenario: 运行在联调模式
- **WHEN** 通过环境配置关闭 mock 运行时
- **THEN** 前端 API 请求发送到配置的后端 base URL
- **THEN** 页面复用同一套逻辑，不在页面组件内加入 mock 专用分支

### Requirement: Mock 样本 SHALL 使用统一基线数据集
项目 SHALL 为 mock 场景定义一套统一共享的基线 fixture 数据集，以确保本地开发与自动化 UI 测试使用一致的样本响应。

#### Scenario: 在开发与测试中复用基线样本
- **WHEN** mock handlers 返回 account 与 users 响应
- **THEN** handlers 从共享 fixture 文件读取数据，而非临时内联对象
- **THEN** UI 测试与本地 mock 模式引用同一份基线 fixture 数据

#### Scenario: 维护 fixture 与契约一致性
- **WHEN** 新增或更新 fixture payload
- **THEN** fixture 结构与当前前端业务路径使用的 OpenAPI 响应形状保持一致
- **THEN** fixture 变更以仓库文件形式进行版本化管理

