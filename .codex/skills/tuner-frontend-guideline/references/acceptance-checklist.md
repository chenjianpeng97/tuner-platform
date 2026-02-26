# Frontend Acceptance Checklist

## A. API 与代码结构

- [ ] `docs/api_doc.json` 与当前迭代需求一致。
- [ ] 已执行 `pnpm --dir frontend run api:generate`。
- [ ] `src/api/generated/*` 无手工改动。
- [ ] 页面仅通过 `src/api/{user,account}/*` 调用接口。

## B. Mock 基线

- [ ] fixtures 位于 `src/mocks/fixtures/*` 且字段与合同一致。
- [ ] handlers 读取 fixtures，无长期内联临时对象。
- [ ] handler 路径支持跨源匹配（`*/api/v1/...`）。
- [ ] `pnpm --dir frontend run dev:mock` 可正常启动并命中 mock。

## C. 联调验证

- [ ] `VITE_ENABLE_MSW=true`：users/account 关键路径通过。
- [ ] `VITE_ENABLE_MSW=false`：同一路径联调通过。
- [ ] mock 未命中场景有排障记录（worker、URL、env）。

## D. 构建与回归

- [ ] `pnpm --dir frontend run build` 通过。
- [ ] 页面语义符合 `Business`/`Template` 边界。
- [ ] 新增 mock 样本可复用，不依赖一次性临时数据。
