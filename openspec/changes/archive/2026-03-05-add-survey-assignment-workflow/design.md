## 上下文

当前仓库仅有前端 `survey-forms` 演示页，后端应用层/领域层/表现层尚无问卷业务模块。我们需要补齐全栈能力：
- 问卷模板创建与发布；
- 面向指定用户创建问卷填写任务；
- 被分发用户填写与重复提交；
- 任务进度跟踪与结果查看。

约束与现有架构：
- 后端采用分层架构（presentation -> application -> domain -> infrastructure），使用 Dishka DI，并采用命令/查询分离。
- 前端采用按 feature 组织，使用自动生成路由树与 API codegen 模式。
- V1 范围明确：仅实名提交、题型限定单选/多选/文本、不支持组织级分发。

相关角色：
- 问卷运营/管理员：维护模板并管理填写任务。
- 被分发用户：执行问卷填写并提交。
- 审计/安全负责人：监控敏感答案访问行为。

## 目标 / 非目标

**目标：**
- 提供不可变模板版本能力，并确保任务绑定已发布版本。
- 提供任务状态生命周期：`in_progress` 与 `completed`。
- 支持在关闭/截止前覆盖式重复提交，并保持进度计数准确。
- 提供任务进度、按用户最新结果、按题聚合汇总结果。
- 对结果查看执行权限校验，并记录原始答案访问审计轨迹。
- 给出可执行实现路径，包括后端 API 契约与前端集成任务。
- 明确“BDD 先行 + TDD 先行 + 验收自动化”质量约束并落到任务顺序与交付门禁。

**非目标：**
- 匿名问卷。
- 扩展题型（评分、日期、附件上传等）。
- 基于组织/部门的分发对象圈选。
- 超出任务级汇总的高级分析能力。
- V1 内的消息通知渠道（邮件/推送）。

## 关键设计决策

### 决策 1：按生命周期职责拆分领域模型
- 使用独立聚合：
  - `SurveyTemplate` (draft editable)
  - `SurveyTemplateVersion` (immutable published snapshot)
  - `SurveyAssignment` (task metadata, assignee set, status, due_at)
  - `SurveySubmission` (latest effective submission per assignment+assignee)
- 决策理由：
  - 让模板编排数据与执行数据边界清晰。
  - 在数据模型层强制版本冻结约束。
- 备选方案：
  - 使用单一可变模板并在 JSON 日志保留历史：已放弃，查询能力弱且数据一致性风险更高。

### 决策 2：提交存储按参与人保留“最新有效记录”
- Persist one logical effective response per `(assignment_id, assignee_user_id)` with update-on-resubmit semantics.
- Track `submitted_at` and revision metadata for auditability.
- 决策理由：
  - 符合产品规则：最后一次提交为有效结果。
  - 简化进度统计和结果查询实现。
- 备选方案：
  - 仅追加提交记录并每次查询最新：V1 放弃，查询复杂度和索引成本更高。

### 决策 3：任务状态采用受控且可推导模型
- 允许状态：`in_progress`、`completed`。
- 状态流转规则：
  - `in_progress -> completed` automatically when `submitted_count == assignee_count`.
  - `in_progress -> completed` manually by privileged close action.
- 一旦 `completed`，禁止继续提交。
- 决策理由：
  - 与用户语义“进行中/收集完毕”完全一致。
- 备选方案：
  - 为任务增加草稿/发布状态：暂缓，避免 V1 增加额外运营复杂度。

### 决策 4：结果可见性权限与审计策略
- `submissions` 与 `summary` 查询要求具备问卷库权限。
- 每次原始提交明细读取都必须写入审计事件。
- 审计事件最小字段：
  - actor user id
  - assignment id
  - action (`survey_result_detail_view`)
  - timestamp
- 决策理由：
  - 满足当前可见性决策，并通过补偿性审计控制隐私风险。
- 备选方案：
  - 限制为任务创建者/管理员可见：默认更安全，但与已确认业务偏好不一致。

### 决策 5：统一使用 `/api/v1/surveys` API 命名空间
- 接口范围：
  - `POST/GET/GET by id/PATCH` for templates
  - `POST publish` for template version creation
  - `POST/GET/GET by id/POST close` for assignments
  - `GET/PUT my-submission` for assignee self-service
  - `GET submissions` and `GET summary` for results
- 决策理由：
  - 模块命名空间清晰统一，前端接入路径明确。
- 备选方案：
  - 将模板和任务拆到 surveys 外部独立根路径：放弃，接口可发现性更差。

### 决策 6：测试先行交付策略（BDD First + TDD First）
- 在进入业务实现前，先完成以下基线：
  - 基于现有 specs 与需求，编写并评审 Gherkin 场景（BDD 先行）。
  - 盘点并对齐后端各层（domain/application/presentation/infrastructure）测试风格与断言模式。
- 开发过程采用 TDD：
  - 先写失败测试（Red）；
  - 再写最小实现使其通过（Green）；
  - 最后重构并保持测试通过（Refactor）。
- 验收自动化要求：
  - 接口层：HTTP-stage Behave（BDD）覆盖主干业务流与关键异常流；
  - UI 层：UI-stage Behave（step 内部使用 Playwright）覆盖关键用户旅程（模板发布、任务分发、用户填写、进度查看、结果查看）。
- 决策理由：
  - 业务链路跨前后端且状态多，先定义行为再实现可降低返工。
  - 与当前仓库已有 Behave 测试基础一致，便于复用。
- 备选方案：
  - 先实现后补测试：放弃，容易导致行为偏差和回归成本上升。

## 风险与权衡

- [结果可见范围较大导致隐私暴露] -> 强制权限校验、强制审计记录、提供审计导出能力。
- [并发提交导致竞态] -> 在提交更新与进度重算时使用事务 + 行级锁（或乐观锁版本校验）。
- [模板结构演进影响历史任务] -> 使用版本快照并在发布流程中做兼容性校验。
- [汇总聚合性能风险] -> 先采用按需聚合 + 索引，指标压力出现后再引入物化投影。
- [文本答案体量大] -> 结果明细接口支持分页并设置响应体大小保护。
- [测试先行增加短期交付成本] -> 将测试编写模板化并分层并行推进，缩短反馈周期。

## 迁移与发布计划

1. 先完成 Gherkin 场景集（按 capability 分组）并评审通过。
2. 盘点后端现有测试风格，形成本变更 TDD 编写约束清单。
3. 为 template、template_version、assignment、assignment_assignee、submission、audit 表新增数据库迁移。
4. 按 TDD 方式实现模板与任务领域层/应用层/表现层。
5. 按 TDD 方式实现提交写入链路与进度更新机制，并通过事务保证一致性。
6. 按 TDD 方式实现结果明细、结果汇总与授权审计链路。
7. 完成接口层 HTTP-stage Behave 自动化，覆盖核心流与异常流。
8. 完成前端页面与 API Client 集成，替换当前 survey demo 入口。
9. 完成 UI-stage Behave 自动化并纳入发布前检查。
10. 视需要使用特性开关灰度发布，优先对管理员开放。

回滚策略：
- 关闭路由暴露与特性开关。
- 保留已迁移数据表，不进行生产数据的破坏性回滚。

## 待确认问题

- V1 是否需要对外提供审计导出 API，还是先仅保留内部查询能力？
- 手动结束任务时是否应强制填写“结束原因”以满足合规追溯？
- V1 管理端是否需要模板软删除/归档能力？
