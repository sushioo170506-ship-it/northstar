| process_id | 关键过程 | 产出成果 | 对决策价值 | 对应结论（conclusion_id） |
|---|---|---|---|---|
| P-01 | 统一来源采集与分层标注（官方/第三方） | `raw_data/source_index.csv` + `references.md` | 消除“来源混杂”导致的可信度争议 | C-04,C-06 |
| P-02 | benchmark 指标汇总与维度覆盖校验 | `raw_data/benchmark_catalog.csv` + `processed_data/tables/benchmark_master_table.md` | 明确能力证据覆盖范围，避免单指标误判 | C-02,C-03,C-07 |
| P-03 | 竞品与定价口径对照 | `competitor_catalog.csv` + `comparison_matrix.md` + `cost_scenario_table.csv` | 建立成本-能力-风险三角比较基线 | C-02,C-03,C-06 |
| P-04 | 部署门禁与路由策略设计 | `deployment_gate_checklist.md` + `roadmap_90d.md` | 将抽象结论转为可执行上线策略 | C-01,C-08 |
| P-05 | 风险登记与治理映射 | `risk_register.md` + `capability_governance_dualtrack.md` | 明确风险责任与缓解动作，降低上线不确定性 | C-05,C-08 |
| P-06 | 证据回链与台账审计 | `evidence_map.csv` + `evidence_ledger.csv` | 保证每条核心结论可追溯和可复核 | C-01,C-04,C-07 |
| P-07 | 加权评分卡与最终复核 | `decision_scorecard.md` + `review_checklist.md` | 将“可用性判断”转为量化决策门槛 | C-04,C-08 |
| P-08 | 多格式发布一致性检查 | `output/report.md` + `output/report.docx` + `output/decision_brief.md` | 确保跨读者渠道的结论口径一致 | C-01,C-04 |
