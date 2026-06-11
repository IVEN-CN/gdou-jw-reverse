# 贡献指南

感谢你对 `gdou-jw-reverse` 项目的兴趣！本项目是广东海洋大学正方教务系统的逆向工具，旨在帮助学生和开发者更方便地查询课表、考试和成绩。

## 如何贡献

### 报告问题

如果你发现了 bug 或有新功能建议，请通过 [GitHub Issues](https://github.com/yourusername/gdou-jw-reverse/issues) 提交。

- **Bug 报告**：使用 "Bug Report" 模板，提供复现步骤、期望行为和实际行为
- **功能建议**：使用 "Feature Request" 模板，描述你的使用场景和期望的解决方案
- **学校适配**：如果你想适配其他学校的正方系统，请提供该校的教务系统 URL 和验证码类型

### 提交代码

1. **Fork 仓库** 并克隆到本地
2. **创建分支**：从 `master` 分支创建功能分支
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/bug-description
   ```
3. **编写代码**：遵循现有代码风格，添加必要的注释
4. **测试**：确保你的改动不会破坏现有功能
5. **提交 PR**：使用 PR 模板，描述改动内容和测试情况

### 代码风格

- Python 代码遵循 PEP 8
- 函数和类添加 docstring
- 关键逻辑添加行内注释
- 变量名使用英文，避免拼音

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>(<scope>): <subject>

<body>
```

类型：
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具链

示例：
```
feat(schedule): 支持查询指定周次的课表

- 添加 week 参数到 get_schedule()
- 过滤返回指定周的课程
```

## 安全提醒

⚠️ **永远不要提交包含敏感信息的代码**：
- 学号、密码
- Cookie、Session ID
- 个人课表/成绩数据

这些应该放在 `.env` 文件中，并确保 `.env` 在 `.gitignore` 中。

## 适配新学校

如果你想让本项目支持其他学校的正方系统，欢迎提交 PR！请参考：

1. 阅读 `skills/gdou-jw/SKILL.md` 了解现有实现
2. 分析目标学校的登录流程和 API 端点
3. 在 `src/gdou_jw/` 中添加新的客户端类
4. 更新 CLI 支持新学校
5. 在 PR 中描述该校的特化配置（验证码类型、端点等）

## 社区行为准则

- 尊重他人，保持友善
- 讨论技术问题，不攻击个人
- 接受不同的技术观点
- 帮助新手入门

## 联系方式

- GitHub Issues: [项目 Issues 页面](https://github.com/IVEN-CN/gdou-jw-reverse/issues)
- 安全漏洞报告: `hyf_iven@outlook.com`（标题前缀 `[SECURITY]`）
- 博客: [正方教务系统逆向实战](https://yourblog.com)
