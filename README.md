# tuner-platform
软件研发管理平台

## 模板
- [前端](https://github.com/satnaing/shadcn-admin.git)
- [后端](https://github.com/ivan-borovets/fastapi-clean-example.git)

## 研发规范
- `openspec`：SDD（规范驱动开发）文件
- `features`：BDD（行为驱动开发）的场景描述和自动化测试步骤

## 项目结构
```text
tuner-platform/
├── backend/                       # 后端代码
├── features/                      # 行为驱动开发(BDD)文件
├── frontend/                      # 前端代码
├── openspec/                      # 规范驱动开发（SDD）文件
│   ├── changes/
│   │   └── archive/
│   ├── specs/
│   └── config.yaml
├── .github/
├── .codex/
├── LICENSE
└── README.md
```

## Python 环境管理（uv workspace）

### 目标
- 单一根锁文件：`uv.lock`
- `backend` 继续保留自己的 `pyproject.toml`
- `features`（BDD）和未来 skills Python 脚本共享同一套依赖解析

### 一次性准备
```bash
uv python install 3.13
uv lock
```

### 常用命令
```bash
# 后端（使用 backend 项目）
uv sync --project backend --group dev
uv run --project backend pytest

# BDD
uv sync --group bdd
uv run --group bdd behave features

# Skills 脚本
uv sync --group skills
uv run --group skills python -c "import app; import yaml; print('skills env ok')"

# 本地全量安装
uv sync --all-groups --all-packages
```

### 跨目录导入验证
```bash
uv run --group bdd python -c "import app; print(app.__file__)"
```
