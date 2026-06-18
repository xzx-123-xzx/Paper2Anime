# Paper2Anime - 文档转动画短视频平台

> 一站式文档转动画视频平台，让文字内容自动变成精彩动画

## 🌟 项目背景

在内容创作领域，将文档转换为视频是一个耗时且专业的工作流程。创作者需要：
1. 理解文档内容并撰写剧本
2. 设计分镜脚本
3. 创建角色和场景
4. 制作动画视频
5. 剪辑合成

**Paper2Anime** 旨在通过 AI 技术自动化这一流程，用户只需上传文档，系统自动完成从剧本生成到视频合成的全流程。

## 📐 项目架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Paper2Anime 平台                           │
├─────────────────────────────────────────────────────────────────────┤
│  Frontend (React + TypeScript + Vite)                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ 首页     │ │ 上传页   │ │ 项目页   │ │ 编辑器   │ │ 设置页   │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │
│       │            │            │            │            │       │
│       └────────────┼────────────┼────────────┼────────────┘       │
│                    ▼            ▼            ▼                    │
├─────────────────────────────────────────────────────────────────────┤
│  Backend (FastAPI + LangGraph)                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    API Gateway                             │   │
│  ├───────────────────┬───────────────────┬───────────────────┤   │
│  │  Documents API    │  Projects API     │  Workflows API    │   │
│  ├───────────────────┼───────────────────┼───────────────────┤   │
│  │              LangGraph Workflow Engine                   │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │   │
│  │  │ Parser  │→│Script   │→│Board    │→│Character│         │   │
│  │  │         │ │Generator│ │Generator│ │Designer │         │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └────┬────┘         │   │
│  │                                            │              │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────┴────┐         │   │
│  │  │Quality  │←│Video    │←│Video    │←│Image    │         │   │
│  │  │ Check   │ │ Editor  │ │Generator│ │Generator│         │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘         │   │
│  └─────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────┤
│  AI Services                                                      │
│  ┌───────────────────┐ ┌───────────────────┐                     │
│  │   DeepSeek LLM    │ │    MinMax AI      │                     │
│  │  (剧本/分镜)      │ │ (文生图/文生视频)  │                     │
│  └───────────────────┘ └───────────────────┘                     │
├─────────────────────────────────────────────────────────────────────┤
│  Infrastructure                                                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                │
│  │  MySQL  │ │  Redis  │ │ MinIO   │ │ Celery  │                │
│  │         │ │         │ │         │ │ Worker  │                │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘                │
└─────────────────────────────────────────────────────────────────────┘
```

### LangGraph 工作流节点

| 节点 | 职责 | 说明 |
|------|------|------|
| **DocumentParser** | 文档解析 | 支持 TXT、DOCX、PDF |
| **ScriptGenerator** | 剧本生成 | 基于 DeepSeek 生成三幕式剧本 |
| **StoryboardGenerator** | 分镜生成 | 生成镜头脚本 |
| **CharacterDesigner** | 角色设计 | 提取并设计角色外观 |
| **ImageGenerator** | 图片生成 | 角色四视图（MinMax） |
| **VideoGenerator** | 视频生成 | 逐镜头生成视频（MinMax） |
| **VideoEditor** | 视频剪辑 | FFmpeg 合成、转场、字幕 |
| **QualityCheck** | 质量检查 | 视频质量评分与重试 |

### 文件目录结构

```
Paper2Anime/
├── backend/                          # 后端服务
│   ├── app/
│   │   ├── api/v1/                   # API 路由
│   │   ├── core/                     # 核心配置
│   │   ├── crud/                     # 数据库操作
│   │   ├── graph/                    # LangGraph 工作流
│   │   │   ├── nodes/                # 工作流节点
│   │   │   └── edges/                # 路由决策
│   │   ├── models/                   # 数据模型（ORM + Pydantic）
│   │   ├── services/                 # 业务服务
│   │   ├── tasks/                    # Celery 异步任务
│   │   ├── storage/                  # 存储抽象层
│   │   └── main.py                   # FastAPI 入口
│   └── requirements.txt
├── frontend/                         # 前端服务
│   ├── src/
│   │   ├── api/                      # API 客户端
│   │   ├── components/               # UI 组件
│   │   ├── pages/                    # 页面组件
│   │   ├── stores/                   # 状态管理
│   │   └── lib/                      # 工具函数
│   └── package.json
├── common/                           # 公共模块
│   ├── config.py                     # 配置管理
│   ├── llm.py                        # LLM 封装
│   ├── logger.py                     # 日志工具
│   └── path_utils.py                 # 路径工具
├── docker/                           # Docker 配置
│   ├── docker-compose.yml
│   └── nginx/
├── docs/                             # 项目文档
│   └── architecture.md
└── .env.example                      # 环境变量示例
```

## 🛠️ 技术栈

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **FastAPI** | 0.115+ | Web 框架 |
| **LangGraph** | 0.2+ | AI 工作流编排 |
| **LangChain** | 0.3+ | LLM 封装 |
| **SQLAlchemy** | 2.0+ | ORM |
| **Celery** | 5.4+ | 异步任务队列 |
| **Redis** | 7.0+ | 缓存与队列 |
| **MySQL** | 8.0+ | 主数据库 |
| **FFmpeg** | 6.0+ | 视频处理 |
| **DeepSeek** | - | LLM API |
| **MinMax** | - | 文生图/视频 API |

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| **React** | 18+ | UI 框架 |
| **TypeScript** | 5.5+ | 类型安全 |
| **Vite** | 5.4+ | 构建工具 |
| **Tailwind CSS** | 3.4+ | 样式框架 |
| **TanStack Query** | 5.51+ | 数据获取 |
| **Zustand** | 4.5+ | 状态管理 |
| **Lucide React** | 0.400+ | 图标库 |
| **Radix UI** | - | 组件库 |

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose（推荐）
- DeepSeek API Key
- MinMax API Key

### 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的 API Key：

```bash
# DeepSeek LLM
MODEL_API_KEY=your-deepseek-api-key

# MinMax 文生图/视频
MINMAX_IMAGE_API_KEY=your-minmax-image-key
MINMAX_VIDEO_API_KEY=your-minmax-video-key
```

### 使用 Docker Compose 启动（推荐）

```bash
# 启动所有服务
docker-compose -f docker/docker-compose.yml up -d

# 查看日志
docker-compose -f docker/docker-compose.yml logs -f

# 停止服务
docker-compose -f docker/docker-compose.yml down
```

### 本地开发模式

#### 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### 启动前端

```bash
cd frontend
npm install
npm run dev
```

#### 启动 Celery Worker

```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4
```

### 访问应用

- **前端**: http://localhost:5173
- **后端 API**: http://localhost:8000/api/v1
- **后端文档**: http://localhost:8000/docs
- **MinIO 控制台**: http://localhost:9001

## 🔧 核心功能实现

### 1. 文档解析

支持三种文档格式的解析：

```python
# backend/app/services/document_parser.py
class DocumentParser:
    def parse(self, file_path: str) -> Dict[str, Any]:
        ext = os.path.splitext(file_path)[-1].lower()
        if ext == ".pdf":
            return self._parse_pdf(file_path)
        elif ext == ".docx":
            return self._parse_docx(file_path)
        elif ext == ".txt":
            return self._parse_txt(file_path)
```

### 2. LangGraph 工作流编排

工作流通过 StateGraph 定义，节点按顺序执行：

```python
# backend/app/graph/workflow.py
def create_workflow():
    workflow = StateGraph(WorkflowState)
    
    workflow.add_node("document_parser", document_parser_node)
    workflow.add_node("script_generator", script_generator_node)
    workflow.add_node("storyboard_generator", storyboard_generator_node)
    workflow.add_node("character_designer", character_designer_node)
    workflow.add_node("image_generator", image_generator_node)
    workflow.add_node("video_generator", video_generator_node)
    workflow.add_node("video_editor", video_editor_node)
    workflow.add_node("quality_check", quality_check_node)
    
    workflow.set_entry_point("document_parser")
    workflow.add_edge("document_parser", "script_generator")
    # ... 连接其他节点
    workflow.add_edge("quality_check", END)
    
    return workflow
```

### 3. AI 服务集成

使用 DeepSeek 生成剧本和分镜：

```python
# backend/app/graph/nodes/script_generator_node.py
def script_generator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    prompt = SCRIPT_GENERATION_PROMPT.format(content=raw_document)
    response = my_llm.invoke(prompt)
    state["script"] = response.content
    return state
```

### 4. 视频处理

使用 FFmpeg 进行视频合成：

```python
# backend/app/services/ffmpeg_service.py
class FFmpegService:
    def merge_videos(self, video_paths: List[str], output_path: str):
        clips = [ffmpeg.input(path) for path in video_paths]
        concat = ffmpeg.concat(*clips, v=1, a=1)
        output = concat.output(output_path, vcodec='libx264', acodec='aac')
        output.run()
```

### 5. 实时进度推送

通过 WebSocket 推送进度：

```python
# backend/app/api/v1/websocket.py
@router.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    await manager.connect(websocket, project_id)
    while True:
        data = await websocket.receive_text()
        # 处理消息并推送进度
```

## 📡 API 接口

### 文档 API

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/documents/upload` | 上传文档 |
| GET | `/api/v1/documents/{id}` | 获取文档详情 |
| POST | `/api/v1/documents/{id}/parse` | 解析文档 |

### 项目 API

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/projects/` | 创建项目 |
| GET | `/api/v1/projects/` | 获取项目列表 |
| GET | `/api/v1/projects/{id}` | 获取项目详情 |
| PATCH | `/api/v1/projects/{id}` | 更新项目 |
| DELETE | `/api/v1/projects/{id}` | 删除项目 |

### 工作流 API

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/tasks/workflows/start` | 启动工作流 |
| GET | `/api/v1/tasks/workflows/{id}/status` | 获取工作流状态 |
| POST | `/api/v1/tasks/workflows/{id}/cancel` | 取消工作流 |

### WebSocket

| 路径 | 描述 |
|------|------|
| `ws://host:port/ws/ws/{project_id}` | 实时进度推送 |

## 📈 性能优化

### 已实现的优化

1. **异步任务处理** - 使用 Celery + Redis 异步执行耗时任务
2. **批量处理** - 角色图片和视频片段并行生成
3. **本地存储** - 支持本地文件系统和 S3/MinIO 对象存储
4. **错误重试** - 工作流节点支持自动重试机制

### 待优化项

| 优化项 | 描述 | 优先级 |
|--------|------|--------|
| **角色一致性** | 使用 LoRA 微调保持角色外观一致 | 高 |
| **成本控制** | 相似镜头合并、降级策略 | 高 |
| **缓存机制** | 缓存已生成的角色和场景 | 中 |
| **分布式处理** | 多 Worker 节点水平扩展 | 中 |
| **监控告警** | Prometheus + Grafana 监控 | 中 |
| **CDN 加速** | 视频分发加速 | 低 |

## 🔒 安全注意事项

1. **API Key 保护** - 使用环境变量存储敏感信息
2. **文件上传限制** - 限制文件大小和类型
3. **输入验证** - 使用 Pydantic 验证所有输入
4. **CORS 配置** - 限制允许的来源
5. **日志脱敏** - 避免记录敏感信息

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至：support@paper2anime.com

---

**Paper2Anime** - 让文档动起来！ 🎬
