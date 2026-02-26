# Frontend 重构与 Orval+MSW 验证计划（Template 归档 + Users/Account 实战）

## Summary
目标是把当前“展示模板前端”拆分成两层：

1. `Template` 层：保留现有页面与样式，作为演示参考，不承担真实业务契约。  
2. `Business` 层：基于 `docs/api_doc.json` 接入真实 `users + account` 接口，使用 `Orval + MSW` 验证 SDD workflow（接口文档 -> 前端业务代码 -> mock -> UI 验证）可行性。

已确认决策：
- 侧边栏新增 `Template` 分组，并把展示代码归档到 template 语义目录。
- `users` 本轮做全量接口。
- `account` 本轮同步真实化（username + 真实接口）。

## Public APIs / Interfaces / Types 变更
1. OpenAPI 输入源固定为 `docs/api_doc.json`。  
2. 新增前端 API 层：
   - `src/api/generated/*`（Orval 生成）
   - `src/api/http-client.ts`（axios 实例、baseURL、withCredentials）
   - `src/api/business/*`（对生成代码做业务封装）
3. 新增 Mock 层：
   - `src/mocks/browser.ts`
   - `src/mocks/handlers.ts`（聚合 Orval 生成 handlers + 自定义场景 handlers）
4. 环境变量：
   - `VITE_API_BASE_URL`
   - `VITE_ENABLE_MSW`
5. Users 领域类型以 OpenAPI 为准（替换当前 demo 用户结构）：
   - `UserQueryModel { id_, username, role, is_active }`
   - role 枚举：`super_admin | admin | user`
6. Account 表单契约改为后端字段：
   - signup/login: `username`, `password`
   - change password: `current_password`, `new_password`

## 实施分期

### Phase 0 - Workflow 对齐
1. 更新 `docs/SDD_workflow.md`：
   - 第 6 步主产物改为 `docs/api_doc.json`（可选再导出 markdown 文档）。
   - 第 7/8 步明确：由 OpenAPI JSON 生成业务代码与 mock handlers（不是手写 `mock.js`）。
2. 保留并使用根目录 `make backend-dev-doc` 作为文档导出入口（已可用）。

### Phase 1 - 信息架构重排（Template vs Business）
1. 侧边栏重组：
   - `Business`：`Users`、`Account`（登录/注册/改密相关入口）
   - `Template`：Dashboard/Tasks/Apps/Chats/Settings/Errors/Clerk 等展示页
2. 代码目录重排（仅语义迁移，不改视觉）：
   - 展示型 feature 迁至 `src/features/template/*`
   - `src/features/users` 与 `src/features/auth` 作为业务实现区继续保留/重建
3. 路由策略：
   - 首轮保持现有 URL 不变
   - 通过菜单分组与目录语义完成“展示/业务”解耦

### Phase 2 - 引入 Orval + MSW 基础设施
1. 新增依赖与脚本：
   - `orval`, `msw`
   - 脚本：`api:generate`, `mock:start`（或集成 `dev`）
2. Orval 配置：
   - input: `../docs/api_doc.json`
   - output: `src/api/generated`
   - 按 tags 拆分（Account / Users）
   - mutator 指向 `src/api/http-client.ts`
3. MSW 集成：
   - 在 `main.tsx` 按 `VITE_ENABLE_MSW` 动态注册 worker
   - handlers 以 Orval 生成结果为主，自定义补充认证/错误场景

### Phase 3 - Users 全量业务接入（验证主样例）
1. 用生成客户端替换 `features/users/data/users.ts` 假数据依赖。
2. 覆盖接口：
   - `GET /api/v1/users/`
   - `POST /api/v1/users/`
   - `PUT /api/v1/users/{user_id}/password`
   - `PUT/DELETE /api/v1/users/{user_id}/roles/admin`
   - `PUT/DELETE /api/v1/users/{user_id}/activation`
3. 表格列与筛选改造：
   - 改为 `id_ / username / role / is_active`
   - demo 字段移出业务主模型
4. 参数映射：
   - UI 分页排序 -> `limit/offset/sorting_field/sorting_order`
5. 错误处理：
   - 401/403/409/422 统一 toast + 页面态反馈

### Phase 4 - Account 真实化
1. 接入接口：
   - `/api/v1/account/signup`
   - `/api/v1/account/login`
   - `/api/v1/account/logout`
   - `/api/v1/account/password`
2. 登录/注册表单改为 `username` 口径。
3. 状态策略（无 `/me` 前提）：
   - 登录成功后更新本地 auth 状态
   - 401 统一回退登录页
   - 废弃现有 mock token 逻辑

### Phase 5 - UI Stage 验证与集成验证
1. Mock 模式：`VITE_ENABLE_MSW=true` 跑 users/account 关键路径。  
2. 联调模式：`VITE_ENABLE_MSW=false` + 后端运行，复跑同一批场景。  
3. 验证 SDD workflow 闭环：接口文档变更 -> 重新生成 -> UI 同步更新 -> 测试通过。

## 测试用例与场景
1. Codegen 稳定性：`api_doc.json` 不变时重复生成无差异。  
2. Users：列表分页排序、创建、激活/停用、提升/撤销 admin、设密成功/失败分支。  
3. Account：signup/login/logout/change-password 成功与错误分支。  
4. 双模式一致性：MSW 与真实后端行为一致。  
5. 回归：Template 分组页面可访问，样式不回退。

## Assumptions / Defaults
1. `docs/api_doc.json` 是前端唯一契约源。  
2. 模板页仅做视觉与交互参考，不业务化。  
3. Users 以后端字段为准，不保留 demo 扩展字段作为主模型。  
4. Account 使用 username 契约，现有 email mock 登录为废弃路径。  
5. 后端未提供 `/me` 时，采用“登录结果 + 401 回退”维持会话体验。
