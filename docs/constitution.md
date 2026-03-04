# Tuner Platform Constitution

## 1. 目的与适用范围

本宪章定义本项目在 API 文档驱动开发（SDD）下的统一实现流程，适用于：

- 后端 FastAPI（domain/entity、infrastructure/orm、presentation/pydantic/dataclass）
- 前端 React（Orval 生成 apiclient 与 mock）
- 前后端联调、回归、交付验收

---

## 2. 核心原则

1. 单一契约源：`docs/api_doc.json` 是前后端接口契约唯一基线。
2. 分层隔离：Domain 规则优先，ORM 与 Presentation 不反向污染 Domain。
3. 生成代码只读：`frontend/src/api/generated/*` 禁止手工修改。
4. 可回归：每次变更必须可通过自动化门禁验证。

---

## 3. API 文档后的后端骨架策略

采用“两段式生成”：

1. Contract DTO 自动生成（可覆盖）
- presentation request/response（Pydantic）
- application request/response（dataclass）

2. Domain/ORM 骨架半自动生成（不覆盖手写规则）
- domain entity/value object skeleton（含 TODO invariants）
- infrastructure orm table + mapper skeleton
- alembic revision stub

要求：

- 生成器对“业务规则实现文件”仅首次创建，不做覆盖更新。
- 字段应维护 lineage（例如 `user.email`）用于全链路影响分析。

---

## 4. 后端实现 SOP

1. 冻结契约
- 锁定 `docs/api_doc.json`，明确字段语义与错误码。

2. 生成后端骨架
- 生成 Contract DTO 与 Domain/ORM 初始骨架。

3. 领域层先行（TDD）
- 先写 domain unit test（无 DB 依赖）。
- 固化 invariant、状态迁移、领域异常。

4. 应用层编排
- 编写 interactor/usecase tests（mock ports）。
- 保证命令编排、事务边界、异常语义正确。

5. ORM 与迁移
- 完成 SQLAlchemy mapping/repository。
- 编写 Alembic migration 与回滚验证。
- 补齐 repository integration tests。

6. Presentation 接线
- controller、鉴权、错误翻译。
- 编写 HTTP-stage 编排/契约测试（可用 Behave）。

7. 发布门禁
- 导出 OpenAPI 与 `docs/api_doc.json` 对比。
- 所有测试通过后方可合并。

---

## 5. 前端实现 SOP（UI 原型完成 + Orval 已生成）

1. 定义边界
- `Template` 仅作样式/布局参考，不承载真实业务。
- 业务能力放入 `src/features/<module>`。

2. 固化 API 分层
- 页面层只依赖 `src/api/<module>/*` 封装层。
- 不直接在页面中使用 `src/api/generated/*` 细节。

3. 状态模型先行
- 每页先定义加载态、空态、错误态、成功态、权限态。
- 先完成数据流与状态迁移，再做 UI 绑定。

4. MSW 基线与关键链路
- fixtures 统一放 `src/mocks/fixtures/*.json`。
- handlers 统一读取 fixtures，减少重复内联 mock。
- 在 `VITE_ENABLE_MSW=true` 下跑通关键路径。

5. 组件与交互落地
- 容器组件负责数据，展示组件保持纯渲染。
- 表单校验、错误提示、loading/disabled 行为统一。

6. 联调与差异收敛
- 在 `VITE_ENABLE_MSW=false` 下复跑同一关键路径。
- 收敛 mock 与真实接口的字段/错误码/鉴权差异。

7. 提交门禁
- 执行 `pnpm --dir frontend run build` 必须通过。
- generated 目录不得手改。

---

## 6. 全链路活文档与自动校验（HexDDD 愿景落地）

CI 必须包含三层 Gate：

1. Schema Gate
- ORM/Alembic 变更必须通过前进/回滚验证。

2. Contract Gate
- FastAPI 导出 OpenAPI 与 `docs/api_doc.json` 做 breaking-change 检查。

3. Binding Gate
- Contract 变更触发 Orval regenerate。
- 前端类型编译与关键契约测试必须通过。

增强建议：

- 建立 field lineage map（domain/orm/api/ts 绑定关系）。
- 变更某字段时自动给出受影响模型、接口、页面与测试清单。

---

## 7. 执行与维护

1. 本宪章默认适用于新功能、重构、联调与接口演进。
2. 任何偏离本宪章的实现需在 PR 中给出理由与回滚方案。
3. 当流程调整时，需同步更新本文件与相关 workflow 文档。

