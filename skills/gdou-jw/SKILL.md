---
name: gdou-jw
description: "Use when working on the gdou-jw-reverse project. Project structure, CLI commands, and API endpoints for Guangdong Ocean University教务系统."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [gdou, jwglxt, project-local]
    related_skills: []
---

# 广东海洋大学教务系统 API

## 项目结构

```
gdou-jw-reverse/
├── src/gdou_jw/
│   ├── __init__.py      # 包导出
│   ├── client.py        # GdouJwClient: login + query APIs
│   ├── crypto.py        # RSA + ef() base64
│   ├── captcha.py       # OpenCV 滑块识别
│   └── cli.py           # Click 命令行入口
├── .env                 # 账号密码（不提交 git）
└── pyproject.toml       # uv 配置
```

## 快速命令

```bash
cd E:/code/code_python/gdou-jw-reverse

# 课表
uv run courses

# 考试
uv run exams

# 成绩
uv run grades
```

## API 端点速查表

| 功能 | 端点 | 方法 | 关键参数 |
|------|------|------|----------|
| 登录页 | `/xtgl/login_slogin.html` | GET | 提取 `csrftoken` |
| RSA公钥 | `/xtgl/login_getPublicKey.html` | POST | 返回 `modulus`, `exponent` |
| 刷新验证码 | `/zfcaptchaLogin?type=refresh` | GET | 返回 `si`, `mi`, `imtk`, `t` |
| 验证码图片 | `/zfcaptchaLogin?type=image&id={si/mi}` | GET | 下载背景图/拼图块 |
| 验证验证码 | `/zfcaptchaLogin` | POST | `type=verify`, `rtk`, `mt` |
| 提交登录 | `/xtgl/login_slogin.html` | POST | `yhm`, `mm`, `csrftoken` |
| **课表查询** | `/kbcx/xskbcx_cxXsgrkb.html` | POST | `xnm`, `xqm`, `kzlx=ck` |
| **考试查询** | `/kwgl/kscx_cxXsksxxIndex.html?doType=query` | POST | `xnm`, `xqm` |
| **成绩查询** | `/cjcx/cjcx_cxDgXscj.html?doType=query` | POST | `xnm`, `xqm` |

### 参数说明

- `xnm`: 学年（如 `2025`）
- `xqm`: 学期编码，`3`=第一学期，`12`=第二学期
- `yhm`: 学号
- `mm`: RSA 加密后的密码

## 关键实现细节

### RTK 动态提取
```python
js_url = f"{BASE_URL}/zfcaptchaLogin?type=resource&name=zfdun_captcha.js"
rtk = re.search(r"rtk:'([^']+)'", js_text).group(1)
```

### 滑块坐标（绝对值）
```python
# 使用 clientX/clientY 绝对坐标，不是相对位移
track = [{"x": 500 + i, "y": 300, "t": timestamp}]
```

### 拼图块裁剪
```python
alpha = slider[:, :, 3]
non_zero = np.where(alpha > 0)
# 用 non_zero 边界裁剪
```

## 环境配置

`.env` 文件：
```
GDOU_USERNAME=202311427408
GDOU_PASSWORD=your_password
```
