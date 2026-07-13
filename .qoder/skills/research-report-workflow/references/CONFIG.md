# Report configuration

Minimal:

```json
{
  "topic": "研究主题",
  "expected_length": 8000,
  "output_format": "markdown",
  "workflow_profile": "deep"
}
```

Recommended:

```json
{
  "topic": "研究主题",
  "expected_length": 8000,
  "style": "专业、客观、证据驱动",
  "output_format": "markdown",
  "output_type": "行业研究报告",
  "audience": "企业管理层",
  "language": "zh-CN",
  "workflow_profile": "deep",
  "confidentiality_level": "internal",
  "content_boundaries": [
    "不得包含未标明来源的数据"
  ],
  "prior_thoughts": "用户已有判断",
  "extra": {
    "sources": [
      {
        "id": "S1",
        "title": "来源标题",
        "category": "industry",
        "url": "https://example.org/original",
        "published_at": "2026-07-01",
        "content": "用于核验的原文内容",
        "issue_ids": ["ISSUE-01"]
      }
    ]
  }
}
```

Supported output formats:

`markdown`, `html`, `json`, `text`, `feishu`, `docx`, `pdf`, `pptx`,
`slides_html`, `slides_zip`.

Profiles:

- `quick`: one confirmation; low-risk drafts only.
- `standard`: outline and pre-review confirmations.
- `deep`: all four confirmations; default for consequential research.
- `regulatory`: all confirmations and stricter quality thresholds.

Source categories are scene-specific. Preserve original URLs and full source
content. Do not put access tokens, API keys, cookies, or passwords in config.
