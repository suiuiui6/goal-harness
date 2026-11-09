---
name: harness-engineering
description: harness-engineering方法论 / Harness Engineering — 当用户启动新项目、搭建工程框架、需要体系化地组织多组件项目（2 个以上外部 API/服务集成）时使用。也覆盖以下英文场景：new project setup, project scaffolding, multi-component integration, monorepo bootstrap, RAG/Agentic system architecture, spec-driven development, document-driven engineering, multi-API orchestration, framework selection from scratch。指导 Claude Code 按照"能力边界摸底 → 组件逐一 MVP 实测+集成拓扑设计 → 外部工具集成与技术架构设计 → 产品蓝图 → 项目规范确立 → 前后端施工联调"的 7 层递进流程完成项目搭建，并通过 chatbot-planner/coder/reviewer/debugger 四大 Agent 协作。也适用于已有组件需要整合、或需要建立规范文档驱动开发流程的场景。本方法论仅覆盖**搭建期 / build phase**，项目稳定后进入维护期需按"何时退出本方法论"章节切换工作模式。不适用于：单文件 bug 修复、已有明确技术方案的简单功能开发、单组件项目（仅集成 1 个外部服务）、已进入维护期的成熟项目，以及纯研究调研任务。
---

# harness-engineering — 项目搭建方法论

## 什么是harness-engineering

harness-engineering是一套**文档驱动的项目搭建方法论**。核心理念是：

> 每一阶段的 MVP 实测结论都沉淀为规范文档，下一阶段的行为严格受已有规范约束，形成层层叠加的知识体系。

它不是告诉你"用什么技术栈"或"怎么写代码"，而是告诉你**按什么顺序做事、每个阶段的产出是什么、各阶段之间如何衔接**。

## 什么时候使用

### Web 全栈交付 profile

当交付对象是 Web full-stack（前端、后端、数据、部署）时，按 `references/web-fullstack-delivery.md` 的 delivery contract 执行，并使用 `references/load-policy.json` 选择加载范围。局部 API 变更仍按维护期处理，不升级为完整 bootstrap。

**触发信号**（满足任意一条即适用）：
- 项目涉及 **2 个以上**外部 API / 服务 / 组件的集成（如：文档解析 + LLM + 向量库）
- 已有若干独立组件，需要整合为完整系统，但组件间接口尚未打通
- 技术栈不确定，需要先探索再落地（不知道用哪个库/服务）
- 需要建立规范文档驱动开发的工程纪律（团队协作或 AI 驱动开发场景）

**不适用场景**（遇到以下情况请用其他 skill）：
- 单文件修复、单个 bug 修复 → 直接修复，无需本方法论
- 已有明确技术方案的功能开发 → 用 `writing-plans` + `subagent-driven-development`
- 纯粹的研究调研、技术选型比较 → 用 `brainstorming`
- 单组件项目（只集成一个外部服务）→ 直接 MVP 实测即可，无需完整流程

**与其他 skill 的协作关系**：
- Layer 0 前可选调用 `brainstorming` 梳理需求
- Layer 6 施工时与 `test-driven-development` 并行使用
- Layer 6 完成后用 `verification-before-completion` 验收

**与 awesome-harness-engineering 系列资源的关系**：本方法论不替代外部资源汇编（如 `ai-boost/awesome-harness-engineering`、`walkinglabs/awesome-harness-engineering`），而是规定流程；Layer 0 / Layer 1 阶段可参考这些资源的"问题类别索引"扩展能力边界自检；运行时层面如需自托管 Agent harness，可考虑 `HKUDS/OpenHarness` 作为 Layer 6 施工的执行容器。

> 项目搭建完成后如何退出本方法论、维护期如何工作、何时需要重新进入，见后文 [何时退出本方法论](#何时退出本方法论)。

## 7 层递进流程

harness-engineering将项目搭建分为 7 个层次，**必须按顺序推进，不跳步**。跳步的代价是后期返工——每一层都在验证上一层假设的正确性。

### 回退机制

流程是有序的，但不是单向的。每层都有明确的**通过条件**和**回退条件**：

| 层 | 通过条件 | 失败时回退到 | 回退时需更新的产物 |
|---|---|---|---|
| Layer 0 | 能一句话说清楚每个组件的能力边界 | — | 重写 Memory 条目 |
| Layer 1 | 每份规范文档有实测数据支撑 | Layer 0（换组件方案） | 重写该组件的 Memory 条目和规范文档 |
| Layer 2 | 完整链路端到端可追溯 | Layer 1（某段桥接无法实现，说明上游组件规范有误） | 修正上游规范文档，重新桥接 |
| Layer 3 | 技术架构方案有依据且组件可追溯（3a 若执行则 MCP 连通） | Layer 2（架构设计发现集成拓扑需调整） | 更新集成拓扑规范文档 |
| Layer 4 | 三份蓝图文档无矛盾 | Layer 3（蓝图设计发现技术架构需调整） | 更新技术架构方案文档 |
| Layer 5 | 版本声明、边界定义、变更记录、验收标准四类产物齐备并可追溯 | Layer 4（规范确立时发现蓝图有遗漏） | 补充蓝图文档对应章节 |
| Layer 6 | 测试全通过 + 生产就绪检查清单全打勾 | Layer 4/5（施工发现蓝图或规范有误） | 修正蓝图/规范文档，重新施工受影响部分 |

**回退原则**：
- 回退时只修改**受影响的文档和代码**，不推倒重来整个流程
- 回退后必须重新验证被修改层的通过条件，再继续向前
- 如果同一层回退超过 2 次，说明上游假设有根本性错误，考虑回退更多层

### Layer 0: 能力边界摸底

**目标**：搞清楚每个候选组件的真实能力边界，不做假设。

**做什么**：
1. 拉取组件源码（如 GitHub 仓库）
2. 通读核心模块，理解：输入格式、输出格式、支持的功能范围、显式不支持的功能
3. 将结论写入**项目 Memory**（用 `Write` 工具写入 `.claude/projects/<project>/memory/`）

**产出**：能力边界评估 Memory 条目

**为什么重要**：后期所有架构决策都依赖这一层的结论。例如，"LangExtract 不支持文档解析"这个发现直接决定了必须引入 MinerU 作为文档解析层。

**验证标准**：能否用一句话说清楚每个组件的核心能力边界？

---

### Layer 1: 核心组件逐一 MVP 实测 → 规范文档

**目标**：对每个候选组件独立进行最小可行测试，逐一产出规范文档。组件数量不限（2 个、3 个、5 个均适用）。

**做什么**（每个组件重复以下流程）：
1. 搭建最小 MVP 测试环境（独立目录、独立虚拟环境）
2. 配置 API Key / Token（写入 `.env`，加入 `.gitignore`）
3. 编写 MVP 测试脚本，只验证最核心的输入→输出链路
4. 实际运行测试，记录真实输出
5. 基于实测结果，生成该组件的规范文档（包含：输入格式规范、输出格式规范、字段说明、关键参数说明）

**产出**：每个组件各自的 MVP 测试脚本 + 规范文档 v1

**关键原则**：
- MVP 越小越好——能用一个 sample.pdf 验证的就不要用 10 个
- 配置信息（API Key 等）永远放在 `.env`，绝不硬编码
- 规范文档必须基于**实测结果**，不是基于文档猜测
- 如果实测结果与官方文档不一致，以实测为准，并在规范文档中标注
- 每个组件必须使用**独立隔离环境**（按所属技术栈：Python `uv venv` / Node `pnpm` workspace / Go module / Java module / Rust crate），组件间依赖互不干扰
- 此阶段不要试图让任何两个组件通信——那是 Layer 2 的事
- 所有规范文档格式保持一致（方便后续集成拓扑设计）

**验证标准**：每份规范文档中描述的每一种输入/输出格式，都有实测数据支撑。

**回退条件**：若某组件实测发现根本不可用（API 不稳定、功能缺失、性能不达标），回退到 Layer 0 重新评估该组件，考虑替换方案。

---

### Layer 2: 集成拓扑设计 → 桥接管道实现

**目标**：基于 Layer 1 产出的所有组件规范文档，设计完整的集成拓扑，并逐段实现桥接管道。

**做什么**：

**2a. 集成拓扑设计**：
1. 列出所有组件及其规范文档
2. 画出组件依赖图（谁的输出是谁的输入，数据流方向）
3. 确定桥接顺序（按依赖关系，从数据源到最终消费者）
4. 生成**集成拓扑规范文档**（包含：组件依赖图、数据流图、每条边的格式转换规则）

**2b. 逐段桥接实现**（按拓扑顺序，每条边依次实现）：
1. 将上游组件规范文档作为约束
2. 定义该段的输入/输出 schema 转换规则
3. 编写桥接代码，端到端验证该段正确性
4. 验证通过后再进行下一段

**产出**：集成拓扑规范文档 + 完整 Pipeline 代码 + 端到端实测数据

**关键原则**：
- 集成拓扑规范文档必须显式引用所有上游组件规范文档
- Pipeline 的每一阶段输入/输出都应在规范中有明确定义
- 使用 `--cached` 模式支持跳过上游组件独立调试下游逻辑
- 逐段验证，不要一次性写完所有桥接代码再测试

**验证标准**：从原始输入到最终输出的完整链路可追溯，每一阶段的中间产物有 schema 约束。

**回退条件**：若某段桥接无法实现（格式不兼容、性能不达标、上游输出字段缺失），回退到 Layer 1 修正对应组件的规范文档，确认问题根源在上游规范而非桥接代码后再重新桥接。

---

### Layer 3: 外部工具集成 + 技术架构设计

**目标**：引入项目需要的外部工具/框架，并基于前序 Layer 的产出设计完整技术架构。

本层包含两个子阶段：3a 可选（仅当项目需要外部 MCP/框架时执行），3b 必选。

---

**3a. 外部工具集成验证**（可选）

**何时执行**：项目需要接入外部框架/工具（如 LangChain、LlamaIndex、特定的 MCP 服务）时。

**何时跳过**：项目使用纯本地工具链（仅依赖 Layer 1 已实测的组件）时，直接进入 3b。

**做什么**：
1. 安装外部工具的 MCP 或 SDK
2. 进行连通性测试（最小 hello-world 调用，验证认证、网络、版本兼容）
3. 记录连通性测试结果到 Memory（包含版本号、关键参数、已知限制）

**产出**：MCP/SDK 连通性验证记录

**回退条件**：连通性测试失败时，先排查是否为环境/认证问题；若工具本身不可用，回退到 Layer 0 重新评估是否需要换工具。

---

**3b. 技术架构设计**（必选）

**做什么**：
1. 列出系统的全部技术组件（Layer 1 实测组件 + 3a 引入的外部工具）
2. 设计组件间的部署拓扑（哪些进程、哪些服务、哪些数据库）
3. 定义跨组件的通信方式（HTTP/消息队列/共享存储/直接函数调用）
4. 标注每个架构决策的依据（性能要求、成本约束、团队熟悉度等）
5. 生成**技术架构方案文档**

**产出**：技术架构方案文档（包含：组件清单、部署拓扑图、通信方式说明、架构决策记录 ADR）

**关键原则**：
- 技术架构方案必须严格参照已有规范文档（Layer 0/1/2）
- 每个架构选型必须写明依据（不是凭感觉），便于后续回顾
- 架构方案不引入未在 Layer 0/1 验证过的新组件——若必须引入，回退到 Layer 0 补做能力边界摸底

**验证标准**：架构方案中每个组件都能追溯到 Layer 0 的能力边界评估和 Layer 1 的规范文档。

**回退条件**：若架构设计中发现 Layer 2 的集成拓扑需要调整（如新增组件、改变数据流方向），回退到 Layer 2 更新集成拓扑规范文档后再继续。

---

### Layer 4: 产品/架构蓝图

**目标**：在写任何产品代码之前，把产品设计、后端架构、前端设计全部以规范文档形式确定下来。

**做什么**：
1. 编写**产品需求文档（PRD）**：产品定义、用户流程、页面/模块清单、核心交互逻辑
2. 编写**后端 API 架构规范**：服务拓扑、API 端点、数据模型、任务状态机、错误处理规范
3. 编写**前端系统设计规范**：架构分层、UI 布局、组件树、数据流、技术选型

**产出**：三份蓝图文档（PRD + Backend API Spec + Frontend Design Spec）

**关键原则**：
- 这三份文档互为约束——前端设计依赖后端 API，后端 API 依赖 PRD 的功能需求
- 每份文档末尾应包含实施路线图
- 这是**施工前最后一次可以低成本修改架构的机会**

**验证标准**：任意两个开发人员分别读这三份文档，对系统设计应达成一致理解。

**回退条件**：若蓝图编写过程中发现技术架构方案有遗漏或矛盾（如 API 端点依赖的数据源在 Layer 3 架构中未覆盖），回退到 Layer 3 更新技术架构方案文档后再继续。

**进入下一层前**：告诉用户 Layer 6 施工与调试需要 chatbot-planner/coder/reviewer/debugger 四个 Agent 协作，Layer 5 会完成 Agent 配置部署。

---

### Layer 5: 项目开发规范确立

**目标**：确立项目的工程纪律，写入 CLAUDE.md。

**核心规范（7 条铁律）**：
1. 前端代码统一放在 `frontend/` 目录
2. 后端代码统一放在 `backend/` 目录
3. 后端敏感配置（API Key 等）统一在 `.env` 文件管理，`.env` 必须加入 `.gitignore`
4. **环境隔离**：每个独立组件使用项目所属技术栈的标准隔离机制（见下方"技术栈映射表"）。同一仓库内组件依赖互不污染
5. **部署 chatbot-planner/coder/reviewer/debugger 四个 Agent 配置到 `.claude/agents/`**（从本 skill 的 `references/agent-templates/` 复制），确保 Layer 6 施工与调试时有 Agent 可用
6. **测试规范**：每个后端 API 端点必须有对应的集成测试；测试文件放在 `backend/tests/`（或语言对应惯例位置）；测试必须在真实依赖（非 mock）上运行
7. **安全规范**：依赖版本必须锁定（生成 lockfile）；提交前运行漏洞扫描；API Key 等敏感值禁止出现在日志输出中

**技术栈映射表**（铁律 4/6/7 的具体实现，按项目语言选择）：

| 语言 | 环境隔离 | Lockfile | 漏洞扫描 | 测试目录惯例 |
|------|---------|---------|---------|-------------|
| Python | `uv venv .venv` | `uv lock` → `uv.lock` | `uv audit` / `pip-audit` | `tests/` |
| Node.js | `pnpm` + `.nvmrc` | `pnpm-lock.yaml` | `pnpm audit` | `__tests__/` 或 `*.test.ts` |
| Go | `go mod` + 项目级 module | `go.sum` | `govulncheck` | `*_test.go` 同包 |
| Java | Maven/Gradle wrapper（多模块） | `pom.xml` 锁版本 / `gradle.lockfile` | OWASP Dependency-Check | `src/test/java/` |
| Rust | Cargo workspace | `Cargo.lock` | `cargo audit` | `tests/` 或 `#[cfg(test)]` |

> 项目混用多语言时（如前端 Node + 后端 Python），每个语言子项目独立遵守对应行的规范，互不干扰。

**五子系统自检**（来自 walkinglabs/awesome-harness-engineering 的理论框架，作为 L5 规范完整性自检）：

| 子系统 | harness-engineering 中的对应物 | 自检问题 |
|--------|-------------------------|---------|
| instructions | 7 条铁律 + 规范文档（PRD/API Spec/Frontend Spec/CLAUDE.md） | Agent 拿到任务时，能从规范文档中找到行为约束吗？ |
| tools | Layer 1 各组件能力边界 Memory + 集成拓扑规范 | 每个工具/组件的输入输出格式、限制、失败模式是否有实测记录？ |
| environment | 技术栈映射表 + 隔离环境 + `.env`/`.env.example` | 新成员按 CLAUDE.md 能在 30 分钟内搭好可运行环境吗？ |
| state | 项目 Memory + 规范文档版本号 + 任务追踪 | 跨 session / 跨成员能恢复"项目当前在 Layer 几、卡在哪"吗？ |
| feedback | 集成测试（真实依赖）+ reviewer issue list + debugger 根因报告 | 出错时能在 1 步内定位是哪个 Layer 的假设错了吗？ |

> 五个子系统中任一项答"否"，说明 L5 规范有遗漏，回到对应 Layer 补齐。

**附加规范**（根据项目需要）：
- 数据库 schema 管理方式（推荐 Alembic 或 Flyway）
- Git 分支策略（推荐 feature branch + PR review）
- Commit message 格式
- CI/CD 流程（推荐在 Layer 6 完成后配置，而非施工前）
- **CLAUDE.md 体量约束**：项目根 `CLAUDE.md` 控制在 100 行以内（"给地图不给百科"），超出部分拆到 `docs/` 子文档并在 CLAUDE.md 中以索引形式列出

**产出**：项目根目录的 CLAUDE.md（含完整环境约束规则 + 规范文档索引）

**Layer 5 Gate（强制）**：Layer 5 通过前，必须具备并链接以下产物：版本声明、边界定义、变更记录、验收标准。任一缺失时，仅可标记为“未通过并回补”，不得进入下一层。

**为什么重要**：这是harness-engineering的**宪章**——所有后续行为都受这些规则约束。如果这一层没做好，施工阶段会出现大量不一致。

**回退条件**：若规范确立过程中发现 Layer 4 蓝图有遗漏（如缺少某个模块的 API 定义），回退到 Layer 4 补充蓝图文档后再继续。

---

### Layer 6: 前后端施工与联调

**目标**：严格按照 Layer 4 的蓝图和 Layer 5 的规范，完成前后端代码实现并验收。

**做什么**：

**6a. 前端施工**：
1. 基于 PRD + Frontend Design Spec，使用 `chatbot-coder` agent 生成前端代码
2. 前端代码放入 `frontend/` 目录
3. 验证前端可独立启动（mock 后端数据或使用静态数据）

**6b. 后端施工**：
1. 基于 Backend API Spec，使用 `chatbot-coder` agent 生成后端代码
2. 后端代码放入 `backend/` 目录
3. 按 Layer 5 技术栈映射表创建独立隔离环境并安装依赖（Python: `uv venv` / Node: `pnpm install` / Go: `go mod tidy` / Java: `mvn install` / Rust: `cargo build`）

**6c. 测试**：
1. 为每个后端 API 端点编写集成测试（放在 `backend/tests/`）
2. 在真实依赖（非 mock）上运行测试，确保全部通过
3. 前端关键交互路径编写 E2E 测试（可选，视项目规模决定）

**6d. 联调与调试**：
1. 启动前后端服务
2. 从前端发起真实用户操作，追踪完整数据流
3. **每个具体 Bug 调用 `chatbot-debugger` agent**：复现故障 → 定位根因 → 输出修复方案
4. `chatbot-coder` 按 debugger 的修复方案执行修改
5. Bug 修复后检查是否需要在规范文档中补充说明（debugger 输出会标注此项）

**6e. 静态审查**：
1. 使用 `chatbot-reviewer` agent 对施工代码进行全面审查
2. 审查维度：代码规范、逻辑漏洞、安全风险、性能问题、业务匹配度
3. reviewer 输出结构化 issue list（按 Critical/High/Medium/Low 分级）
4. 使用 `chatbot-coder` agent 按 issue list 逐条修复，修复后重新运行测试

> **6d 与 6e 的边界**：6d 处理**已发生的具体故障**（debugger 找根因），6e 处理**潜在的代码隐患**（reviewer 全维度扫描）。两者互补，不可替代。

**6f. 生产就绪检查**（上线前必须完成）：
1. **依赖安全**：按 Layer 5 技术栈映射表运行漏洞扫描（`uv audit` / `pnpm audit` / `govulncheck` / OWASP DC / `cargo audit`），无 Critical/High 级别漏洞
2. **敏感信息**：确认日志输出中无 API Key、Token、密码等敏感值
3. **错误处理**：所有外部 API 调用有超时设置和错误处理，不会因单点故障导致整体崩溃
4. **环境变量**：`.env.example` 包含所有必需的环境变量键名（值为占位符），新成员可按此配置
5. **文档同步**：规范文档与最终代码实现一致，无过期描述
6. **运行时隔离三件套**（来自 OpenHarness 安全层规范）：
   - **permissions**：Agent / 服务的权限分级（只读 / 读写 / 提权），权限矩阵显式声明
   - **hooks**：危险命令（`rm -rf` / `git push --force` / 数据库 drop）配置 deny hooks 或确认拦截
   - **sandbox**：不可信代码执行隔离在容器 / 子进程 / 沙箱（Docker / nsjail / WebAssembly 之一）

**产出**：可运行的前后端系统 + 测试报告 + 审查报告 + 生产就绪检查清单

**验证标准**：完整用户流程可走通；所有测试通过；生产就绪检查清单全部打勾。

**回退条件**：
- 若施工中发现 Backend API Spec 有误（字段缺失、类型错误、端点遗漏），回退到 Layer 4 修正蓝图，再重新施工受影响的部分
- 若施工中发现 Layer 5 规范有矛盾（如目录结构与实际技术栈不符），回退到 Layer 5 修正 CLAUDE.md
- 不要在代码里绕过规范文档的错误——规范错了就修规范，代码跟着改

---

## 何时退出本方法论

harness-engineering是**项目搭建**方法论，不是项目全生命周期方法论。Layer 6 走完后系统已上线运行，此时强行套用 7 层结构会造成过度工程。明确退出时机和维护期工作模式是防止方法论"虎头蛇尾"或"水土不服"的关键。

### 退出条件（满足以下全部）

1. **Layer 6 全部交付物已完成**：所有 API 端点的集成测试通过，6f 生产就绪 5 项检查全部打勾
2. **系统已稳定运行**：连续 2 周无 P0/P1 级别线上故障（可视项目调整窗口）
3. **规范文档与代码一致**：抽查 3 个端点和 3 个组件，确认 Backend API Spec / Frontend Design Spec / 集成拓扑文档无过期描述
4. **CLAUDE.md 完整**：新成员按 CLAUDE.md 可独立完成环境搭建并跑通端到端流程

满足以上四项后，宣告**harness-engineering搭建期结束，进入维护期**。

### 维护期的工作模式

退出 7 层流程后，团队按照"轻量纪律"运作。**保留**以下 5 条铁律不可松懈：
- 规范文档是唯一真相源（代码与规范不一致 → 选一边改，不留下不一致状态）
- 每次迭代都沉淀（新认知必须落到对应的规范文档）
- 环境隔离是纪律（依赖变更走 lockfile 重锁）
- 安全规范（依赖扫描、敏感值不入日志）
- Agent 协作流程（feature 开发仍走 planner → coder → reviewer，bug 修复仍走 debugger → coder）

**取消**以下重型流程：
- 不再强制按 0→6 顺序推进——维护期是**单点修改**，不是层级推进
- 单个 Bug 修复不需要回退到 Layer 4 改蓝图（除非该 Bug 暴露了蓝图根本性遗漏）
- 不再要求每次改动都更新所有上游规范——只更新被影响的那一份

**可选项**（按团队规模与项目寿命决定是否启用）：
- **entropy management（文档漂移修复）**：每月 / 每 quarter 由 chatbot-reviewer 或专用 agent 巡检规范文档与代码的一致性，主动修复漂移。来自 Martin Fowler "Humans on the Loop" 三系统中的 entropy management 概念，填补"取消全规范同步"后留下的真空

### 何时需要重新进入本方法论

维护期偶尔会触发**回到harness-engineering的信号**。识别下列任一信号时，从对应 Layer 重新进入：

| 触发信号 | 重新进入起点 | 工作范围 |
|---------|------------|---------|
| 引入新的核心组件 / 替换现有组件 | Layer 0 | 仅对新组件做能力边界 + MVP，不重做整个项目 |
| 调整集成拓扑（新增数据流、改变上下游关系） | Layer 2 | 更新集成拓扑规范 + 受影响的桥接段 |
| 引入新的外部框架 / 切换部署架构 | Layer 3 | 更新技术架构方案 |
| 新增主功能模块（不只是 endpoint，是新页面+新流程） | Layer 4 | 补 PRD/API/Frontend 三份蓝图的对应章节 |
| 工程纪律出问题（多人改 .env、依赖未锁定、测试 mock 化） | Layer 5 | 修订 CLAUDE.md，重新对齐团队 |
| 大规模重构（>30% 后端代码改写） | Layer 4 | 完整走 4→6，旧代码视为遗留 |

**关键原则**：重新进入只走需要的那几层，不需要从 Layer 0 重做。例如新增一个组件，只需 Layer 0（评估）+ Layer 1（MVP）+ Layer 2（与现有拓扑桥接）+ Layer 4（API 蓝图补章节），不需要重写技术架构方案或重做产品 PRD。

### 退出反模式

避免以下三种错误退出：

1. **早退**：Layer 6 没完成就宣告"项目搭建完毕"，把 6f 生产就绪检查留给"以后再说"——结果上线后被安全/可观测性问题反噬
2. **死守**：项目稳定后仍机械地按 7 层做每个 feature，给一个"加导出 CSV 按钮"的小需求也走全流程——团队反感方法论
3. **静默退出**：没明确告知团队"已进入维护期"，导致一部分人按搭建期流程做事、一部分人按维护期做事，规范执行混乱

退出时应**明确通告**：在项目根 CLAUDE.md 顶部记录"harness-engineering搭建期完成日期：YYYY-MM-DD，自此进入维护期"，让团队成员有共同认知。

---

## 四大 Agent 使用时机

harness-engineering依赖四个专用 Agent 完成不同类型的工作。它们应在**正确的阶段**被调用：

### chatbot-planner（前端产品架构师）
- **调用时机**：Layer 4（架构蓝图）阶段，需要设计页面结构和交互流程时
- **工具**：Read, Glob, Grep, WebSearch（只读，不写代码）
- **调用方式**：使用 `Agent` 工具，`subagent_type: chatbot-planner`
- **输入**：PRD + 后端 API 规范 + 现有设计模式
- **输出**：实现计划（需求分析→组件树→交互流程→数据设计→实施步骤）

### chatbot-coder（全栈开发工程师）
- **调用时机**：Layer 6（施工）阶段，planner 输出实现计划之后
- **工具**：Read, Write, Edit, Bash, Glob, Grep
- **调用方式**：使用 `Agent` 工具，`subagent_type: chatbot-coder`
- **输入**：planner 的实现计划 + 规范文档
- **输出**：可运行的代码文件
- **注意**：给 coder 的 prompt 必须包含完整的规范文档路径和约束条件

### chatbot-reviewer（代码审查专家）
- **调用时机**：Layer 6e（静态审查）阶段，或每个 feature 完成后
- **工具**：Read, Glob, Grep（只读）
- **调用方式**：使用 `Agent` 工具，`subagent_type: chatbot-reviewer`，建议设置 `run_in_background: true`
- **输入**：施工代码的文件路径
- **输出**：审查报告（按 Critical/High/Medium/Low 分级的问题清单 + 修复建议）

### chatbot-debugger（调试专家）
- **调用时机**：Layer 6d（联调）阶段遇到具体故障时；上线后线上 Bug 复盘时
- **工具**：Read, Glob, Grep, Bash（只读 + 可运行临时复现脚本，不修改产品代码）
- **调用方式**：使用 `Agent` 工具，`subagent_type: chatbot-debugger`
- **输入**：故障现象描述 + 复现步骤 + 相关文件路径
- **输出**：根因分析 + 修复方案（含 file:line + before/after 代码）+ 回归测试建议
- **与 reviewer 的边界**：reviewer 找"代码哪里写得不好"（静态、全维度），debugger 找"为什么这次它崩了"（动态、单点根因）

### Agent 协作流程

```
Layer 4 蓝图 + 规范文档
         │
         ▼
chatbot-planner ──► 实现计划
         │
         ▼
chatbot-coder ──► 代码实现
         │
         ▼
   ┌─────┴─────┐
   ▼           ▼
联调遇到Bug   静态审查
   │           │
   ▼           ▼
chatbot-debugger    chatbot-reviewer
（根因+修复方案）   （issue list）
   │           │
   └─────┬─────┘
         ▼
chatbot-coder ──► 修复代码
         │
         ▼
    回归测试
```

## Agent 配置部署指南

当目标项目还没有配置这四个 Agent 时：

1. 创建 `.claude/agents/` 目录（在项目根目录下）
2. 从本 skill 的 `references/agent-templates/` 复制四个配置文件
3. 根据项目实际情况调整以下字段：
   - `model`: 改为项目使用的模型
   - `max_turns`: 根据项目复杂度调整（planner 默认 10，coder 默认 20，debugger 默认 15）
   - coder 的代码风格部分：替换为项目的技术栈和设计规范

这些模板文件是**经过实战验证的默认配置**，大部分项目可以直接使用，只需调整技术栈特定的描述。

## 关键原则

### MVP 优先于完美
不要在 Layer 0-2 追求完美。MVP 的目的不是做出产品，而是**验证假设是否成立**。一个跑通的 50 行脚本比一个 500 行的完整实现更有价值。

### 规范文档是唯一真相源
当代码行为与规范文档不一致时，只有两种选择：
1. 修改代码使其符合规范（如果规范是正确的）
2. 更新规范使其反映真实情况（如果规范有误）

**不允许**存在"代码是对的、规范也是对的，但它们不一致"的状态。

### 每次迭代都沉淀
每一轮 MVP 测试或代码修改后，问自己：是否有新的认知需要写入规范文档？如果没有，说明这轮迭代只产生了代码，没有产生知识。

### 施工严格参照蓝图
Layer 6 的施工代码中，每个 API 端点都应能追溯到 Layer 4 的 Backend API Spec，每个页面组件都应能追溯到 Frontend Design Spec。蓝图没有定义的，不要实现；蓝图定义的，必须实现。

### 环境隔离是纪律
每个独立组件使用各自技术栈的标准隔离机制（见 Layer 5 技术栈映射表）。不要为了省事把依赖混在一起——隔离的代价是初始化时的几分钟，但环境混乱的代价是隐蔽且不可预估的。

## 参考资源

- `references/methodology.md` — 7 层方法论的详细展开，含会话 eb2a0fa2 的真实案例
- `references/agent-templates/` — chatbot-planner/coder/reviewer 的配置模板
- 项目 Memory（`.claude/projects/<project>/memory/`）— 能力边界评估等长期记忆

**外部参考**（与本方法论互补的资源汇编与运行时）：
- `ai-boost/awesome-harness-engineering` — 按 25 问题类别组织的 harness engineering 资源汇编，可作为 L0/L1 能力边界自检的扩展索引
- `walkinglabs/awesome-harness-engineering` + 配套 `learn-harness-engineering` — 提出 instructions/tools/environment/state/feedback 五子系统框架，已并入本 skill L5 自检
- `HKUDS/OpenHarness` — Python 实现的开源 Agent harness（Claude Code 兼容工具栈），可作为 L6 施工的可选执行容器
