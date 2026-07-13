---
name: claim_verification
description: 将每项论断对齐到不可变原文片段，核验数字、独立来源和冲突并生成发布硬门。
license: MIT
version: 1.0.0
---

# Claim Verification

输入`data_processing`、`source_snapshot`、`evidence_governance`和`outline`，输出
`claim_verification_report`。

## 硬规则

1. 每项论断必须至少定位一段原文证据并保存source_id、原始URL和snapshot_checksum。
2. 论断内全部数字、单位和百分比必须能在支持来源中找到。
3. 关键论断至少两个独立来源；未解决冲突不得发布。
4. 无原文片段、数字不一致、D级证据或关键论断单一来源时标记`blocked`。
5. `quality_gate`必须以`all_claims_verified`为硬门，不以模型自评分替代。

## 统一输出格式约束

JSON产物必须保留claim_id、issue_ids、evidence_spans、数字锚点、验证原因和红线。
