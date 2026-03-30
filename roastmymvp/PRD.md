# AI Beta Test — Product Requirements Document

**Version:** 1.0
**Date:** 2026-03-27
**Author:** jincinga24
**Status:** Living document

---

## 1. Vision

A CLI tool that lets any developer run AI-simulated beta testing on their product — finding real bugs, UX friction, and PMF signals without needing real users.

**One-liner:** `ai-beta-test <url> --personas 20` → 10 分钟后拿到完整的内测报告。

**Not a company (yet).** This is a developer tool, open-source first. Anyone building a startup, side project, or prototype can use this to get feedback before launch.

---

## 2. Target Users

| User | Context | What they need |
|------|---------|----------------|
| 独立开发者 | Side project 做完了没人测 | 快速获取 UX 反馈和 bug 报告 |
| 学生创业者 | Prototype 阶段，缺专业视角 | 有人告诉他方向对不对 |
| 小团队 Startup | MVP 上线前 | PMF 信号验证 |
| Hackathon 参赛者 | 48 小时内需要快速迭代 | 即时反馈 |

---

## 3. Core Requirements

### R1: Multi-Input Support
接受多种产品形态作为输入：
- **URL** → Playwright 真实浏览测试
- **截图/图片** → AI 视觉分析
- **PRD/描述文字** → 纯 persona 分析
- **Figma URL** → 截图提取 + 分析

### R2: Three-Layer Testing
每次测试产出三层报告：
- **Layer 1 — 技术测试:** Bug、死链、性能、移动端兼容
- **Layer 2 — UX 体验测试:** 时间到价值、摩擦点、导航清晰度
- **Layer 3 — PMF/战略测试:** 下载意愿、付费意愿、留存信号、竞品对比

### R3: Configurable Personas
用户可自定义目标用户画像：
```bash
ai-beta-test https://example.com \
  --persona "22岁墨大精算学生，中国留学生" \
  --persona "35岁产品经理，已经在用竞品" \
  --count 5  # 每类生成 5 个变体
```

### R4: Scalable Persona Engine
- 20 个深度 persona（定性 — 完整叙事反馈）
- 1,000-10,000 个量化 persona（定量 — JSON 评分）
- 多 LLM 交叉验证（Claude + GPT + Gemini）
- 非理性行为注入（30% persona 带随机约束）

### R5: Structured Report Output
输出 `FEEDBACK-REPORT.md`，包含：
- Bug 列表 + 截图证据
- UX 评分（按维度打分 1-10）
- PMF 信号统计（下载率、付费意愿分布、留存预测）
- 按人群分切的数据
- GO / CONDITIONAL GO / NO-GO 建议

### R6: CLI-First
- `pip install ai-beta-test`
- 一行命令运行
- 零配置即可使用（带默认 persona 模板）
- 支持配置文件 `.ai-beta-test.yaml` 进阶使用

---

## 4. Acceptance Criteria

| ID | Feature | Pass Condition |
|----|---------|----------------|
| AC1 | URL 输入 | 给定任意公开 URL，工具能自动浏览、截图、发现至少 1 个真实问题 |
| AC2 | 深度 persona | 20 个 persona 中至少 3 个产出创始人之前没想到的洞察 |
| AC3 | 量化 persona | 1000 个量化 persona 在 5 分钟内完成，成本 < $1 |
| AC4 | 报告生成 | 自动生成结构化 markdown 报告，人类可读 |
| AC5 | 移动端测试 | 自动检测移动端 UI 问题（溢出、重叠、不可点击） |
| AC6 | 多 LLM | 支持至少 2 种 LLM 后端，结果可对比 |
| AC7 | 自定义 persona | 用户自定义的 persona 描述能产出与该人群相关的反馈 |

---

## 5. MVP Scope

### Do (Sprint 1-3, 3 weeks)

| Feature | Sprint |
|---------|--------|
| Playwright Browser Agent — 自动浏览 URL、截图、发现 bug | Sprint 1 |
| Persona Engine — 20 深度 persona 基于截图+交互数据给反馈 | Sprint 2 |
| Report Generator — 三层报告输出 + CLI 包装 | Sprint 3 |

### Don't Do (v2+)

| Feature | Why Not Now |
|---------|------------|
| Web UI / Dashboard | CLI 先验证价值 |
| 10000 量化 persona | 先验证 20 深度够不够用 |
| 多 LLM 交叉验证 | 先用 Claude 跑通 |
| Figma 输入 | URL + 截图先行 |
| GitHub Action 集成 | CLI 稳定后再做 |
| 校准引擎（AI vs 真实数据对比） | 需要积累数据 |
| 付费 / SaaS | 开源先行 |

---

## 6. Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| 自己觉得有用 | 对自己的 3 个项目跑测试，每次发现 >= 3 个新洞察 | 手动验证 |
| GitHub stars | 100 stars in first month | GitHub |
| 外部用户使用 | 5 个非自己的开发者用过并给反馈 | Issue / Discussion |

## 7. Kill Metrics

| Signal | Action |
|--------|--------|
| 自己用了 3 次觉得反馈都是废话 | 停下来重新想 persona 质量问题 |
| 跑一次成本 > $5 | 优化 prompt 或换模型 |
| 开源 1 个月 0 外部用户 | 验证是不是只有自己需要 |
