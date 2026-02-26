# Frontend Workflow (No OpenSpec Content)

## 固定输入与输出

- 合同输入：`docs/api_doc.json`
- 生成输出：`frontend/src/api/generated/*`
- 模块封装：`frontend/src/api/user/*`、`frontend/src/api/account/*`
- Mock 数据：`frontend/src/mocks/fixtures/*`
- Mock 处理：`frontend/src/mocks/handlers.ts`

## 实施顺序

1. 明确需求属于 `Business` 还是 `Template` 参考。
2. 更新/确认 `docs/api_doc.json`。
3. 执行 `pnpm --dir frontend run api:generate`。
4. 在 `src/api/{user,account}/*` 进行业务封装。
5. 在 `src/mocks/fixtures/*` 增补基线样本并更新 handlers。
6. 页面层接入模块封装 API，不直接耦合 generated。
7. 依次验证 mock 模式与联调模式。
8. 执行 `pnpm --dir frontend run build` 作为提交前门槛。

## 目录约束

- 不在 `src/api/generated/*` 手工改动。
- 不把可对接后端能力放进 template-only 目录。
- 优先复用模块 API 与 fixtures，避免页面层复制请求逻辑。
