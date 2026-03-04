## ADDED Requirements

### Requirement: BDD 先行门禁
系统交付流程 SHALL 要求在业务实现开始前先完成与评审 Gherkin 场景，且场景必须覆盖本变更核心业务能力与关键异常流。

#### Scenario: 开发前完成 Gherkin 基线
- **WHEN** 团队准备开始实现问卷相关功能
- **THEN** 必须先提交并评审通过覆盖模板、任务、提交、进度、结果、权限、审计的 Gherkin 场景

#### Scenario: 未完成 Gherkin 不得进入实现
- **WHEN** Gherkin 场景未完成或未评审通过
- **THEN** 该变更不得进入业务代码实现阶段

### Requirement: TDD 先行门禁
系统交付流程 SHALL 要求后端代码采用 TDD（Red-Green-Refactor），并遵循当前仓库既有各层单元测试风格与覆盖率目标。

#### Scenario: 后端新逻辑按 TDD 开发
- **WHEN** 开发者实现新的后端领域或应用逻辑
- **THEN** 先编写失败测试，再写最小实现通过测试，最后重构并保持测试通过

#### Scenario: 测试风格一致性
- **WHEN** 开发者为新功能新增后端测试
- **THEN** 测试命名、fixture、mock 边界、断言风格应与现有同层测试风格保持一致

### Requirement: 验收自动化门禁
系统交付流程 SHALL 同时具备接口层 BDD 自动化验收测试与 UI 端到端 Playwright 自动化测试，二者均通过后方可作为合格交付。

#### Scenario: 接口层 BDD 自动化
- **WHEN** 变更进入验收阶段
- **THEN** 必须存在可执行的 HTTP-stage Behave 自动化场景并通过

#### Scenario: UI 端到端自动化
- **WHEN** 变更进入验收阶段
- **THEN** 必须存在覆盖核心用户旅程的 Playwright 自动化测试并通过

### Requirement: Feature 文件按业务能力组织
系统测试规范 SHALL 要求 feature 文件表达系统核心业务能力，不得按测试层（HTTP/UI）拆分为独立 feature 文件；测试层差异 SHALL 通过 `behave --stage` 选择对应步骤实现。

#### Scenario: 禁止按层命名 feature 文件
- **WHEN** 团队新增问卷相关 feature 文件
- **THEN** 文件命名不得使用 `*_ui.feature`、`*_http.feature` 或等价按层后缀命名方式

#### Scenario: 通过 stage 区分步骤实现
- **WHEN** 同一业务能力需要在接口层和 UI 层复用验收场景
- **THEN** 复用同一份业务导向 feature 文件，并通过 `behave --stage` 选择 HTTP 或 UI 步骤实现
