# Claude Code Assembly

本文件定义如何把 `harness-engineering` 能力包装配到 Claude Code 宿主。

## 装配目标

在 Claude Code 中提供三层入口：

- 仓库级默认行为：根目录 `CLAUDE.md`
- 组件级局部行为：子目录 `CLAUDE.md`
- 可显式调用的技能入口：`.claude/skills/harness-engineering/SKILL.md`

其中：

- `SKILL.md` 与 `core/*` 是平台无关的规范源。
- `adapters/claude-code/*` 只描述 Claude Code 宿主如何接入这些规范。

## 推荐目录映射

```text
<repo>/
├─ CLAUDE.md
├─ .claude/
│  ├─ skills/
│  │  └─ harness-engineering/
│  │     └─ SKILL.md
│  └─ agents/
│     ├─ chatbot-planner.md
│     ├─ chatbot-coder.md
│     ├─ chatbot-reviewer.md
│     └─ chatbot-debugger.md
└─ <component>/CLAUDE.md
```

## 1. 仓库根 `CLAUDE.md`

用途：

- 让 Claude Code 在未显式调用技能时也遵守 Harness Engineering 的入口判定。
- 规定默认模式判断、最小重入层、文档优先和高风险动作确认。

建议最小模板：

```md
# Repository Instructions

This repository follows the `harness-engineering` superpower.

Before implementation work:

1. Classify the request as `bootstrap` or `maintenance`.
2. Choose the smallest valid start layer.
3. Do not skip a layer gate without evidence.
4. If assumptions fail, roll back to the smallest upstream layer.

When the user explicitly requests the workflow, invoke `/harness-engineering`.
```

## 2. 组件级 `CLAUDE.md`

用途：

- 为独立运行的组件补充局部约束。
- 不重写全局方法论，只补充组件边界、运行入口和验收命令。

建议内容：

- 组件职责和非职责
- 本组件常用运行/测试命令
- 与上游/下游契约的关键边界
- 该组件默认从哪一层重入最常见

## 3. 技能入口 `.claude/skills/harness-engineering/SKILL.md`

用途：

- 让用户通过 `/harness-engineering` 显式触发标准执行编排。
- 把平台无关规范压缩成 Claude Code 可执行指令。

技能入口应：

- 引用 `SKILL.md`
- 引用 `core/layer-details.md`
- 引用 `core/flow.md`
- 引用 `core/layer-details.md`
- 引用 `core/checklists.md`
- 引用 `core/exit-and-reentry.md`
- 要求先做 mode + start layer 判定，再决定是否编码
- 要求按 scope 选择读取材料，不把全套文档设为默认前置
- 要求每个 touched layer 记录 `pass/fail/not-run` 与证据
- 要求失败时执行最小回滚，而不是抽象地“返回上一步”
- 要求结束时报告 touched layers、evidence pointers 与 final operation state

## 4. Agents 装配

建议把角色模板复制到 `.claude/agents/`：

- `references/agent-templates/chatbot-planner.md` -> `.claude/agents/chatbot-planner.md`
- `references/agent-templates/chatbot-coder.md` -> `.claude/agents/chatbot-coder.md`
- `references/agent-templates/chatbot-reviewer.md` -> `.claude/agents/chatbot-reviewer.md`
- 如需调试角色，再补 `.claude/agents/chatbot-debugger.md`

角色约定：

- 规划类问题优先 planner
- 落地实现优先 coder
- 评审与风险扫描优先 reviewer
- 长链调试再启用 debugger

## 5. 推荐技能入口模板

以下内容可直接作为 `.claude/skills/harness-engineering/SKILL.md` 初稿：

```md
---
name: harness-engineering
description: Run the Harness Engineering workflow with explicit mode, layer gates, rollback discipline, and readiness checks.
---

# Harness Engineering

Use this skill when the task requires structured execution rather than direct ad hoc coding.

## Required behavior

1. Classify the request as `bootstrap` or `maintenance`.
2. Select the smallest valid start layer using `core/flow.md`.
3. Read only the core and adapter files needed for the chosen scope.
4. Do not advance across a layer without pass evidence.
5. If a downstream failure invalidates an upstream assumption, roll back minimally.
6. Before closing, confirm touched layers, evidence, and final operation state.

## Canonical references

- `SKILL.md`
- `core/layer-details.md`
- `core/flow.md`
- `core/checklists.md`
- `core/exit-and-reentry.md`
- `adapters/claude-code/host-map.md`

## Claude Code execution notes

- Use task tracking for multi-step work.
- Use agents only when the task is broad enough to justify delegation.
- Ask before irreversible or shared-state actions.
- Prefer the smallest possible layer re-entry during maintenance.
```

## 6. 不应放进宿主装配层的内容

以下内容保持在平台无关层，不写死到 Claude Code 模板中：

- 7-layer 的规范定义本体
- Gate 判定细则本体
- 证据判定标准本体
- 回滚方法论本体
- operation state 的 canonical 语义本体
- 产品契约或具体项目业务规则

这些内容统一留在 `SKILL.md` 与 `core/*`。

## 7. 最小可运行装配顺序

1. 在仓库根创建或更新 `CLAUDE.md`，加入 Harness Engineering 默认约束。
2. 在 `.claude/skills/harness-engineering/` 放入 `SKILL.md`。
3. 在 `.claude/agents/` 放入 planner/coder/reviewer 模板。
4. 对需要独立约束的组件补局部 `CLAUDE.md`。
5. 通过一次 `/harness-engineering` 真实调用验证：mode 判定、最小起始层、evidence 记录、minimal rollback 与 final operation state 都能被报告。
