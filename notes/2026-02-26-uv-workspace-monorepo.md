---
title: 用 uv 在多目录项目中统一 Python 环境（backend + BDD + skills）
date: 2026-02-26 18:43:15
tags:
  - Python
  - uv
  - FastAPI
  - Behave
  - BDD
  - Monorepo
---

## 问题背景

一个仓库里有三类 Python 需求：

1. `backend/` 是 FastAPI 项目，已经有自己的 `pyproject.toml`。
2. 根目录 `features/` 需要跑 Behave（BDD）。
3. `.codex/.github/openspec` 相关脚本未来也会吃 Python 依赖。

如果每处各自维护虚拟环境和锁文件，容易出现版本漂移、CI 不一致、导入路径混乱。

## 目标

- 使用 `uv` 做统一依赖解析。
- 只维护一份根锁文件：`uv.lock`。
- 保持 `backend` 现有项目结构不拆。
- 让 BDD/skills 可以直接导入 backend 包（如 `import app...`）。

## 最终方案

采用 **uv workspace + 根依赖组 + 单一根锁**：

1. 根目录新增 `pyproject.toml`，作为 workspace root。
2. `backend` 作为 workspace member。
3. 根目录维护依赖组：
   - `bdd`：Behave + backend package
   - `skills`：skills 脚本依赖 + backend package
   - `dev`：聚合 `bdd + skills`
4. 锁文件统一在根目录：`uv.lock`。
5. `backend/uv.lock` 退役。

## 关键配置示例

```toml
[project]
name = "tuner-platform-workspace"
version = "0.1.0"
requires-python = ">=3.13,<3.14"
dependencies = []

[tool.uv]
package = false

[tool.uv.workspace]
members = ["backend"]

[tool.uv.sources]
fastapi-clean-example = { workspace = true }

[dependency-groups]
bdd = ["behave>=1.2.6", "fastapi-clean-example"]
skills = ["fastapi-clean-example", "pyyaml>=6.0.2"]
dev = [{ include-group = "bdd" }, { include-group = "skills" }]
```

## 日常命令规范

```bash
# 生成/更新根锁
uv lock

# backend
uv sync --project backend --group dev
uv run --project backend pytest

# BDD
uv sync --group bdd
uv run --group bdd behave features

# skills
uv sync --group skills
uv run --group skills python -c "import app; import yaml; print('skills env ok')"

# 全量安装
uv sync --all-groups --all-packages
```

## 跨目录导入验证

```bash
uv run --group bdd python -c "import app; print(app.__file__)"
```

能打印到 `backend/src/app/__init__.py`，说明 BDD 环境可直接复用 backend 模型。

## CI 拆分建议

三个 job，全部基于根 `uv.lock`：

1. `backend-test`：`uv sync --project backend --group test` + `pytest`
2. `bdd-test`：`uv sync --group bdd` + `behave features`
3. `skills-check`：`uv sync --group skills` + smoke test

## 常见坑

1. `uv sync --group xxx` 会按组切换环境，不在该组内的包可能被卸载，这是正常行为。
2. 统一 Python 主版本（如 3.13）很关键，否则 lock/CI 容易出现平台差异。
3. 迁移后应明确“根锁是唯一真相”，不要再维护多个 lock。

## 结论

对于这种 “后端应用 + BDD 自动化 + 脚本工具” 的多场景仓库，`uv workspace + 单一根锁` 是兼顾可维护性和可复现性的方案，且对现有 `backend` 入侵最小。
