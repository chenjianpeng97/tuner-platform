# User HTTP-stage 标准示例模式

## 目标
用 `features/user.feature` 与 `features/http_steps/step_user.py` 作为标准样例，验证控制器层编排：
- 路由可达；
- 请求模型可反序列化；
- 异常映射到 HTTP 状态码正确；
- 响应契约稳定；
- interactor/handler dispatch 被正确触发。

## 推荐结构
- feature 使用 `Feature -> Rule -> Scenario`，每条规则覆盖 1 个核心约束。
- Given 只记录上下文（用户状态、ID、当前用户名），不发 HTTP。
- When 先配置 mock（`return_value`/`side_effect`），再发真实 HTTP 请求。
- Then 同时断言状态码、错误/响应体关键字段、以及对应 mock 的调用。

## 设计原则
- 用最小但真实的用户语义覆盖核心控制器路径（创建、登录、激活、停用）。
- request body 由 presentation 层 request model 生成（如 `model_dump(mode="json")`）。
- 对失败路径断言 domain/infrastructure 常量，避免“只看状态码”的假阳性。
- 对成功路径至少断言一次 `*.execute` 被调用到正确 interactor。

## 标准场景（user.feature）
1. Given 已存在用户名为 `alice` 的用户。
2. When 再次创建 `alice`。
3. Then 返回 409，错误体包含“already exists”。
4. And 断言 `create_user.execute` 被调用。

5. Given 已停用用户名为 `bob` 的用户。
6. When 用户登录。
7. Then 返回 401，错误体包含 `AUTH_ACCOUNT_INACTIVE`。
8. And 断言 `log_in.execute` 被调用。

9. Given 已停用用户名为 `carol` 的用户。
10. When 管理员激活该用户。
11. Then 返回 204。
12. And 断言 `activate_user.execute` 被调用。

13. Given 启用状态用户名为 `dave` 的用户。
14. When 管理员停用该用户。
15. Then 返回 204。
16. And 断言 `deactivate_user.execute` 被调用。

## 执行建议
- 本地改动控制器后先跑 `user.feature` 的相关场景。
- 提交前跑 user 场景 + 当前需求相关 feature。

可选命令约定：
- `behave --stage http features/user.feature`
