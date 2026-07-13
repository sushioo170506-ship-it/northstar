---
name: source_snapshot
description: 将检索结果冻结为带时间、原文与SHA-256的不可变来源快照并执行场景来源策略。
license: MIT
version: 1.0.0
---

# Source Snapshot

输入`research`、`writing_standards`和`outline`，输出`source_snapshot`。

## 硬规则

1. 每项来源必须保存标题、原始URL、正文、抓取时间、Provider和SHA-256。
2. 空正文、缺标题或缺URL标记`snapshot_complete=false`，不得视为完整证据。
3. 来源要求按场景区分：技术以学术来源为核心；投研要求产业/一手信息与独立方法来源；
   公众号要求事实来源与真实反馈；官方内参要求法规、标准或授权一手来源。
4. 后续证据治理、论断验证和质量门必须引用快照哈希，不直接信任可漂移网页。

## 统一输出格式约束

JSON产物不得破坏来源URL、正文、发布时间、issue_ids、claim_key和下游引用所需字段。
