# Claude Code Host Map

## 入口判断

在开始执行前，先完成同一套入口判定：

1. 判定当前模式：`bootstrap` 或 `maintenance`。
2. 选择最小合法起始层：只允许从当前问题实际失效的最早层重入。
3. 判定当前层与目标层：只允许跨过已通过 Gate 的层。
4. 判定输入是否齐全：需求、约束、验收标准、现有资产位置。
5. 若任一项不明确，回到 Layer 0 先补齐边界与事实，不直接编码。

## 读取范围

- 先读 canonical 入口 `SKILL.md`，再按当前 scope 补读 `core/*` 与本适配层文件。
- 维护期只读本次起始层及其必要上游/下游材料，不把全套文档当默认前置。
- 宿主层补充的是 Claude Code 的执行映射，不改写 7-layer 定义、Gate 本体与回滚方法论。

## Gate 与证据

- 每个 touched layer 都要显式记录 `pass`、`fail` 或 `not-run`，并给出对应证据。
- 没有证据不得宣称通过；证据不足时保持在当前层，不向下推进。
- 下游失败若否定上游假设，只回退到最小必要上游层重做，不整链重跑。

## 结束状态

- 收尾时必须报告 touched layers、每层证据指针、是否发生 rollback，以及最终 operation state。
- operation state 至少显式区分：`bootstrap_exited`、`maintenance_exited`、`maintenance_continues`。

## 能力边界

Claude Code 端按以下边界落地：

- 探索与取证：`Read`、`Grep`、`Glob`。
- 修改代码：优先 `Edit`，仅在必要时 `Write` 新文件。
- 执行验证：`Bash` 运行测试、构建、脚本与检查命令。
- 任务编排：`TaskCreate/TaskUpdate` 跟踪步骤；复杂研究用 `Agent`。
- 高风险动作：任何不可逆或高影响操作先确认，不绕过安全约束。

## 宿主映射

- 项目级宿主指引文件：仓库根目录 `CLAUDE.md`
- 组件级局部指引文件：需要独立运行或独立环境的组件目录内 `CLAUDE.md`
- Agent 配置目录：`.claude/agents/`
- 角色到固定 agent 名称的映射：规划 = `chatbot-planner`，实现 = `chatbot-coder`，审查 = `chatbot-reviewer`，调试 = `chatbot-debugger`
- 模板来源：`references/agent-templates/`

## 危险动作约束

- 不可逆操作（如强制覆盖、批量删除、重写历史）执行前必须确认。
- 对共享环境有影响的动作（如推送、发布、修改 CI/权限）执行前必须确认。
- 不绕过测试、签名、审查与安全钩子。
