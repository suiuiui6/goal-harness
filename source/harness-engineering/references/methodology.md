# harness-engineering 7 层方法论详解

> 本文档是 `SKILL.md` 的补充参考，提供每层的详细操作指南、真实案例和检查清单。
> 案例来源：会话 `eb2a0fa2-3d94-4954-b673-b733155b548c`（多模态 RAG 知识图谱问答系统搭建）

---

## 目录

1. [Layer 0: 能力边界摸底](#layer-0-能力边界摸底)
2. [Layer 1: 核心组件逐一 MVP 实测](#layer-1-核心组件逐一-mvp-实测)
3. [Layer 2: 集成拓扑设计 + 桥接管道](#layer-2-集成拓扑设计--桥接管道)
4. [Layer 3: 外部工具集成 + 技术架构设计](#layer-3-外部工具集成--技术架构设计)
5. [Layer 4: 产品/架构蓝图](#layer-4-产品架构蓝图)
6. [Layer 5: 项目开发规范确立](#layer-5-项目开发规范确立)
7. [Layer 6: 前后端施工与联调](#layer-6-前后端施工与联调)
8. [何时退出本方法论](#何时退出本方法论)
9. [回退机制实战](#回退机制实战)
10. [反模式：常见错误](#反模式常见错误)
11. [检查清单汇总](#检查清单汇总)

---

## Layer 0: 能力边界摸底

### 操作步骤

1. 获取每个候选组件的源码（git clone / 下载 zip）
2. 通读核心模块，重点关注：
   - `__init__.py` 或主入口的公开 API 列表
   - 输入数据类/schema 定义
   - 输出数据类/schema 定义
   - `pyproject.toml` / `requirements.txt` 的依赖列表（判断是否引入了文档解析、数据库、向量库等）
   - Provider/factory 模式（判断支持的模型类型）
3. 使用 Grep 搜索排除项：搜索 `pdf|docx|embedding|chromadb|neo4j|elasticsearch` 等关键词，确认组件不包含这些能力
4. 将结论写入项目 Memory

### 真实案例

会话 eb2a0fa2 中，Layer 0 的结论直接决定了后续所有架构决策：

```
LangExtract 能力边界：
✅ 支持：纯文本 → 结构化实体抽取（通过 LLM）
✅ 支持：多 Provider（Gemini / OpenAI / Ollama）
❌ 不支持：PDF/DOCX 文档解析
❌ 不支持：Embedding 向量化
❌ 不支持：知识图谱索引与检索
❌ 不支持：数据库存储
```

这个结论意味着：必须引入 MinerU 做文档解析层，且需要自行构建 KG 存储和检索层。

### 检查清单

- [ ] 能一句话说清楚每个候选组件的核心能力
- [ ] 能列出每个组件**显式不支持**的能力（同样重要）
- [ ] 结论已写入项目 Memory
- [ ] Memory 条目包含文件路径、关键函数、依赖列表的引用

### 回退触发

若 Memory 条目模糊（"大概支持 XX"、"应该可以"），说明源码阅读不到位，重做 Layer 0。

---

## Layer 1: 核心组件逐一 MVP 实测

### 操作步骤（每个组件重复执行）

1. 创建独立目录（如 `<component>-mvp/`）
2. 初始化独立隔离环境（按技术栈选择，见 [Layer 5 技术栈映射表](#layer-5-项目开发规范确立)）：
   - Python：`uv venv .venv --python 3.12`
   - Node.js：`pnpm init` + `.nvmrc`
   - Go：`go mod init <component>`
   - Java：`mvn archetype:generate` 或 Gradle init
   - Rust：`cargo new <component>`
3. 安装最小依赖（只安装 MVP 必需的）
4. 配置 `.env`（API Key/Token + 关键参数）
5. 创建 `.env.example` 模板（可提交到 git）
6. 配置 `.gitignore`（排除隔离环境产物：`.venv/` / `node_modules/` / `target/` 等，以及 `.env`、`output/`）
7. 创建 `CLAUDE.md`（记录环境激活方式、运行命令）
8. 准备最小测试数据（如一个 sample.pdf）
9. 编写 MVP 脚本（按语言选 `run_mvp.py` / `mvp.ts` / `main.go` 等），只验证核心输入→输出链路
10. 实际运行测试
11. 将实测结果（输出文件）保留作为证据
12. 基于实测结果生成该组件的规范文档

### MVP "越小越好" 的操作定义

- 测试样本：1 份典型输入即可，不要 10 份
- 代码行数：能跑通核心链路即停手，目标 <100 行
- 功能覆盖：仅覆盖项目实际会用到的 API/参数，不做全功能验证
- 时间预算：单组件 MVP 控制在 1-2 个工作日内

### 真实案例：MinerU MVP（7 轮迭代）

- 第 1 轮：调研 MinerU 支持的输入/输出格式
- 第 2 轮：梳理 API Key 配置需求
- 第 3 轮：生成 `MinerU-API-Specification.md`（输入格式、输出文件结构、字段说明）
- 第 4-7 轮：本地实际调用 MinerU 云端 API，根据实测结果修正规范文档

最终产出 `MinerU-API-Specification.md` 和 `MinerU_MVP测试配置指南.md_v1.0.md`。

### 真实案例：LangExtract MVP

1. 在 `langextract/` 下使用 `uv` 创建独立 `.venv`
2. 通过 OpenAI Provider 接入 DeepSeek v4 pro
3. 验证 `lx.extract()` 的输入输出
4. 生成 `LangExtract-Pipeline-Specification.md`

**关键点**：LangExtract 和 MinerU 的虚拟环境完全独立（63 个包 vs 10 个包），互不干扰。

### 检查清单（对每个组件重复）

- [ ] 虚拟环境独立（不与其他组件共享）
- [ ] `.env` 已加入 `.gitignore`
- [ ] 有 `.env.example` 模板
- [ ] CLAUDE.md 包含环境激活命令
- [ ] MVP 脚本可独立运行
- [ ] 实测输出文件已保留
- [ ] 规范文档全部字段有实测数据支撑
- [ ] 没有试图让任何两个组件通信（那是 Layer 2 的事）
- [ ] 所有组件的规范文档格式保持一致

### 回退触发

若某组件实测发现根本不可用（API 不稳定、功能缺失、性能不达标），回退到 Layer 0 重新评估并考虑替换方案。

---

## Layer 2: 集成拓扑设计 + 桥接管道

### 2a. 集成拓扑设计

1. 列出所有组件及其规范文档路径
2. 画出组件依赖图（谁的输出是谁的输入，数据流方向）
3. 确定桥接顺序（按依赖关系，从数据源到最终消费者）
4. 生成**集成拓扑规范文档**：组件依赖图、数据流图、每条边的格式转换规则

### 2b. 逐段桥接实现

按拓扑顺序，每条边依次实现：

1. 将上游组件规范文档作为约束（只读）
2. 定义该段的输入/输出 schema 转换规则
3. 编写桥接代码，端到端验证该段正确性
4. 验证通过后再进行下一段

### 真实案例：6 阶段 Bridge Pipeline

User 提示：

> "请严格参照以下三个规范文档: MinerU_MVP测试配置指南.md_v1.0.md, MinerU-API-Specification.md, LangExtract-Pipeline-Specification.md"

实际 Pipeline 的 6 个 Stage：
1. PDF Ingestion（MinerU API）
2. Content Extraction（从 MinerU 输出提取 markdown）
3. Text Segmentation（按 section 分段）
4. Entity Extraction（LangExtract）
5. Position Mapping（字符位置 → 页面/bbox）
6. KG Construction（entity → node + edge）

产物：`bridge-pipeline-specification-v1.0.md` + `pipeline.py` + `bridge.py` + `kg_builder.py`

### 检查清单

- [ ] 集成拓扑规范文档显式引用所有上游组件规范
- [ ] 每个 Pipeline Stage 的输入/输出 schema 有明确定义
- [ ] Pipeline 有 `--cached` 模式（跳过上游调试下游）
- [ ] 端到端测试链路可追溯
- [ ] 逐段验证（不要一次性写完所有桥接再测试）

### 回退触发

若某段桥接无法实现（格式不兼容、性能不达标、上游字段缺失），回退到 Layer 1 修正对应组件的规范文档。

---

## Layer 3: 外部工具集成 + 技术架构设计

### 3a. 外部工具集成验证（可选）

**何时执行**：项目需要接入外部框架/工具（LangChain、LlamaIndex、特定 MCP 服务）

**何时跳过**：项目使用纯本地工具链（仅依赖 Layer 1 已实测的组件）

**操作步骤**：
1. 安装外部工具的 MCP 或 SDK
2. 进行连通性测试（最小 hello-world 调用，验证认证、网络、版本兼容）
3. 记录连通性测试结果到 Memory（包含版本号、关键参数、已知限制）

### 3b. 技术架构设计（必选）

1. 列出系统的全部技术组件（Layer 1 实测组件 + 3a 引入的外部工具）
2. 设计组件间的部署拓扑（哪些进程、哪些服务、哪些数据库）
3. 定义跨组件的通信方式（HTTP / 消息队列 / 共享存储 / 直接函数调用）
4. 标注每个架构决策的依据（性能要求、成本约束、团队熟悉度等）
5. 生成**技术架构方案文档**（含 ADR）

### 真实案例

会话 eb2a0fa2 中：
1. 安装 LangChain MCP 工具并完成连通性测试（3a）
2. 基于 BridgePipeline 输出，设计 Agentic-RAG 架构（3b）
3. 生成 `Agentic-RAG-Architecture.md`
4. 编写 `agentic_kg_rag_mvp.py` 验证架构可行性
5. 将 MVP 验证结果反哺回 BridgePipeline 规范文档

### 检查清单

- [ ] （3a）MCP/SDK 已安装并连通性验证通过
- [ ] （3b）技术架构方案中每个组件都能追溯到 Layer 0 的能力边界评估
- [ ] （3b）架构选型有明确依据（不是凭感觉）
- [ ] 没有引入未在 Layer 0/1 验证过的新组件

### 回退触发

- 3a 连通性失败：先排查环境/认证；若工具本身不可用，回退到 Layer 0 评估替换
- 3b 架构需要调整集成拓扑：回退到 Layer 2 更新拓扑规范文档

---

## Layer 4: 产品/架构蓝图

### 编写顺序

按以下顺序编写三份文档（顺序重要——每份依赖上一份）：

#### 1. 产品需求文档（PRD）
- 产品定义 + 一句话描述
- 用户流程（从打开页面到完成任务的完整路径）
- 页面/模块清单（每个模块标注 P0/P1/P2 优先级）
- 核心交互逻辑

#### 2. 后端 API 架构规范
- 系统架构总览图
- 服务拓扑与部署方案
- RESTful API 端点列表（method + path + request/response schema）
- 数据模型定义
- 异步任务状态机
- 错误处理规范
- 实施路线

#### 3. 前端系统设计规范
- 前端架构分层
- UI 布局风格（颜色、字体、间距）
- 响应式适配方案
- 完整页面清单 + 组件树
- 详细交互逻辑
- 数据流与状态管理方案
- 技术选型（框架、构建工具、状态管理）

### 真实案例

会话产出三份蓝图：
- `multimodal-rag-prd-v1.0.md`
- `backend-api-architecture-v1.0.md`（基于 MinerU → BridgePipeline → Agentic KG-RAG 三阶段）
- `frontend-system-design-v1.0.md`（基于后端 API 规范）

### 检查清单

- [ ] PRD 写在 Backend API Spec 之前
- [ ] Backend API Spec 写在 Frontend Design Spec 之前
- [ ] 三份文档之间的依赖关系显式标注
- [ ] 每份文档末尾有实施路线图
- [ ] 功能需求的优先级用 P0/P1/P2 标注

### 回退触发

若蓝图编写过程中发现技术架构方案有遗漏或矛盾，回退到 Layer 3 更新技术架构方案。

---

## Layer 5: 项目开发规范确立

### Product Contract（Layer 5 必备）

一个 `skill/superpower` 只有在以下字段完整时，才可视为“可维护产品”：

- 版本（Version）：
  - 语义版本号（如 `v1.2.0`）
  - 兼容性声明（向后兼容/不兼容）
- 边界（Boundary）：
  - 输入范围（适用场景 / 非适用场景）
  - 输出物与完成定义
  - 明确不做项（Out of scope）
- 变更记录（Change Log）：
  - 变更项、原因、影响面、迁移要求
  - 对应证据链接（PR / 测试 / 评测）
- 验收标准（Acceptance）：
  - 必过检查项
  - 失败信号
  - 回退条件

缺失任一字段时：不得标记 Layer 5 通过。

### 7 条铁律（必须写入 CLAUDE.md）

1. 前端代码统一放在 `frontend/` 目录
2. 后端代码统一放在 `backend/` 目录
3. 后端敏感配置（API Key 等）统一在 `.env` 文件管理，`.env` 必须加入 `.gitignore`
4. **环境隔离**：每个独立组件使用项目技术栈的标准隔离机制（见技术栈映射表）
5. 部署 chatbot-planner / coder / reviewer / debugger 四个 Agent 配置到 `.claude/agents/`（从本 skill 的 `references/agent-templates/` 复制）
6. **测试规范**：每个后端 API 端点必须有对应的集成测试；测试文件放在语言惯例位置（见映射表）；测试必须在真实依赖（非 mock）上运行
7. **安全规范**：依赖版本必须锁定（生成 lockfile）；提交前运行漏洞扫描；API Key 等敏感值禁止出现在日志中

### 技术栈映射表

| 语言 | 环境隔离 | Lockfile | 漏洞扫描 | 测试目录惯例 |
|------|---------|---------|---------|-------------|
| Python | `uv venv .venv` | `uv lock` → `uv.lock` | `uv audit` / `pip-audit` | `tests/` |
| Node.js | `pnpm` + `.nvmrc` | `pnpm-lock.yaml` | `pnpm audit` | `__tests__/` 或 `*.test.ts` |
| Go | `go mod` + 项目级 module | `go.sum` | `govulncheck` | `*_test.go` 同包 |
| Java | Maven/Gradle wrapper（多模块） | `pom.xml` 锁版本 / `gradle.lockfile` | OWASP Dependency-Check | `src/test/java/` |
| Rust | Cargo workspace | `Cargo.lock` | `cargo audit` | `tests/` 或 `#[cfg(test)]` |

> 项目混用多语言时（如前端 Node + 后端 Python），每个语言子项目独立遵守对应行的规范。

### 五子系统自检（来自 walkinglabs/awesome-harness-engineering）

L5 规范完整性的横向检查框架。如果五项中任一答"否"，说明对应 Layer 有遗漏，回去补齐：

| 子系统 | harness-engineering 对应物 | 自检问题 |
|--------|------------------------|---------|
| instructions | 7 条铁律 + PRD/API Spec/Frontend Spec/CLAUDE.md | Agent 能从规范文档找到行为约束吗？ |
| tools | Layer 1 组件能力边界 Memory + 集成拓扑规范 | 每个工具的输入输出/限制/失败模式有实测记录吗？ |
| environment | 技术栈映射表 + 隔离环境 + `.env`/`.env.example` | 新成员按 CLAUDE.md 能在 30 分钟内搭好可运行环境吗？ |
| state | 项目 Memory + 规范文档版本号 + 任务追踪 | 跨 session / 跨成员能恢复"项目当前在 Layer 几"吗？ |
| feedback | 集成测试（真实依赖）+ reviewer issue list + debugger 根因报告 | 出错时能在 1 步内定位是哪个 Layer 的假设错了吗？ |

### 变更记录模板（可直接复用）

```text
## [skill/superpower-name] Changelog

### vX.Y.Z - YYYY-MM-DD
- Change: <改了什么>
- Why: <为什么改>
- Impact: <影响哪些角色/流程/产物>
- Compatibility: <兼容/不兼容 + 说明>
- Migration: <需要执行的迁移步骤；若无写 None>
- Evidence: <PR / 测试结果 / 评测链接>
```

### 验收标准模板（Layer 5 Gate）

- [ ] 已声明当前版本与兼容性级别
- [ ] 已定义输入/输出边界与不做项
- [ ] 已更新变更记录并附证据链接
- [ ] 已定义必过检查项（可复测）
- [ ] 已定义失败信号（可观测）
- [ ] 已定义回退条件与回退入口

评审结论规则：
- 任一未勾选 => Layer 5 未通过
- 全部勾选且证据可访问 => Layer 5 通过

### 附加规范（按需）

- 数据库 schema 管理（Alembic / Flyway）
- Git 分支策略（feature branch + PR review）
- Commit message 格式
- CI/CD 流程（推荐 Layer 6 完成后配置）
- **CLAUDE.md 体量约束**：项目根 `CLAUDE.md` ≤ 100 行（"给地图不给百科"），超出拆到 `docs/` 子文档并在 CLAUDE.md 中以索引列出

### 产出

项目根目录的 `CLAUDE.md`，包含：
- 项目概述
- 虚拟环境隔离规范（激活方式 + 验证方式 + 首次创建方式）
- 项目文件结构
- 环境约束规则
- 规范文档索引（所有 Layer 0-4 产出的文档路径）

### 检查清单

- [ ] CLAUDE.md 包含完整的虚拟环境激活/验证/创建命令
- [ ] `.gitignore` 包含 `.venv/`、`.env`、`output/`
- [ ] 规范文档索引列出所有 Layer 产出的文档
- [ ] 所有组件目录都有各自的 CLAUDE.md
- [ ] `.claude/agents/` 已部署 planner/coder/reviewer/debugger

### 回退触发

若规范确立中发现 Layer 4 蓝图有遗漏，回退到 Layer 4 补充。

---

## Layer 6: 前后端施工与联调

### 顺序：6a → 6b → 6c → 6d → 6e → 6f

#### 6a. 前端施工

1. 调用 `chatbot-planner` agent，输入 Frontend Design Spec + PRD，输出实现计划
2. 审查实现计划是否与 Layer 4 规格一致
3. 调用 `chatbot-coder` agent，输入实现计划，生成代码到 `frontend/`
4. 验证前端可独立启动（mock 后端数据或静态数据）

#### 6b. 后端施工

1. 确认 Backend API Spec 中每个端点的 schema 定义完整
2. 调用 `chatbot-coder` agent，输入 Backend API Spec + 数据模型，生成代码到 `backend/`
3. 按 Layer 5 技术栈映射表创建独立隔离环境并安装依赖
4. 验证后端可独立启动

#### 6c. 测试

1. 为每个后端 API 端点编写集成测试（`backend/tests/`）
2. 在真实依赖（非 mock）上运行测试，确保全部通过
3. 前端关键交互路径编写 E2E 测试（可选，视项目规模决定）

#### 6d. 联调与调试

1. 启动后端服务
2. 启动前端开发服务器
3. 从前端发起真实用户操作，追踪完整数据流
4. **每个具体 Bug 调用 `chatbot-debugger` agent**：
   - 输入：故障现象 + 复现步骤 + 相关文件路径
   - 输出：根因分析 + 修复方案（file:line + before/after）+ 回归测试建议
5. `chatbot-coder` 按 debugger 的修复方案执行修改
6. 修复后检查是否需要更新规范文档（debugger 输出会标注此项）

#### 6e. 静态审查（reviewer ↔ coder 闭环）

1. 调用 `chatbot-reviewer` agent（建议 `run_in_background: true`）
2. 审查维度：代码规范 / 逻辑漏洞 / 安全风险 / 性能问题 / 业务匹配度
3. reviewer 输出**结构化 issue list**（按 Critical/High/Medium/Low 分级）
4. 调用 `chatbot-coder` agent 按 issue list 逐条修复
5. 修复后重新运行测试

> **6d 与 6e 的边界**：6d 是"已发生的故障 → debugger 找根因"；6e 是"代码静态扫描 → reviewer 找隐患"。两者互补，不可替代。

#### 6f. 生产就绪检查（上线前必须完成）

1. **依赖安全**：按 Layer 5 技术栈映射表运行漏洞扫描（`uv audit` / `pnpm audit` / `govulncheck` / OWASP DC / `cargo audit`），无 Critical/High 级漏洞
2. **敏感信息**：日志中无 API Key / Token / 密码
3. **错误处理**：所有外部 API 调用有超时和错误处理
4. **环境变量**：`.env.example` 包含所有必需键名（值为占位符）
5. **文档同步**：规范文档与最终代码一致
6. **运行时隔离三件套**（来自 OpenHarness 安全层规范）：
   - **permissions** — Agent / 服务的权限分级（只读 / 读写 / 提权）有显式声明
   - **hooks** — 危险命令（`rm -rf` / `git push --force` / 数据库 drop）配置 deny hooks 或确认拦截
   - **sandbox** — 不可信代码执行隔离在容器 / 子进程 / 沙箱（Docker / nsjail / WebAssembly 之一）

### 真实案例（联调阶段问题）

| 问题 | 类型 | 解决方向 |
|------|------|---------|
| 图谱可视化不显示 | 数据流 Bug | 追踪 KG 构建到前端的完整链路 |
| 文档名显示随机数字 | 字段映射 Bug | 修复后端返回的文档名字段 |
| HTTP 413 上传失败 | 配置问题 | 调整文件大小限制 |
| 文档管理只显示一个 | 状态管理 Bug | 检查前端列表渲染逻辑 |

### 检查清单

- [ ] 前端使用 chatbot-planner → chatbot-coder 的标准流程
- [ ] 后端在独立隔离环境中运行（按技术栈映射表）
- [ ] 每个 API 端点 response 格式与 Backend API Spec 一致
- [ ] 每个前端组件能追溯到 Frontend Design Spec
- [ ] 联调中发现的 Bug 由 chatbot-debugger 输出根因 + 修复方案，coder 执行
- [ ] chatbot-reviewer 的 issue list 已被 coder 逐条处理
- [ ] 所有测试通过（集成 + E2E）
- [ ] 生产就绪检查清单 5 项全部打勾
- [ ] 完整用户流程可走通

### 回退触发

- 施工发现 Backend API Spec 有误：回退 Layer 4
- 施工发现 Layer 5 规范矛盾：回退 Layer 5
- **不要在代码里绕过规范文档的错误**——规范错了就修规范，代码跟着改

---

## 何时退出本方法论

harness-engineering是**项目搭建**方法论，不是项目全生命周期方法论。Layer 6 走完后系统已上线运行，此时强行套用 7 层结构会造成过度工程。明确退出时机和维护期工作模式是防止方法论"虎头蛇尾"或"水土不服"的关键。

### 退出条件（满足以下全部）

1. Layer 6 全部交付物已完成（API 集成测试通过 + 6f 生产就绪 5 项打勾）
2. 系统稳定运行 ≥ 2 周，无 P0/P1 级别线上故障（窗口可视项目调整）
3. 抽查 3 个端点 + 3 个组件，规范文档与代码一致，无过期描述
4. CLAUDE.md 完整：新成员按其指引可独立完成环境搭建并跑通端到端流程

满足后宣告**搭建期结束，进入维护期**，并在项目根 CLAUDE.md 顶部记录"harness-engineering搭建期完成日期：YYYY-MM-DD"。

### 维护期工作模式

**保留**（不可松懈）：
- 规范文档是唯一真相源（不一致 → 必须选一边修）
- 每次迭代都沉淀（新认知落到对应规范文档）
- 环境隔离（依赖变更走 lockfile 重锁）
- 安全规范（依赖扫描、敏感值不入日志）
- Agent 协作（feature 走 planner → coder → reviewer，bug 走 debugger → coder）

**取消**（避免过度工程）：
- 不再强制按 0→6 顺序推进——维护期是单点修改
- 单个 Bug 修复不需要回退到 Layer 4 改蓝图（除非该 Bug 暴露蓝图根本性遗漏）
- 不再要求每次改动都更新所有上游规范——只更新被影响的那一份

**可选项**（按团队规模与项目寿命决定是否启用）：
- **entropy management（文档漂移修复）**——每月 / 每 quarter 由 chatbot-reviewer 或专用 agent 巡检规范文档与代码的一致性，主动修复漂移。来源：Martin Fowler "Humans on the Loop" 三系统之一，填补"取消全规范同步"后留下的真空

### 重新进入触发器

| 触发信号 | 重新进入起点 | 工作范围 |
|---------|------------|---------|
| 引入 / 替换核心组件 | Layer 0 | 仅对新组件做能力边界 + MVP |
| 调整集成拓扑（数据流变化） | Layer 2 | 更新拓扑规范 + 受影响桥接段 |
| 引入新外部框架 / 切换部署架构 | Layer 3 | 更新技术架构方案 |
| 新增主功能模块（新页面+新流程） | Layer 4 | 补 PRD/API/Frontend 蓝图章节 |
| 工程纪律出问题（依赖未锁定、测试 mock 化） | Layer 5 | 修订 CLAUDE.md，重新对齐 |
| 大规模重构（>30% 后端改写） | Layer 4 | 完整走 4→6，旧代码视为遗留 |

**关键原则**：重新进入只走需要的层，不重做整个项目。

### 退出反模式

1. **早退**：6f 生产就绪检查未完成就宣告搭建结束 → 上线后被安全/可观测性问题反噬
2. **死守**：稳定后仍机械按 7 层做小需求（"加导出 CSV 按钮"也走全流程）→ 团队反感方法论
3. **静默退出**：未通告团队"已进入维护期"→ 一部分人按搭建期、一部分人按维护期，规范执行混乱

### 退出检查清单

- [ ] Layer 6 全部交付物完成
- [ ] 系统稳定运行 ≥ 2 周无 P0/P1 故障
- [ ] 规范文档抽查与代码一致
- [ ] CLAUDE.md 已通告搭建期完成日期
- [ ] 团队已对齐维护期工作模式（保留 5 条 / 取消 3 条）

---

## 回退机制实战

### 回退原则

- 回退时只修改**受影响的文档和代码**，不推倒重来
- 回退后必须重新验证被修改层的通过条件，再继续向前
- 同一层回退超过 2 次，说明上游假设有根本性错误，考虑回退更多层

### 典型回退场景

| 触发情境 | 当前层 | 回退到 | 操作 |
|---------|-------|--------|------|
| API 实测格式与文档不符 | 1 | 0 | 重做能力边界评估 |
| 桥接发现上游字段缺失 | 2 | 1 | 修正组件规范并重新桥接 |
| 架构设计需要新组件 | 3 | 0 | 补做能力边界评估 + MVP 实测 |
| 蓝图发现 API 缺数据源 | 4 | 3 | 更新技术架构方案 |
| 施工发现端点 schema 不全 | 6 | 4 | 补充 Backend API Spec |

---

## 反模式：常见错误

### 错误 1: 跳过 Layer 0 直接开始写代码
**症状**：做到一半发现某组件不支持需要的功能，推倒重来。
**正确做法**：先花 10 分钟通读源码，把结论写下来。

### 错误 2: 规范文档基于猜测而非实测
**症状**：规范文档写得很好，但实际运行时 API 返回与文档不符。
**正确做法**：每个字段说明都要有实测数据支撑。

### 错误 3: Layer 1 没各自跑通就开始 Layer 2 桥接
**症状**：调试时无法判断是哪个组件的问题。
**正确做法**：所有组件 MVP 各自验证通过后，再进 Layer 2。

### 错误 4: 跳过 Layer 4 蓝图直接施工
**症状**：写到一半前后端接口对不上，或遗漏关键功能。
**正确做法**：先写完三份蓝图，确认无矛盾再动代码。

### 错误 5: 规范文档更新滞后于代码
**症状**：代码改了但规范没更新，后人只能读代码理解意图。
**正确做法**：代码修改后，同步检查相关规范文档是否需要更新。

### 错误 6: 跳过 6e 审查闭环直接交付
**症状**：简单测了一下"看起来能跑"就觉得完成了。
**正确做法**：reviewer 出 issue list → coder 逐条修复 → 再测。

### 错误 7: 跳过 6f 生产就绪检查
**症状**：上线后发现日志泄露 API Key、依赖有已知漏洞。
**正确做法**：5 项检查全部打勾才算 Layer 6 完成。

---

## 检查清单汇总

### 每层完成标志

| Layer | 完成标志 |
|-------|---------|
| 0 | 每个候选组件的能力边界评估已写入 Memory |
| 1 | 每个组件的规范文档 v1（有实测数据支撑） |
| 2 | 集成拓扑规范文档 + Bridge Pipeline 端到端测试通过 |
| 3 | 技术架构方案文档（3a 若执行则附 MCP 连通性记录） |
| 4 | PRD + Backend API Spec + Frontend Design Spec（三份无矛盾） |
| 5 | 项目 CLAUDE.md（含 7 条铁律） + 所有组件 CLAUDE.md |
| 6 | 可运行系统 + 测试报告 + 审查报告 + 生产就绪检查表 |

### 全局检查清单

- [ ] 每个组件使用独立隔离环境（按技术栈映射表）
- [ ] `.gitignore` 包含隔离环境产物（`.venv/` / `node_modules/` / `target/` 等）和 `.env`、`output/`
- [ ] 所有 API Key / Token 在 `.env` 中管理
- [ ] `.env` 已加入 `.gitignore`
- [ ] 规范文档之间没有矛盾（交叉引用已验证）
- [ ] 每个规范文档的字段说明有实测数据支撑
- [ ] chatbot-planner → coder → (debugger | reviewer) → coder 的协作流程已执行
- [ ] reviewer 的 issue list 已被 coder 处理
- [ ] 联调阶段每个 Bug 都有 debugger 的根因分析记录
- [ ] 生产就绪检查 5 项全部打勾
- [ ] 完整用户流程可走通
