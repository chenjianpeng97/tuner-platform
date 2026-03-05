## Context

当前 Survey 相关前端页面在导航信息架构与列表交互上，与既有 Users 页面存在明显不一致：Users 已形成稳定的筛选、批量选择、动作菜单与分页模式，而 Templates/Assignments 仍使用不同实现。该不一致直接影响可用性、复用率与 UI 行为步骤稳定性。

约束条件：
- 仅进行前端重构与 UI 测试步骤调整，不改动后端 API 契约。
- 保持现有路由语义（templates 与 assignments 不改业务语义），仅调整导航挂载位置与列表交互组件组合。
- 复用 Users 页面已落地的组件与使用规则，避免引入新的自定义模式。

## Goals / Non-Goals

**Goals:**
- 将 Templates 与 Assignments 注册到 Survey 模块的 `items`，并支持与 “Secured by Clerk” 类似的分组展开/折叠交互。
- 将 templates 与 assignments 列表统一为 Users 列表同款交互基线：Filter/筛选、行选择列（含多选）、`Actions` 三点菜单、分页器。
- 统一组件使用方式（表格、筛选区、分页、action menu）以降低样式和行为分叉。
- 调整 `features/ui_steps` 以匹配新 UI 结构，恢复对应场景通过。

**Non-Goals:**
- 不新增业务字段或后端接口。
- 不重构 Users 页面本身。
- 不引入新的设计系统规范之外的视觉 token 或交互范式。

## Decisions

1. **导航结构采用分组式注册，而非平铺顶级入口**
   - 决策：将 Templates/Assignments 作为 Survey 分组下 `items` 进行注册。
   - 原因：与 “Secured by Clerk” 一致，降低用户跨模块认知切换。
   - 备选方案：保持平铺路由入口；被拒绝，因为会继续放大信息架构不一致。

2. **列表 UI 采用 Users 页面已使用的通用构件组合**
   - 决策：模板列表与任务列表重用 Users 的表格模式（filter bar + selectable rows + actions dropdown + pagination）。
   - 原因：可复用稳定组件与交互语义，减少维护面。
   - 备选方案：在 survey 内实现独立列表组件；被拒绝，因为重复建设且易产生行为漂移。

3. **UI 步骤按“语义定位优先，结构定位兜底”重构**
   - 决策：优先匹配统一后的按钮/列头/菜单可见文本与角色语义；仅在必要时回落到结构选择器。
   - 原因：在组件内部 DOM 变化时更稳定，降低脆弱断言。
   - 备选方案：继续依赖旧选择器；被拒绝，因为重构后失败概率高。

## Risks / Trade-offs

- [风险] 复用 Users 组件时字段映射不完整导致列表展示缺列 → [缓解] 在 survey 页面增加显式列配置并补齐映射测试。
- [风险] 导航迁移影响现有书签路径可达性 → [缓解] 保持原路由 path 不变，仅调整侧边栏挂载与显示层级。
- [风险] UI 步骤仍受文案微调影响 → [缓解] 在步骤中优先使用角色与稳定文本片段，避免脆弱全量文本匹配。
- [权衡] 统一组件将限制 survey 页面个性化交互 → [缓解] 以一致性优先，后续若有明确业务差异再通过扩展点处理。

## Migration Plan

1. 调整 Survey 模块导航注册结构并本地验证可展开/折叠。
2. 替换 Templates 列表为 Users 同款列表组合，验证筛选、选择、actions、分页。
3. 替换 Assignments 列表为同款组合，验证筛选、选择、actions、分页。
4. 重构 `features/ui_steps` 对应步骤断言并执行相关场景。
5. 回归检查受影响页面与关键 UI 场景；如失败则按页面粒度回滚重构提交。

## Open Questions

- templates/assignments 具体复用 Users 的哪些列选择与批量动作策略（仅 UI 对齐，还是动作语义也要完全对齐）？
- `features/ui_steps` 是否只需覆盖 `survey-assignment-workflow.feature`，还是包含其他 survey 相关 feature 文件？
