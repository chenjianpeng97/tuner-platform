# SDD工作流

# 目标
建立以SDD逐步迭代的研发流程

# 迭代步骤

1. 编写origin_requirements/下描述用户需求
2. [接口实现]需求和设计确定后，先计划需要哪些http接口
3. [接口实现]实现backend/presentation/http的fastapi路由定义和RequestPydantic定义,接口留下@inject注册执行函数的位置
4. [接口实现]实现application层的执行函数返回Response模型
5. [接口文档编排测试](../.codex/skills/http-stage-behave-testing/)实现接口编排的BDD测试，验证接口编排可行，Response和Request定义合理
6. [接口文档]通过fastapi自动生成接口文档到根目录docs/api_doc.md
7. [前端实现]前端通过工具将openapi文档转换成前端接口调用代码，编写前端界面
8. [前端实现]前端编写mock.js模拟接口数据，验证前端界面设计合理
9. [前端实现]风格统一的实现新的页面或组件，自有组件应在关键地方加data-testid
10. [前端测试]以mock模式运行前端,并且实现前端的BDD测试(stage=ui),验证前端页面设计对需求的可行性
11. [后端实现]以TDD的形式，编写unit测试(../backend/tests/app/unit/各层)测试
12. [后端实现]以TDD形式，实现各层domain,application,presentation,infrastructure的代码
13. [集成测试]前后端都完成时，运行集成测试，前后端连接之后运行bdd的ui stage测试，验证前后端连接的正确性和需求的满足程度
