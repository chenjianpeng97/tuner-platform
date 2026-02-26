## ADDED Requirements

### Requirement: OpenAPI 文档 SHALL 成为前端唯一契约源
前端 API 生成流水线 SHALL 使用 `docs/api_doc.json` 作为契约驱动代码生成的唯一真实来源。

#### Scenario: 从仓库契约文件生成 API 客户端
- **WHEN** 开发者执行 API 生成命令
- **THEN** 生成器从仓库读取 `docs/api_doc.json`
- **THEN** 生成产物仅由该文件推导，不依赖在线后端接口

### Requirement: 生成代码 SHALL 可复现且与手写代码隔离
前端 SHALL 将生成的 API 代码与手写业务代码隔离存放，并且在输入不变时重复生成 SHALL 得到稳定产物。

#### Scenario: OpenAPI 输入不变时稳定再生成
- **WHEN** `docs/api_doc.json` 无契约变化
- **THEN** 重跑生成流程不需要手工修改生成文件
- **THEN** 手写 API 封装层保持不变

#### Scenario: 强制执行生成与手写边界
- **WHEN** 组织前端 API 代码目录时
- **THEN** 生成文件存放在专用 generated 目录
- **THEN** 手写集成逻辑存放在 generated 目录之外
