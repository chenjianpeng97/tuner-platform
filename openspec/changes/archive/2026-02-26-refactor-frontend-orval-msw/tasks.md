## 1. 契约与基础设施准备

- [x] 1.1 在 `frontend` 引入 `orval` 与 `msw` 依赖，并补充 `api:generate` 等脚本
- [x] 1.2 新建 Orval 配置，输入固定为 `docs/api_doc.json`，输出到 `src/api/generated/*`
- [x] 1.3 建立 `src/api/http-client.ts` 与 `src/api/account/*`、`src/api/users/*` 模块边界，约束 generated 代码禁止手改

## 2. Mock 运行时与基线样本

- [x] 2.1 新建 `src/mocks/browser.ts` 与 handlers 聚合入口，支持通过环境变量启停 mock
- [x] 2.2 建立统一 mock 基线样本目录（JSON fixtures），覆盖 account/users 常见成功与错误场景
- [x] 2.3 将 MSW handlers 改为读取共享 fixtures，避免临时内联对象
- [x] 2.4 校验 mock fixtures 与当前 OpenAPI 响应结构一致

## 3. Template/Business 信息架构重组

- [x] 3.1 调整侧边栏分组为 `Business` 与 `Template`，保证导航语义清晰
- [x] 3.2 将展示型页面代码迁移到 `features/template/*` 语义目录
- [x] 3.3 保持首轮 URL 不变并验证原模板页面可访问

## 4. Users 真实接口接入

- [x] 4.1 用 generated + `src/api/users/*` 替换 users 静态数据源
- [x] 4.2 接入 users 全量操作接口（列表、创建、激活/停用、授权/撤销 admin、设密）
- [x] 4.3 将 users 页面模型收敛到当前契约字段（`id_`, `username`, `role`, `is_active`）
- [x] 4.4 将分页排序参数映射到当前导出契约（`limit/offset/sorting_field/sorting_order`）
- [x] 4.5 明确记录并执行“本迭代不扩展额外筛选条件”的边界

## 5. Account 真实流程接入

- [x] 5.1 将登录/注册字段切换为 `username/password`，移除 email-only mock 登录路径
- [x] 5.2 接入 account 接口（signup/login/logout/password）并统一错误处理
- [x] 5.3 在 `/account/me` 尚未可用时实现最小代价 fallback 用户态（固定返回值策略）
- [x] 5.4 隔离 fallback 逻辑，确保后续可无痛替换为 `GET /api/v1/account/me`

## 6. 工作流与验收

- [x] 6.1 更新 `docs/SDD_workflow.md`，对齐 OpenAPI JSON -> 代码生成 -> mock 验证流程
- [x] 6.2 在 `VITE_ENABLE_MSW=true` 下验证 users/account 关键路径
- [x] 6.3 在 `VITE_ENABLE_MSW=false` 联调模式复跑同一关键路径
- [x] 6.4 补充开发说明，明确生成命令、mock 开关与 fixtures 维护约定
