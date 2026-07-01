# Social Media Skills for Cursor Agent

This repository is configured with a collection of AI agent skills and MCP servers for retrieving information from domestic and international social media platforms.

## Installed Skills (`~/.cursor/skills/`)

| Skill | Platforms | Type |
|---|---|---|
| `agent-reach` | Twitter/X, YouTube, Reddit, Bilibili, 小红书, 抖音, 微信, LinkedIn, RSS | Agent Skill (SKILL.md) |
| `last30days-skill-cn` | 微博, 小红书, B站, 知乎, 抖音, 微信公众号, 百度, 头条 | Agent Skill |
| `all-in-one` | 小红书, 微博, 抖音 | CLI (`aione`) + Agent Skill |
| `tikomni-skills` | 抖音, 小红书, 快手, Bilibili, 微博, TikTok, YouTube, Instagram, X, Reddit, LinkedIn, 微信, 知乎 等20+平台 | Agent Skill |
| `social-superpowers-mcp` | X/Twitter, Reddit | MCP Server (hosted, free) |
| `socialcrawl-mcp` | 42 platforms including all major social media | MCP Server (requires API key) |

## MCP Servers (`.cursor/mcp.json`)

### `social-superpowers` — Free, no API key needed
- **Endpoint:** `https://superpowers.social/mcp`
- **Platforms:** X/Twitter (5 tools), Reddit (7 tools)
- **Tools:** `twitter-search`, `reddit-search`, `reddit-get-post`, etc.

### `socialcrawl` — 42 platforms, API key required
- **Binary:** `~/.cursor/skills/socialcrawl-mcp/dist/index.js`
- **Required secret:** Set `SOCIALCRAWL_API_KEY` in Cursor Settings → Cloud Agents → Secrets
- **Platforms:** TikTok, Instagram, YouTube, Twitter/X, Reddit, LinkedIn, GitHub, HackerNews, Amazon, Tripadvisor, Naver, and 30+ more

## API Keys Required

Some skills require API keys or authentication cookies:

| Service | Environment Variable | Where to Set |
|---|---|---|
| SocialCrawl (42 platforms) | `SOCIALCRAWL_API_KEY` | Cursor Settings → Secrets |
| TikOmni (20 platforms) | `TIKOMNI_API_KEY` | `~/.cursor/skills/tikomni-skills/skills/.env` |
| All-IN-ONE (小红书/微博/抖音) | Cookie auth | `aione auth <platform> set-cookie --cookie "..."` |

## Python Dependencies Installed

- `jieba` — Chinese text segmentation (for last30days-skill-cn)
- `playwright` + Chromium — Browser automation for crawling
- `yt-dlp` — YouTube/Bilibili video info & subtitles
- `feedparser` — RSS feed parsing
- `miku_ai` — WeChat public account article search
- `aione` CLI — All-IN-ONE platform operations

## Quick Usage Examples

```
# Search Reddit and X for a topic (via social-superpowers MCP)
"Search Reddit for discussions about AI agents"

# Search Chinese platforms (via last30days-skill-cn skill)
"搜索小红书最近30天关于AI工具的内容"

# Get YouTube video transcript (via agent-reach)
"Get the transcript of this YouTube video: https://youtube.com/..."

# Search across 小红书/微博/抖音 (via All-IN-ONE aione CLI)
aione xhs note search --query "AI工具" --output json
```
