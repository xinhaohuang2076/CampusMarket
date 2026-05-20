# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CampusMarket — 校园二手交易平台。**FastAPI 后端** + Vue 3 + Tailwind CSS 前端 + 完整测试体系。课程实训项目，要求覆盖单元测试 / 接口测试 / Selenium UI 自动化 / Locust 性能测试。

## Commands

```bash
# 后端：开发模式启动（Uvicorn 热重载）
.venv/Scripts/python project/backend/app.py

# 后端：生产模式启动（Uvicorn 多 workers）
ENV=production .venv/Scripts/python project/backend/app.py

# 后端：MySQL 模式
DATABASE_URL="mysql+pymysql://root:root123@127.0.0.1:3306/campus" ENV=production .venv/Scripts/python project/backend/app.py

# 种子数据（1000学生 + 800商品 + 115笔交易）
.venv/Scripts/python project/backend/seed.py

# 诊断工具（一键检查前后端状态）
.venv/Scripts/python tools.py

# 测试总控运行器
.venv/Scripts/python run_tests.py                 # 全部
.venv/Scripts/python run_tests.py --unit          # 仅单元（79项）
.venv/Scripts/python run_tests.py --api           # 仅API（62项，需后端）
.venv/Scripts/python run_tests.py --e2e           # 仅E2E（需前后端）
.venv/Scripts/python run_tests.py --coverage      # 带覆盖率报告

# 直接运行测试
.venv/Scripts/pytest tests/unit_tests/ -v --cov=project/backend --cov-report=term
.venv/Scripts/pytest tests/api_tests/ -v
.venv/Scripts/pytest tests/auto_tests/test_edge_flow.py -v -s    # 8项快速回归
.venv/Scripts/python -c "import sys; sys.path.insert(0, 'tests/auto_tests'); from test_comprehensive_e2e import e2e, tests; e2e.run(tests)"  # 24项完整

# 前端：开发 / 构建
cd project/frontend && pnpm dev
cd project/frontend && pnpm build

# Locust 性能测试（多场景文件）
.venv/Scripts/locust -f tests/performance_tests/run_mixed.py --headless -u 100 -r 10 --run-time 2m --host=http://127.0.0.1:5000 --html=report.html
.venv/Scripts/locust -f tests/performance_tests/run_read.py          # 读密集
.venv/Scripts/locust -f tests/performance_tests/run_write.py         # 写密集
.venv/Scripts/locust -f tests/performance_tests/run_seller.py        # 卖家行为
.venv/Scripts/locust -f tests/performance_tests/run_transaction.py   # 交易流程
```

## Architecture

### 后端（FastAPI，分层结构）

```
project/backend/
├── app.py              # FastAPI 应用，工厂 + CORS + 中间件 + 异常处理
├── config.py           # Config 类（SECRET_KEY / DB / JWT / 上传限制）
├── seed.py             # 种子数据生成（1001用户 + 800商品 + 交易评价）
├── logs/               # 错误日志（app.log，自动轮转）
├── models/
│   ├── __init__.py     # 普通 SQLAlchemy（非 Flask-SQLAlchemy），无 app context 依赖
│   ├── user.py         # 6 个模型继承 Base（declarative_base）
│   ├── product.py
│   ├── message.py
│   ├── favorite.py
│   ├── transaction.py
│   └── review.py
├── routes/             # FastAPI APIRouter（非 Flask Blueprint）
│   ├── __init__.py
│   ├── auth.py         # JWT 注册/登录/个人信息/密码
│   ├── product.py      # CRUD/搜索/筛选/上传/收藏
│   ├── message.py      # 留言列表/发送
│   ├── transaction.py  # 发起/完成/取消交易
│   ├── review.py       # 评价/信用分更新
│   └── admin.py        # 管理后台统计/用户/商品管理
└── utils/
    ├── __init__.py
    ├── auth.py          # JWT 创建 + get_current_user + admin_required 依赖
    └── helpers.py       # 验证器 + 上传 + 分页
```

**关键差异（相比标准 FastAPI 模板）：**
- `db` 是一个 `_DBProxy` 兼容层（代理 `sqlalchemy.Column`/`String`/`Integer` 等），使旧代码的 `db.Column(db.String(...))` 语法在普通 SQLAlchemy 下可用
- `db.session` 是**共享单例**，请求结束后由中间件自动 `rollback()` 清理
- `Base.query` 通过 `_QueryProperty` 描述符提供 `Model.query.filter_by()` 语法
- JWT 用 `python-jose` 而非 `PyJWT` 或 `Flask-JWT-Extended`

**关键模型约定：**
- `Product.status` 状态机：`onsale → reserved → sold | removed`，sold/removed 为终态
- `Review.rating`：1-5 整数，评价后自动更新对方 `User.credit`（>=4 +2, <=2 -2, 其余 +1, 范围 0-200）
- `User.student_id`：10 位数字，22023 开头（正则 `^22023\d{5}$`）
- `User.email`：仅限 @qq.com / @163.com
- `condition` 字段：全新/几乎全新/九成新/八成新/七成新/六成新及以下

### 后端实现细节

- 密码：werkzeug.security 哈希（generate/check）
- 图片：POST /api/upload → FastAPI `UploadFile` → 存 `uploads/` → 返回 `/uploads/{uuid}.{ext}`
- 日志：Python logging + RotatingFileHandler，5MB 轮转
- 中间件：`_DBCleanupMiddleware`（每个请求后自动 rollback session，防止脏数据污染）
- 404/500 异常处理：返回 `JSONResponse(status_code=..., content={"error": "..."})`

### 前端（Vue 3 + Composition API + Tailwind CSS v4）

```
project/frontend/src/
├── main.js             # 挂载 App + router + 全局 Vue errorHandler
├── App.vue             # 导航栏 + slide-up 页面过渡 + 用户态管理（自定义事件）
├── style.css           # Tailwind + @theme 自定义色板（coral/warm/slate）+ 字体
├── api/index.js        # axios 封装，JWT 拦截器 + 401 自动跳转登录
├── router/index.js     # Hash 路由 + 懒加载 + meta.requiresAuth + meta.requiresAdmin 守卫
├── utils/admin.js      # isAdmin() 工具函数
├── components/Modal.vue # 通用 confirm/alert 弹窗（Teleport + 键盘事件）
└── views/              # 12 个页面组件（含 Admin.vue 管理后台）
```

**设计系统：** coral-500 (#E85D5D) 主色，暖灰 warm-50 背景，Outfit + DM Sans 字体。全局动画类：`.card-hover`（lift + shadow）、`.btn-press`（scale）、`.input-fancy`（coral focus ring）。

**路由（12 条）：** `/` `/login` `/register` `/product/:id` `/product/new` `/product/:id/edit` `/profile` `/my-products` `/favorites` `/transactions` `/messages` `/admin`

### 测试

```
tests/
├── unit_tests/                     # 79 项 — 纯逻辑，tempfile SQLite
│   ├── conftest.py                 #   独立 tempfile，不碰种子数据库
│   ├── test_validators.py          #   56项：边界值/等价类/判定表
│   ├── test_models.py              #   15项：状态机/密码生命周期/常量
│   └── test_admin.py               #   8项：管理员权限条件覆盖
├── api_tests/                      # 62 项 — 需后端运行（requests + pytest）
│   └── test_api_comprehensive.py   #   7模块 × (正向+异常+边界)
├── auto_tests/                     # 32 项 — 需前后端运行（Selenium Edge）
│   ├── driver.py                   #   E2ETest 基类（浏览器管理+截图+重试）
│   ├── test_edge_flow.py           #   快速回归 8项
│   └── test_comprehensive_e2e.py   #   完整用户旅程 24项
└── performance_tests/              # 6类用户，27+种API行为
    ├── locustfile.py               #   基类（数据池+用户类+预生成token池）
    ├── run_mixed.py                #   混合场景（全部6类）
    ├── run_read_write.py           #   读写混合
    ├── run_customer_journey.py     #   用户完整旅程
    ├── run_read.py / run_write.py  #   读密集 / 写密集
    ├── run_seller.py / run_transaction.py
    └── run_user.py                 #   用户操作

run_tests.py                        # 总控运行器
tools.py                            # 诊断工具
```

### API 端点（23+6 个）

| 模块 | 端点 |
|------|------|
| Auth | register, login, profile(GET/PUT), password |
| Product | list(search/filter/sort), create, detail, update, remove, mine, upload |
| Favorite | toggle, list |
| Message | list, send, mine(direction) |
| Transaction | create, update(complete/cancel), list |
| Review | create, user_reviews(+avg_rating) |
| Admin | stats, users(list+update), products(list+delete), transactions(list) |
| Meta | categories, conditions, health |

## Design Contracts

- 所有 API 错误响应格式统一为 `{"error": "描述信息"}`（401 除外：`{"msg": "..."}` 来自 HTTPBearer）
- 创建操作返回 `status_code=201`（favorite toggle 除外，返回 200/201 皆可）
- `paginate()` 返回 `{items, total, page, per_page, pages, has_next, has_prev}`
- `admin_required` 是 FastAPI 依赖（不是装饰器），返回 403 + `{"error": "需要管理员权限"}`
- 前端 `api/index.js` 拦截 401 自动跳 `/login`

## 已知注意事项

- **Vite HMR 缓存问题**：长时间运行后可能出现路由参数损坏（如 `product/2:0`），重启 Vite 开发服务器可清除
- **单元测试不污染数据库**：conftest.py 使用独立 tempfile SQLite，不碰 campus_market.db
- **Locust 写数据库**：性能测试的 ActiveSeller 会往数据库写入商品，必要时重新 seed 恢复
- **datetime.utcnow() 弃用警告**：Python 3.13+ 的 DeprecationWarning，不影响功能
- **Docker Desktop** 需要手动启动才能使用 MySQL；单元测试默认使用 SQLite 临时文件
- **共享 Session**：`models/__init__.py` 的 `_shared_session` 全局单例，所有请求共用。若因异常导致 session 脏，后续请求的 `commit()` 会失败。`app.py` 中的 `_DBCleanupMiddleware` 负责每个请求后自动 rollback
- **`/mine` 路由必须在 `/{id}` 之前**注册，否则 FastAPI 会尝试把 `"mine"` 解析为 `int(product_id)` 返回 422

## 设计约束

- 不要改动 `validate_student_id` 和 `validate_email` 的规则（课程要求）
- 前端样式用 Tailwind utility classes + 自定义 @theme，不写独立 CSS 文件
- Modal 组件用于替代全站的 alert/confirm，不要再用原生弹窗
- 不要在 locustfile 中给商品标题加"-性能测试"后缀（会污染数据库）
- E2E 测试不要依赖具体数据值（如商品数量、用户昵称），使用弹性断言
