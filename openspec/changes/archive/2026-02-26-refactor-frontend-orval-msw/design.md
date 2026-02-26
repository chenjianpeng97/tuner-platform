## Context

当前 `frontend` 是展示型项目，导航、页面与数据模型主要围绕 demo 数据组织，尚未形成以后端契约驱动的业务实现路径。后端已提供 `docs/api_doc.json`（覆盖 `account` 与 `users`），且根目录已有 `make backend-dev-doc` 可导出 OpenAPI 文档。

现状约束与边界：
- 前端技术栈为 Vite + React + TanStack Router + React Query + Zustand。
- 路由采用文件路由与自动生成 `routeTree.gen.ts`，应避免手工维护路由树。
- 当前 users 页面字段与后端 `UserQueryModel` 不一致，account 登录流仍是本地 mock。
- 目标不是重做 UI，而是在保留模板价值的同时建立业务实现主干。

相关干系方：
- 前端开发：需要可重复的接口生成与 mock 机制。
- 后端开发：需要前端可快速跟随 OpenAPI 变化验证契约。
- 测试/流程：需要支撑 SDD workflow 的“文档驱动前端实现”闭环。

## Goals / Non-Goals

**Goals:**
- 建立“`docs/api_doc.json` -> Orval 生成 -> 业务调用 -> MSW mock -> UI 验证”的标准链路。
- 将前端信息架构分为 `Template`（展示参考）与 `Business`（真实接口实现）两层。
- 完成 `users` 全量接口与 `account`（signup/login/logout/password）真实接入。
- 让前端在 mock 模式和联调模式都能运行同一套页面逻辑。
- 使 `docs/SDD_workflow.md` 与实际工程流程一致。

**Non-Goals:**
- 不在本变更中重做整套视觉设计或组件库。
- 不在本变更中实现后端新接口（如 `/me`）。
- 不将全部 template 页面业务化，仅迁移与归档其语义位置。
- 不在本变更中引入新的前端测试框架（仅适配现有流程）。

## Decisions

### Decision 1: OpenAPI JSON 作为前端唯一契约源
- 决策：统一使用 `docs/api_doc.json` 作为代码生成输入，前端不直接依赖在线 Swagger 地址生成。
- 原因：可版本化、可审计、可在 CI/离线环境重复生成，且与 SDD 文档流程一致。
- 备选方案：
  - 直接请求运行中后端 `/openapi.json` 生成：环境依赖高、构建不稳定、难复现。

### Decision 2: 使用 Orval 生成客户端与 MSW handlers
- 决策：引入 Orval（按 tags 拆分）并生成 API 调用代码与 mock handlers；通过自定义 mutator 统一请求行为。
- 原因：一套配置同时覆盖类型、请求函数和 mock handlers，降低手写维护成本。
- 备选方案：
  - OpenAPI Generator + 手写 MSW：可行但模板重、mock 与客户端分离，维护成本更高。
  - 仅生成 types：无法满足“快速生成业务代码+mock”的流程目标。

### Decision 3: API 目录按后端模块对齐，隔离生成代码与手写集成代码
- 决策：
  - `src/api/generated/*` 只存放生成产物（禁止手改）。
  - `src/api/http-client.ts` 统一 axios/baseURL/withCredentials/错误拦截。
  - 手写 API 适配代码按后端模块划分在 `src/api/account/*`、`src/api/users/*` 等目录。
- 原因：在避免页面直接依赖生成细节的同时，与后端模块命名保持一致，降低理解与维护成本。
- 备选方案：
  - 页面直接调用 generated 方法：短期快，但后期变更扩散严重。

### Decision 4: Template/Business 语义分层采用“先稳 URL，再调整目录”
- 决策：首轮保持现有 URL 兼容，仅重组侧边栏分组并将展示页迁移到 `features/template/*` 语义目录。
- 原因：降低路由回归风险，优先完成业务契约打通。
- 备选方案：
  - 一次性改到 `/template/*` 路由前缀：语义更纯，但迁移与回归成本更高，推迟到后续迭代。

### Decision 5: users 页面模型向后端契约收敛，不做“伪兼容扩展字段”
- 决策：users 页面主模型使用 `UserQueryModel`（`id_`, `username`, `role`, `is_active`）及后端分页排序参数（`limit/offset/sorting_field/sorting_order`）。
- 原因：避免继续绑定 demo 字段（如 firstName/email/phone），减少双模型维护。
- 备选方案：
  - 维持旧 UI 字段并做前端拼装：会引入大量推断逻辑，增加错误面。

### Decision 6: account 全链路改为 username 契约，认证状态采用“请求结果+401回退”
- 决策：登录注册表单与后端保持 `username/password`；在无 `/me` 接口前，以登录结果与接口 401 响应维护会话状态。
- 原因：优先保证契约一致性与可交付性，不阻塞 users/account 打通。
- 备选方案：
  - 保留 email UI 并做映射：存在契约偏差，易引发认知混乱。
  - 等待 `/me` 再改：会拖延主流程验证。

## Risks / Trade-offs

- [生成代码更新引发大面积 diff] -> 将 generated 目录与手写目录严格隔离；在脚本中固定输出路径和分组策略。
- [mock 与真实后端行为不一致] -> 以生成 handlers 为主，关键流程同时跑 mock 模式与联调模式。
- [users 旧 UI 字段缺失导致交互退化] -> 明确本期以契约字段为主，必要展示信息采用占位文案而非伪造字段。
- [account 无 `/me` 导致刷新后状态不完整] -> 用 401 回退与显式登录入口兜底，后续迭代补 `/me` 再增强。
- [目录迁移影响导入路径与路由文件] -> 分批迁移并在每批后执行类型检查与路由生成校验。

## Migration Plan

1. **基础设施落地**
   - 新增 Orval 配置、MSW 启动逻辑、API 分层目录与 npm scripts。
   - 验证 `api_doc.json` 可生成客户端与 handlers。
2. **信息架构迁移**
   - 重组侧边栏为 `Business` + `Template`。
   - 将展示页移动到 `features/template/*`（保留现有 URL）。
3. **users 业务改造**
   - 用 generated + `api/users` 模块替换静态 users 数据与操作。
   - 对齐筛选、分页、排序、错误处理。
4. **account 业务改造**
   - 替换 sign-in/sign-up/logout/password 为真实接口调用。
   - 统一 username 字段与会话错误处理。
5. **流程文档对齐**
   - 更新 `docs/SDD_workflow.md` 的前端实现步骤描述。
6. **验收**
   - 分别在 `VITE_ENABLE_MSW=true/false` 下验证 users/account 关键路径。

回滚策略：
- 代码层面按阶段提交，若某阶段不稳定可回滚该阶段提交而保留之前稳定阶段。
- 运行层面可临时关闭 MSW（`VITE_ENABLE_MSW=false`）继续联调。

## Open Questions

- 后端是否会补充 `GET /api/v1/account/me`（或等价会话查询）以完善刷新后的用户信息恢复？
- `users` 列表是否需要后端支持更多筛选条件（当前契约主要是分页与排序）？
- UI stage 自动化是否需要统一约定“mock 基线场景数据集”以减少场景漂移？
