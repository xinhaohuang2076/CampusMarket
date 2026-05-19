# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CampusMarket — 校园二手交易平台。Flask 后端 + Vue 3 + Tailwind CSS 前端 + 完整测试体系。课程实训项目，要求覆盖单元测试 / 接口测试 / Selenium UI 自动化 / Locust 性能测试。

## Commands

```bash
# 后端：启动开发服务器
.venv/Scripts/python project/backend/app.py

# 种子数据（1000学生 + 800商品 + 115笔交易）
.venv/Scripts/python project/backend/seed.py

# 诊断工具（一键检查前后端状态）
.venv/Scripts/python tools.py

# 测试总控运行器
.venv/Scripts/python run_tests.py                 # 全部
.venv/Scripts/python run_tests.py --unit          # 仅单元（79项）
.venv/Scripts/python run_tests.py --api           # 仅API（62项，需后端）
.venv/Scripts/python run_tests.py --e2e           # 仅E2E（15项，需前后端）
.venv/Scripts/python run_tests.py --coverage      # 带覆盖率报告

# 前端：开发 / 构建
cd project/frontend && pnpm dev
cd project/frontend && pnpm build

# Locust 性能测试（需后端，6类用户27+种行为）
.venv/Scripts/locust -f tests/performance_tests/locustfile.py
.venv/Scripts/locust -f tests/performance_tests/locustfile.py --headless -u 30 -r 5 --run-time 3m --host=http://127.0.0.1:5000 --html=report.html

# 按标签过滤 Locust 场景
.venv/Scripts/locust -f tests/performance_tests/locustfile.py --tags browse search

# 快速 Selenium 回归（8项，需前后端）
.venv/Scripts/pytest tests/auto_tests/test_edge_flow.py -v
```

## Architecture

### 后端（Flask，分层结构）

```
project/backend/
├── app.py              # 工厂函数 create_app()，注册蓝图 + 初始化 + 文件日志
├── config.py           # Config 类（SECRET_KEY / DB / JWT / 上传限制）
├── seed.py             # 种子数据生成（1001用户 + 800商品 + 交易评价）
├── logs/               # Flask 错误日志（app.log，自动轮转）
├── models/             # SQLAlchemy 模型（user, product, message, favorite, transaction, review）
├── routes/             # 蓝图（auth, product, message, transaction, review）
└── utils/              # 验证函数 + 上传/分页辅助
```

- 认证：JWT（Flask-JWT-Extended），token 存 localStorage，axios 拦截器自动注入
- 数据库：SQLite，ORM 操作
- 密码：werkzeug.security 哈希（generate/check）
- 图片：POST /api/upload → 存 uploads/ → 返回 URL
- 日志：RotatingFileHandler，5MB 轮转，存 `logs/app.log`

**关键模型约定：**
- `Product.status` 状态机：`onsale → reserved → sold | removed`，sold/removed 为终态
- `Review.rating`：1-5 整数，评价后自动更新对方 `User.credit`
- `User.student_id`：10 位数字，22023 开头
- `User.email`：仅限 @qq.com / @163.com
- `condition` 字段：全新/几乎全新/九成新/八成新/七成新/六成新及以下

### 前端（Vue 3 + Composition API + Tailwind CSS v4）

```
project/frontend/src/
├── main.js             # 挂载 App + router + 全局 Vue errorHandler
├── App.vue             # 导航栏 + slide-up 页面过渡 + 用户态管理（自定义事件）
├── style.css           # Tailwind + @theme 自定义色板（coral/warm/slate）+ 字体
├── api/index.js        # axios 封装，JWT 拦截器 + 401 自动跳转登录
├── router/index.js     # Hash 路由 + 懒加载 + meta.requiresAuth 鉴权守卫
├── components/Modal.vue # 通用 confirm/alert 弹窗（Teleport + 键盘事件）
└── views/              # 11 个页面组件
```

**设计系统（style.css @theme）：**
- 主色 coral-500 (#E85D5D)，暖灰 warm-50 背景，深灰 slate-800 文字
- 字体：Outfit（标题）+ DM Sans（正文），Google Fonts 加载
- 全局动画类：`.card-hover`（lift + warm shadow）、`.btn-press`（scale 点击效果）、`.input-fancy`（珊瑚色 focus ring）

**路由表（11 条）：** `/` `/login` `/register` `/product/:id` `/product/new` `/product/:id/edit` `/profile` `/my-products` `/favorites` `/transactions` `/messages`

### 测试

```
tests/
├── unit_tests/                     # 79 项 — 纯逻辑，in-memory SQLite
│   ├── conftest.py                 #   独立 Flask app，不污染种子数据库
│   ├── test_validators.py          #   学号/邮箱/密码/价格/手机/评分/文件格式 边界值
│   ├── test_models.py              #   商品状态机/User模型/分类/成色
│   └── test_admin.py               #   管理员权限装饰器/端点访问控制
├── api_tests/                      # 62 项 — 需后端运行
│   └── test_api_comprehensive.py   #   7模块 × (正向+异常+边界)，含Admin模块
├── auto_tests/                     # 23 项 — 需前后端运行
│   ├── test_edge_flow.py           #   快速回归（8项）
│   └── test_comprehensive_e2e.py   #   完整用户旅程（15项）
└── performance_tests/              # 6类用户，27+种API行为
    └── locustfile.py               #   Browsing / Search / Auth / Seller / Transaction / Admin

run_tests.py                        # 总控运行器，--unit / --api / --e2e / --coverage
tools.py                            # 诊断工具：后端/前端/API一致性 一键检查
```

## Performance Test Scenarios（6 类用户）

```python
# locustfile.py 用户类概览
BrowsingUser          # 游客：列表/搜索/详情/分页边界/分类筛选 — 25%
SearchIntensiveUser   # 深度搜索：组合搜索+逐页翻 — 15%
AuthenticatedUser     # 登录用户：个人信息/商品/收藏/交易/留言 — 25%
ActiveSeller          # 卖家：发布/编辑/下架/上传 — 15%
TransactionUser       # 买家：留言/收藏/交易意向/评价 — 15%
AdminUser             # 管理员：批量查看商品和评价 — 5%
```

预期错误处理：locustfile 中使用 `catch_response=True` 标记 400/404/409 为成功（不计入失败统计）。

## Seed Data

| 数据 | 数量 | 测试账号 |
|------|------|----------|
| 学生 | 1001 | 2202300001~0005 密码 123456 |
| 商品 | 800 | 在售 ~506 件，覆盖 6 分类 |
| 收藏 | ~1500 | admin: 2202300000 / admin123 |
| 留言 | ~650 | 其他学生: 学号=密码 |
| 交易 | 115 | |
| 评价 | 115 | |

## Key API Endpoints（共 23 个）

| 模块 | 端点 |
|------|------|
| Auth | register, login, profile(GET/PUT), password |
| Product | list(GET/search/filter/sort), create, detail, update, remove, mine, upload |
| Favorite | toggle, list |
| Message | list, send, mine + direction=received/sent |
| Transaction | create, update(complete/cancel), list |
| Review | create, user_reviews |
| Meta | categories, conditions, health |

## 已知注意事项

- **Vite HMR 缓存问题**：文件编码损坏或中文乱码时，重启 Vite 开发服务器可清除 HMR 缓存
- **单元测试不污染数据库**：conftest.py 使用独立 in-memory SQLite，不碰 campus_market.db
- **Locust 写数据库**：性能测试的 ActiveSeller 会往数据库写入商品，必要时重新 seed 恢复
- **datetime.utcnow() 弃用警告**：Python 3.13+ 的 DeprecationWarning，不影响功能，后续可改为 `datetime.now(datetime.UTC)`
- **Flask debug 模式**：`app.py` 使用 `debug=True`，代码修改后自动重启。生产环境应关闭

## 设计约束

- 不要改动 `validate_student_id` 和 `validate_email` 的规则（课程要求）
- 前端样式用 Tailwind utility classes + 自定义 @theme，不写独立 CSS 文件
- Modal 组件用于替代全站的 alert/confirm，不要再用原生弹窗
- 所有 API 错误响应格式统一为 `{"error": "描述信息"}`
- 不要在 locustfile 中给商品标题加"-性能测试"后缀（会污染数据库）
