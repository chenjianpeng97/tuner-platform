## 1. Layout Baseline Alignment

- [x] 1.1 对照 `Tasks` 页面梳理标准 CRUD 结构分区（标题区、操作区、数据区）并标注 UserList 差异
- [x] 1.2 在 UserList 页面中调整容器层级与区域顺序，使其与 `Tasks` 页面布局骨架一致

## 2. UserList Page Refactor

- [x] 2.1 复用现有布局组件与样式约定重排 UserList 页面头部与操作区，不新增全局视觉规范
- [x] 2.2 保持 UserList 现有数据加载与列表渲染逻辑不变，仅完成结构性调整
- [x] 2.3 校验页面内核心交互入口在新布局下仍可发现且语义一致

## 3. Verification

- [x] 3.1 对比调整前后 UserList 核心功能行为，确认无 API 调用与业务语义回归
- [x] 3.2 进行前端本地回归，确认 UserList 页面在当前路由下可正常访问与操作
- [x] 3.3 记录与 `Tasks` 页面布局对齐结果，作为后续 CRUD 页面统一规范参考
