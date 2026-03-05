## 1. Survey 导航结构调整

- [x] 1.1 在 Survey 模块导航配置中将 Templates 与 Assignments 注册到 `items` 下，并保持原有路由 path 不变
- [x] 1.2 对齐分组展开/折叠交互行为到现有 “Secured by Clerk” 分组模式
- [x] 1.3 本地验证侧边栏展开后可进入 Templates 与 Assignments 页面

## 2. Templates 列表对齐 Users 交互

- [x] 2.1 盘点并复用 Users 列表使用的筛选、表格选择列、Actions 菜单、分页器组件
- [x] 2.2 重构 templates 列表页面布局与组件组合，补齐 Filter、选择列、Actions、分页器
- [x] 2.3 校验 templates 列表在筛选、勾选、菜单触发、分页切换下的交互一致性

## 3. Assignments 列表对齐 Users 交互

- [x] 3.1 复用与 templates 相同的通用列表模式到 assignments 页面
- [x] 3.2 重构 assignments 列表并补齐 Filter、选择列、Actions、分页器
- [x] 3.3 校验 assignments 列表在筛选结果集中的选择与分页语义一致

## 4. UI Steps 重构与验证

- [x] 4.1 更新 `features/ui_steps` 中 survey 相关步骤定位与断言，匹配新导航层级与新列表控件
- [x] 4.2 按需调整受影响 `.feature` 场景描述，使其与统一后的 UI 行为一致
- [x] 4.3 运行 survey assignment 相关 UI 场景并修复因重构导致的步骤失败

## 5. 回归与收尾

- [x] 5.1 回归检查 Survey 导航、templates 列表、assignments 列表核心路径
- [x] 5.2 清理重构中产生的冗余组件引用与不再使用的旧列表实现
- [x] 5.3 更新必要文档/备注（如前端约定或测试运行说明）
