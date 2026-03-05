## MODIFIED Requirements

### Requirement: 验收自动化门禁
系统交付流程 SHALL 同时具备接口层与 UI 层的 Behave 自动化验收测试（通过 `behave --stage` 选择实现层）；其中 HTTP-stage SHALL 支持 `mock` 与 `real` 双模式运行，同一业务场景须可在两种模式下复用执行。`real` 模式下 HTTP-stage 与 UI-stage SHALL 共用每场景 `cleanup -> seed -> auth-bootstrap` 数据夹具流程。二者均通过后方可作为合格交付。

#### Scenario: 接口层 mock 模式 BDD 自动化
- **WHEN** 变更进入验收阶段并以 HTTP-stage `mock` 模式执行
- **THEN** 必须存在可执行的 HTTP-stage Behave 自动化场景并验证接口层编排通过

#### Scenario: 接口层 real 模式 BDD 自动化
- **WHEN** 变更进入验收阶段并以 HTTP-stage `real` 模式执行
- **THEN** 必须存在连接真实后端接口服务与数据库的 HTTP-stage Behave 自动化场景并通过

#### Scenario: UI-stage BDD 自动化
- **WHEN** 变更进入验收阶段
- **THEN** 必须存在覆盖核心用户旅程的 `behave --stage ui` 自动化场景并通过

#### Scenario: real 模式共享夹具门禁
- **WHEN** 变更进入 `real` 模式验收阶段
- **THEN** HTTP-stage 与 UI-stage 必须通过共享夹具脚本完成每个场景的数据清理、注入与鉴权初始化
