---
title: 前端 i18n 开发指南（EN/ZH）
date: 2026-03-05 15:25:00
tags:
  - Frontend
  - i18n
  - React
  - i18next
  - 开发规范
---

## 背景与目标

项目已接入 `i18next + react-i18next`，当前支持 `en`/`zh` 双语，默认语言为 `en`。
本指南用于帮助前端同学在新增/修改页面时，按统一方式完成国际化，不再引入硬编码文案。

## 一、核心约定（先看）

### 1) 语言与默认值

- 支持语言：`en`、`zh`
- 默认语言：`en`
- 用户选择会持久化到 `localStorage`（键：`app.locale`）

### 2) 命名空间（namespace）

- `common.*`：公共壳层/通用组件文案（导航、搜索、主题、账号菜单等）
- `business.*`：业务页面文案（surveys/users/account 等）

### 3) key 命名规则

推荐层级：`<namespace>.<module>.<section>.<name>`

示例：

- `common.profile.signOut`
- `common.search.placeholder`
- `business.users.columns.username`
- `business.surveys.templates.status.draft`

避免：

- 无语义短 key（如 `title1`、`btnText`）
- 中英文混合 key
- 在组件里直接写文案字符串

## 二、你会用到的文件

- i18n 启动与配置：[frontend/src/i18n/index.ts](frontend/src/i18n/index.ts)
- 语言常量：[frontend/src/i18n/constants.ts](frontend/src/i18n/constants.ts)
- 资源文件：
  - [frontend/src/i18n/resources/en/common.ts](frontend/src/i18n/resources/en/common.ts)
  - [frontend/src/i18n/resources/zh/common.ts](frontend/src/i18n/resources/zh/common.ts)
  - [frontend/src/i18n/resources/en/business.ts](frontend/src/i18n/resources/en/business.ts)
  - [frontend/src/i18n/resources/zh/business.ts](frontend/src/i18n/resources/zh/business.ts)
- 语言切换组件：[frontend/src/components/language-switch.tsx](frontend/src/components/language-switch.tsx)

## 三、日常开发怎么做

### 场景 A：新增公共组件文案

1. 在 `common` 的 `en/zh` 文件里新增 key。
2. 在组件中使用：

```tsx
import { useTranslation } from 'react-i18next'

const { t } = useTranslation('common')

return <span>{t('search.placeholder')}</span>
```

### 场景 B：新增业务页面文案

1. 在 `business` 的 `en/zh` 文件里新增对应模块 key（如 `users.*`）。
2. 页面中使用：

```tsx
const { t } = useTranslation('business')
return <h2>{t('users.title')}</h2>
```

3. 如果同一组件既有 `common` 又有 `business` 文案：

```tsx
const { t } = useTranslation(['business', 'common'])

// business 默认可直接写
const title = t('users.title')

// common 建议显式前缀，避免歧义
const aria = t('common:selection.selectAll')
```

### 场景 C：表格/状态/筛选项文案

建议统一放在模块下：

- 列名：`*.columns.*`
- 状态：`*.status.*`
- 操作：`*.actions.*`
- 筛选 placeholder：`*.filterPlaceholder`

这样可以避免列表页 key 分散。

## 四、语言切换组件如何复用

已有 `LanguageSwitch`：

- 默认模式（按钮 + EN/ZH）：`<LanguageSwitch />`
- 紧凑模式（仅图标）：`<LanguageSwitch compact />`

建议放在全局壳层（已在 profile dropdown 中接入），业务页面通常不需要重复放置。

## 五、校验与自测清单

开发完成后至少检查：

1. `en` 与 `zh` 都补了 key（不允许单边缺失）。
2. 默认首次访问是英文。
3. 切换到中文后刷新页面，语言保持为中文。
4. 切回英文后页面文案同步更新。
5. 列表空态/加载态/按钮/tooltip/aria-label 是否都已国际化。

建议命令：

```bash
cd frontend
pnpm exec eslint src
pnpm run build
```

## 六、常见坑

1. **只改了英文没改中文**
   - 现象：中文下回退到英文或显示 key。

2. **命名空间用错**
   - 例如把业务文案放到 `common`，后续难维护。

3. **在 `useMemo` 列定义里忘记依赖 `t`**
   - 语言切换后列名不更新。

4. **把 key 当文案随意改名**
   - 会导致多个页面一起失效；改名前先全局检索。

5. **硬编码 toast/弹窗文案**
   - 这些也属于用户可见文案，必须走 `t()`。

## 七、提交流程建议

1. 先提交资源文件变更（`i18n/resources`）。
2. 再提交组件/页面替换文案。
3. 最后提交校验修复（lint/build）。
4. PR 描述里附上 `en/zh` 页面截图各一组（核心页面）。

---

如果后续要扩展第三语言（如 `ja`），直接沿用当前结构新增 `resources/ja/common.ts` 和 `resources/ja/business.ts`，并在 `i18n/index.ts` 注册即可。
