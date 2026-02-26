---
name: tuner-frontend-guideline
description: 面向 tuner-platform 的前端开发规范。用于前端新功能、重构、联调、mock 和 API 代码生成任务，尤其当任务涉及 frontend/、docs/api_doc.json、orval、msw 时触发。提供 Template/Business 边界、API 分层、Orval 生成、MSW 基线数据与验收流程约束。
---

# Frontend Guideline

按以下顺序执行，保持中等约束：关键流程必须遵守，具体实现可做工程判断。

## 1) 先确定页面语义边界

- 将 `Template` 视为样式和布局参考区，不承载真实业务功能。
- 将可对接后端的功能放入 `src/features/<module>`。
- 保持侧边栏语义清晰：`Business` 是业务入口，`Template` 是展示参考入口。
- 避免把真实业务继续堆到 template 目录。

需要边界示例时，读取 `references/template-boundary.md`。

## 2) 固化 API 分层

- 将合同源固定为 `docs/api_doc.json`。
- 将 Orval 生成层固定为 `frontend/src/api/generated/*`，禁止手改 generated 文件。
- 按后端模块划分业务 API 封装层：`frontend/src/api/user/*`、`frontend/src/api/account/*`。
- 让页面层仅依赖模块封装层，不直接耦合 generated 细节。

需要完整目录约定时，读取 `references/frontend-workflow.md`。

## 3) 用 Orval 生成并更新 API 代码

- 使用 `frontend/orval.config.ts`，输入 `../docs/api_doc.json`，输出 `src/api/generated/*`。
- 执行 `pnpm --dir frontend run api:generate` 更新类型和请求函数。
- 在模块封装层适配页面所需参数与返回模型，避免在页面中散落协议细节。

需要 Orval 工作机制与常见问题时，读取 `references/orval-msw-playbook.md`。

## 4) 用 MSW 维护可复用 mock 基线

- 将 mock 数据放在 `frontend/src/mocks/fixtures/*.json`。
- 让 handlers 读取 fixtures，避免长期内联临时对象。
- 用跨源 URL 匹配（如 `*/api/v1/...`）覆盖 `localhost:5173 -> 127.0.0.1:8000` 场景。
- 使用 `pnpm --dir frontend run dev:mock` 进入 mock 模式。
- 缺失 worker 时先执行 `pnpm --dir frontend run mock:init`（或依赖 `mock:ensure` 自动兜底）。

需要排障步骤时，读取 `references/orval-msw-playbook.md`。

## 5) 联调与验收

- 在 `VITE_ENABLE_MSW=true` 下验证 users/account 关键路径。
- 在 `VITE_ENABLE_MSW=false` 下复跑同一关键路径。
- 在提交前执行 `pnpm --dir frontend run build` 并确保通过。
- 将开发态双请求优先识别为 React StrictMode 检查行为，不直接判定为生产缺陷。

需要完整检查单时，读取 `references/acceptance-checklist.md`。

## 6) 输出要求

- 输出中给出使用的命令、涉及目录和关键决策依据。
- 优先复用统一 fixtures 与模块封装，减少场景漂移与重复逻辑。
- 新增规则时同步更新本 skill 的 references 文件，保持规范可追踪。
