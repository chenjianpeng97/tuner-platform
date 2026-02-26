## Why

当前前端 `UserList` 页面虽然已在上个迭代完成基础功能，但页面结构与项目内既有 CRUD 页面规范不一致，导致交互与视觉层级不统一，影响可维护性与使用一致性。现在需要将其对齐到已有 `Tasks` 页面布局模式，确保同类业务页面具备一致的信息组织与操作体验。

## What Changes

- 调整 `UserList` 页面整体结构，使其遵循现有 `Tasks` CRUD 页面布局范式（页面头部、操作区、列表区等分层一致）。
- 复用并对齐已有前端布局组件与样式约定，避免新增不必要的自定义视觉规则。
- 在不改变现有用户管理核心功能与 API 调用行为的前提下，重排页面元素位置与层级关系。
- 确保页面在当前路由与数据流下保持可用，且与 `Tasks` 页面在信息架构上达到一致。

## Capabilities

### New Capabilities
- `frontend-userlist-crud-layout-consistency`: 规范 UserList 页面布局为项目既有 CRUD 标准，要求与 Tasks 页面结构模式一致。

### Modified Capabilities
- None.

## Impact

- Affected code: `frontend/src/routes/` 下 UserList 页面相关路由/页面文件；`frontend/src/components/` 中该页面引用的布局与列表容器组件。
- APIs: 无新增或变更后端 API；仅前端页面结构调整。
- Dependencies: 无新增第三方依赖。
- Systems: 影响前端用户管理页面的 UI 一致性与可维护性，对后端与数据契约无影响。
