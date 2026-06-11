# 分支保护规则

## master 分支保护

### 必需规则

| 规则 | 配置 |
|------|------|
| **Require pull request reviews** | ✅ 启用，至少 1 个 approving review |
| **Dismiss stale reviews** | ✅ 启用，新提交后重置审查 |
| **Require review from CODEOWNERS** | ✅ 启用 |
| **Require status checks** | ✅ 启用，CI 通过后方可合并 |
| **Require branches to be up to date** | ✅ 启用 |
| **Require signed commits** | ❌ 可选（建议启用） |
| **Require linear history** | ❌ 可选 |
| **Include administrators** | ✅ 启用，管理员也需遵守 |
| **Restrict pushes** | ✅ 仅允许 PR 合并 |

### 禁止直接推送

- 禁止直接向 `master` 分支推送代码
- 所有改动必须通过 Pull Request
- PR 必须通过审查和 CI 检查

## 开发流程

```
master
  │
  ├── feature/xxx  ──→ PR ──→ Review ──→ Merge
  │
  ├── fix/xxx      ──→ PR ──→ Review ──→ Merge
  │
  └── school/xxx   ──→ PR ──→ Review ──→ Merge
```

## 分支命名规范

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feature/` | 新功能 | `feature/weekly-schedule` |
| `fix/` | Bug 修复 | `fix/login-timeout` |
| `docs/` | 文档更新 | `docs/api-examples` |
| `refactor/` | 代码重构 | `refactor/client-class` |
| `school/` | 学校适配 | `school/gdut` |
| `chore/` | 工具链/构建 | `chore/update-deps` |

## CODEOWNERS

```
# 全局默认审查者
* @yourusername

# 核心代码
/src/ @yourusername

# 文档
/docs/ @yourusername
/*.md @yourusername

# 学校适配（新学校适配需要额外审查）
/src/gdou_jw/schools/ @yourusername
```

## 合并策略

- **Squash and merge**：功能分支 → 单条 commit
- **Rebase and merge**：保持线性历史（可选）
- **禁止 Create a merge commit**

## 紧急修复流程

如果 `master` 有严重 bug 需要热修复：

1. 从 `master` 创建 `hotfix/xxx` 分支
2. 修复并提交 PR
3. 优先审查和合并
4. 合并后立即打 tag
