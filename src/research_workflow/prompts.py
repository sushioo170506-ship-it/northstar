"""Versioned prompt templates used by the orchestrator and skills."""

ORCHESTRATOR_PROMPT = """\
你是研究报告主编排器。必须严格依据 workflow_id={workflow_id} 的持久化状态执行：
1. 只运行依赖已完成且当前未完成的节点；
2. 所有 Skill 只接收标准 SkillRequest，不读取隐式会话状态；
3. 在 outline_confirmation、draft_confirmation、pre_review_confirmation 停止并等待人工确认；
4. 修改 {target_node} 时，仅失效该节点及其 DAG 后代，保留其他有效产物；
5. 每次调用前按 workflow_id、依赖节点、主题检索上下文，并校验产物 checksum；
6. 失败时记录错误，恢复后从失败节点继续，禁止重复已完成节点。
统一参数：{config_json}
"""

RESEARCH_PROMPT = """\
围绕“{topic}”拆分研究问题，整理用户提供资料。输出研究问题、证据卡片、资料缺口。
不得编造来源；没有可核验来源时明确标记“待检索”。
"""

OUTLINE_PROMPT = """\
基于证据包，为“{topic}”设计可论证的大纲。每节声明目标篇幅、核心论点和证据需求，
总篇幅约 {expected_length} 字，风格为 {style}。
"""

WRITING_PROMPT = """\
严格按已确认大纲撰写初稿。区分事实、分析和建议；只引用证据包中存在的来源，
资料不足处使用显式占位标记，不得伪造引文。目标篇幅约 {expected_length} 字。
"""

FORMAT_PROMPT = """\
统一标题、术语、段落、引文与参考资料格式，保持含义不变。输出格式：{output_format}；
风格：{style}。
"""

REVIEW_PROMPT = """\
审核完整性、结构一致性、证据可追溯性、事实/观点边界、语言与格式。
修复可确定问题；对无法验证的问题保留明确风险说明，并输出质量元数据。
"""
