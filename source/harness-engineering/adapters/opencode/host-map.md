# OpenCode Host Map

## 入口判断

在开始执行前，先完成同一套入口判定：

1. 判定当前阶段：搭建期（Layer 0-6）或维护期。
2. 判定当前层与目标层：只允许跨过已通过 Gate 的层。
3. 判定输入是否齐全：需求、约束、验收标准、现有资产位置。
4. 若任一项不明确，回到 Layer 0 先补齐边界与事实，不直接编码。

## 能力边界

OpenCode 端按以下边界落地：

- 探索与取证：`Read`、`Grep`、`Glob`。
- 修改代码：优先 `Edit`，仅在必要时 `Write` 新文件。
- 执行验证：`Bash` 运行测试、构建、脚本与检查命令。
- 任务编排：`TaskCreate/TaskUpdate` 跟踪步骤；复杂研究用 `Agent`。
- 高风险动作：任何不可逆或高影响操作先确认，不绕过安全约束。

## 宿主映射

- 项目级宿主指引文件：仓库根目录 `AGENTS.md`
- 组件级局部指引文件：需要独立运行或独立环境的组件目录内 `AGENTS.md`
- Agent 配置目录：`.opencode/agents/`
- 角色到固定 agent 名称的映射：规划 = `chatbot-planner`，实现 = `chatbot-coder`，审查 = `chatbot-reviewer`，调试 = `chatbot-debugger`
- 模板来源：`references/agent-templates/`

## 危险动作约束

- 不可逆操作（如强制覆盖、批量删除、重写历史）执行前必须确认。
- 对共享环境有影响的动作（如推送、发布、修改 CI/权限）执行前必须确认。
- 不绕过测试、签名、审查与安全钩子。
