## ADDED Requirements

### Requirement: HTTP-stage 服务绑定模式选择
HTTP-stage Behave 验收测试 SHALL 支持通过统一配置选择 `mock` 或 `real` 服务绑定模式，并在测试环境初始化阶段完成模式解析。

#### Scenario: 显式选择 mock 模式
- **WHEN** 执行 HTTP-stage 测试并设置模式为 `mock`
- **THEN** 测试环境应绑定 mock 接口服务实现并执行同一套业务场景

#### Scenario: 显式选择 real 模式
- **WHEN** 执行 HTTP-stage 测试并设置模式为 `real`
- **THEN** 测试环境应绑定真实后端接口服务实现并执行同一套业务场景

### Requirement: 场景契约跨模式复用
系统测试规范 SHALL 要求 HTTP-stage 在 `mock` 与 `real` 模式下复用同一份 feature 场景与步骤契约，不得按模式复制业务 feature。

#### Scenario: 复用同一份 feature 场景
- **WHEN** 同一业务能力需要在 HTTP-stage 的 `mock` 与 `real` 模式验证
- **THEN** 两种模式均使用同一份业务导向 feature 文件

#### Scenario: 禁止按模式复制步骤契约
- **WHEN** 团队为 HTTP-stage 增加模式切换能力
- **THEN** 不得通过复制一套独立业务步骤契约实现 `real` 模式

### Requirement: real 模式集成前置条件
系统在 HTTP-stage `real` 模式执行前 SHALL 验证数据库与后端服务前置条件满足，前置条件不满足时必须明确失败并给出原因。

#### Scenario: real 模式前置条件满足
- **WHEN** 数据库可连接且真实后端接口服务可用
- **THEN** HTTP-stage `real` 模式测试应正常执行并产出验收结果

#### Scenario: real 模式前置条件不满足
- **WHEN** 数据库未就绪或真实后端接口服务不可用
- **THEN** 测试应在执行前置检查阶段失败并报告缺失依赖

### Requirement: real 模式共享数据夹具脚本
系统在 `real` 模式执行时 SHALL 使用一套共享的测试数据夹具脚本（清理、注入、鉴权初始化），并允许 HTTP-stage 与 UI-stage 共同调用同一实现。

#### Scenario: HTTP 与 UI 共用同一夹具脚本
- **WHEN** HTTP-stage 与 UI-stage 在 `real` 模式执行同一业务场景
- **THEN** 两者均调用同一套 `cleanup -> seed -> auth-bootstrap` 夹具脚本流程

#### Scenario: 每个场景前执行清理与注入
- **WHEN** 任一 `real` 模式场景开始执行前
- **THEN** 系统应先完成数据库清理与基线数据注入，再进入步骤执行

### Requirement: real 模式鉴权上下文初始化
系统在 `real` 模式 SHALL 为测试阶段初始化可复用的鉴权上下文，使受保护接口在 HTTP-stage 与 UI-stage 均可按场景契约访问。

#### Scenario: HTTP-stage 使用已初始化鉴权上下文
- **WHEN** HTTP-stage `real` 模式访问受保护接口
- **THEN** 请求应携带由共享夹具脚本初始化的有效鉴权信息（如会话 Cookie）

#### Scenario: UI-stage 使用相同身份基线
- **WHEN** UI-stage `real` 模式执行受保护用户旅程
- **THEN** 浏览器会话应基于同一套已注入测试身份完成鉴权访问
