# gdou-jw

广东海洋大学教务系统 CLI 工具

## 定位

本项目是一个**命令行接口（CLI）工具**，专为 AI Agent（如 Hermes Agent、Marvis、OpenClaw 等）设计，用于帮用户查询教务信息：

- 📚 **查课表** - 查看本学期课程安排
- 📝 **查考试** - 查看考试时间和地点
- 📊 **查成绩** - 查看各科成绩和绩点

Agent 可以通过调用 `uv run courses` / `uv run exams` / `uv run grades` 等命令，直接获取用户的教务数据。

## 安装

```bash
# 克隆仓库
git clone <仓库地址>
cd gdou-jw-reverse

# 安装依赖
uv sync
```

## 配置

在项目根目录创建 `.env` 文件：

```env
GDOU_USERNAME=你的学号
GDOU_PASSWORD=你的密码
```

## 用法

### 查课表

```bash
uv run courses --year 2025 --term 1
uv run courses -y 2025 -t 1
```

### 查考试

```bash
uv run exams --year 2025 --term 2
uv run exams -y 2025 -t 2
```

### 查成绩

```bash
uv run grades --year 2025 --term 1
uv run grades -y 2025 -t 1
```

### 参数说明

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--year` | `-y` | `2025` | 学年，如 `2025` 表示 2025-2026 学年 |
| `--term` | `-t` | `1` | 学期：`1` 或 `2` |

## 技术实现

- **登录**：RSA 加密密码 + 滑块验证码自动识别（OpenCV 模板匹配）
- **验证码**：自动识别缺口位置，模拟人类拖动轨迹
- **接口**：逆向正方教务系统 V9.0 的 AJAX 接口

## 项目结构

```
gdou-jw-reverse/
├── .env                  # 账号密码（不提交到git）
├── pyproject.toml        # uv 项目配置
├── src/
│   └── gdou_jw/
│       ├── __init__.py   # 包入口
│       ├── client.py     # 教务客户端（登录+查询）
│       ├── cli.py        # Click 命令行入口
│       ├── captcha.py    # 滑块验证码处理
│       └── crypto.py     # RSA 加密/轨迹加密
```

## 依赖

- Python >= 3.12
- requests
- pycryptodome
- opencv-python
- numpy
- click
- python-dotenv

## 注意事项

- `.env` 文件包含敏感信息，**不要提交到 Git**
- 滑块验证码识别需要 OpenCV，首次安装可能较慢
- 教务系统接口可能变动，如遇问题请提 Issue
