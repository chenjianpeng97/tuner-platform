## Why

当前前端项目主要是展示模板，页面与数据结构大量依赖本地假数据，和后端 `docs/api_doc.json` 的真实契约不一致，导致无法稳定验证 SDD 工作流中“接口文档 -> 前端业务代码 -> mock -> UI 测试”的闭环。现在后端已具备 `account` 与 `users` 的接口能力，需要尽快把前端重构为“模板展示层 + 业务实现层”并引入可持续的代码生成与 mock 机制。

## What Changes

- 将现有展示页面归档为 `Template` 语义分组，保留样式参考价值，但与业务实现解耦。
- 在前端架构中引入 `Orval + MSW`，以 `docs/api_doc.json` 作为唯一契约源，生成 TypeScript API 客户端与 mock handlers。
- 建立统一 API 访问层与 mock 启停机制（基于环境变量），支持 mock 模式与联调模式切换。
- 将 `users` 页面改造为对接真实后端接口（含全量 users 管理相关接口），替换 demo 用户模型与静态数据。
- 将 `account` 相关页面改造为真实接口流程（signup/login/logout/password），并统一为 `username` 契约。
- 调整 `docs/SDD_workflow.md` 的前端实现步骤描述，使其与 OpenAPI JSON 驱动生成的实际流程一致。

## Capabilities

### New Capabilities
- `frontend-openapi-codegen`: 基于 OpenAPI 文档自动生成前端 API 客户端代码与调用入口。
- `frontend-msw-mock-runtime`: 提供可切换的前端运行时 mock 能力，并复用 OpenAPI 生成的 handlers。
- `frontend-template-business-separation`: 将展示模板页面与真实业务页面进行信息架构与目录结构分层。
- `frontend-users-account-api-integration`: 完成 users 与 account 两个业务域的真实接口接入与页面行为改造。

### Modified Capabilities
- None.

## Impact

- Affected code:
  - `frontend/src/components/layout/data/sidebar-data.ts` 及相关导航/路由组织
  - `frontend/src/features/users/**`, `frontend/src/features/auth/**`
  - 新增 `frontend/src/api/**`, `frontend/src/mocks/**` 等基础设施目录
  - `frontend/package.json` 脚本与依赖配置
  - `docs/SDD_workflow.md` 工作流描述
- APIs:
  - 前端对接 `docs/api_doc.json` 中的 `account` 与 `users` 接口契约
- Dependencies:
  - 引入 `orval`, `msw` 及其运行/生成配置
- Systems:
  - 前端开发与测试流程从“手写假数据”转向“OpenAPI 驱动的生成与 mock 联动”
