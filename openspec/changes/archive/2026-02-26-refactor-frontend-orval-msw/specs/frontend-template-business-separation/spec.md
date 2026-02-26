## ADDED Requirements

### Requirement: 导航结构 SHALL 分离 template 区与 business 区
侧边栏信息架构 SHALL 区分 template/demo 页面与 business 页面，避免展示内容与契约驱动功能混杂。

#### Scenario: 侧边栏分组清晰隔离
- **WHEN** 用户打开认证后的导航侧边栏
- **THEN** template/demo 入口被归入独立的 template 分组
- **THEN** 真实后端业务流程入口被归入独立的 business 分组

### Requirement: Template 页面 SHALL 保持可访问并仅作为样式参考
Template 页面 SHALL 继续可访问用于视觉参考，但不得作为后端契约行为的权威来源。

#### Scenario: 重组后 template 页面仍可访问
- **WHEN** 前端代码将 template 页面迁移到 template 语义目录
- **THEN** 这些页面仍可从 UI 导航访问
- **THEN** business 实现不再依赖 template demo 数据模块
