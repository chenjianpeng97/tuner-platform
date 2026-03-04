# Orval + MSW Playbook

## Orval 在本项目中的作用

- 从 `docs/api_doc.json` 生成 TypeScript 类型与请求函数。
- 将接口字段和分页/排序参数约束前置到编译期。
- 减少手写请求代码和字段漂移。

## Orval 使用

1. 检查 `frontend/orval.config.ts`：
   - input: `../docs/api_doc.json`
   - output: `src/api/generated/*`（`mode: tags-split`）
   - mutator: `./src/api/http-client.ts` 的 `orvalMutator`
2. 运行：
   - `pnpm --dir frontend run api:generate`
3. 在 `frontend/src/api/{users,account}/*` 适配页面调用参数。

## 本次迁移约定（2026-03）

1. 只使用 tags-split 产物：
   - `frontend/src/api/generated/models/*`
   - `frontend/src/api/generated/account/account.ts`
   - `frontend/src/api/generated/users/users.ts`
2. 业务封装层统一通过工厂调用：
   - `getAccount()` / `getUsers()`
3. `mockServiceWorker.js` 不由 Orval 生成：
   - Orval 负责生成 `*.msw.ts` handler 代码
   - `pnpm --dir frontend run mock:init` 负责初始化浏览器 worker 文件

## 推荐命令流

1. 重新生成 API client + Orval MSW handlers：
   - `pnpm --dir frontend run api:generate`
2. 首次或 worker 丢失时初始化：
   - `pnpm --dir frontend run mock:init`
3. 启动前端 mock 开发：
   - `pnpm --dir frontend run dev:mock`
4. 生成后做类型检查：
   - `pnpm --dir frontend exec tsc -p tsconfig.app.json --noEmit`

## MSW 使用

1. fixtures 放在 `frontend/src/mocks/fixtures/*.json`。
2. handlers 从 fixtures 读取返回数据。
3. handler URL 使用跨源匹配，例如 `*/api/v1/users/`。
4. 启动 mock：
   - `pnpm --dir frontend run dev:mock`
5. 首次或 worker 丢失时：
   - `pnpm --dir frontend run mock:init`

## 常见问题排查

### Q1: `mockServiceWorker.js` MIME 是 `text/html`

- 现象：worker 注册失败，提示 unsupported MIME type。
- 处理：
  1. 访问 `http://127.0.0.1:5173/mockServiceWorker.js` 检查是否返回 JS。
  2. 运行 `pnpm --dir frontend run mock:init`。
  3. 重启 `pnpm --dir frontend run dev:mock`。

### Q2: 请求未被 MSW 命中

- 检查点：
  1. `VITE_ENABLE_MSW` 是否为 `true`。
  2. handler 是否写成跨源匹配（`*/api/v1/...`）。
  3. 请求 URL 是否与 handler path 一致（含尾斜杠）。

### Q3: 开发环境出现双请求

- 优先判断 React StrictMode 开发态双调用。
- 先确认生产构建行为与真实业务逻辑，再决定是否处理。
