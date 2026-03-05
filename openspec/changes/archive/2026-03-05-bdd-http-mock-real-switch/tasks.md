## 1. HTTP-stage 模式配置与引导

- [x] 1.1 在 HTTP-stage 环境初始化中新增统一模式解析（`mock`/`real`），并设置默认值为 `mock`
- [x] 1.2 将模式值注入 Behave context/测试容器构建入口，移除步骤层分支选择逻辑
- [x] 1.3 为无效模式输入增加显式失败与错误提示

## 2. DI 绑定与步骤复用改造

- [x] 2.1 重构 HTTP-stage 容器装配，按模式切换 mock 适配器与真实后端服务适配器
- [x] 2.2 保持现有业务 feature 与 step 定义不变，验证双模式复用同一场景契约
- [x] 2.3 为关键编排接口增加模式无关断言，确保 mock/real 结果契约一致

## 3. real 模式集成前置与数据生命周期

- [x] 3.1 在 real 模式执行前加入 DB 与后端服务可用性检查
- [x] 3.2 建立共享 real 模式测试数据脚本（`cleanup`/`seed`/`auth-bootstrap`）并定义统一调用接口
- [x] 3.3 为前置条件失败场景补充可观测错误输出（缺失依赖、连接失败原因）
- [x] 3.4 将共享夹具脚本接入 HTTP-stage real 模式 `before_scenario` 生命周期
- [x] 3.5 将共享夹具脚本接入 UI-stage real 模式 `before_scenario` 生命周期

## 4. 验收与质量门禁更新

- [x] 4.1 更新 HTTP-stage BDD 验收流程，覆盖 `mock` 编排校验与 `real` 集成校验（每场景执行共享夹具）
- [x] 4.2 对齐 UI-stage 现有 `mock`/`dev` 与 HTTP-stage 模式命名及使用说明
- [x] 4.3 更新工程质量门禁文档/规范，明确双模式通过条件与共享夹具门禁

## 5. 命令入口与 CI 落地

- [x] 5.1 新增或调整 Makefile/脚本参数，支持按模式执行 HTTP-stage BDD
- [x] 5.2 在 CI 中增加模式化运行策略（快速 mock gate + 集成 real gate）
- [x] 5.3 验证本地与 CI 的运行结果，确保任务完成后 `openspec apply` 前置条件满足

## 6. real 模式鉴权与数据基线

- [x] 6.1 定义共享基线数据集（测试用户、角色、问卷模板、分配任务）并保证可重复注入
- [x] 6.2 设计并实现 HTTP/UI 共用的 real 模式鉴权初始化策略（会话 Cookie/登录流程）
- [x] 6.3 为关键场景补充 real 模式契约验证，确保 mock/real 在核心断言上保持一致
