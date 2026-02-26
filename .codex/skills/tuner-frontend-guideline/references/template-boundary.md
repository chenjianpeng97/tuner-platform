# Template / Business Boundary

## 目标

将展示参考与业务实现分离，避免模板代码与真实业务耦合。

## 规则

- `Template`：
  - 仅承载页面样式、布局、交互展示。
  - 可复用 UI 组件与视觉结构。
  - 不承载后端可对接业务流程。

- `Business`：
  - 承载真实业务入口与数据流。
  - 调用 `src/api/{user,account}/*` 模块 API。
  - 以当前后端合同为边界实现功能。

## 目录建议

- 模板参考：`frontend/src/features/template/*`
- 业务实现：`frontend/src/features/<module>/*`
- 路由保持语义清晰，可在侧边栏区分 `Business` 与 `Template`。

## 迁移原则

1. 先保留 URL 稳定，优先迁移代码目录语义。
2. 先抽离业务数据流，再复用模板 UI。
3. 页面最终依赖业务 API 模块，不依赖模板假数据。
