"""Versioned writing-standard profiles stored independently from workflow runs."""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .storage import utc_now


@dataclass(frozen=True)
class WritingStandardProfile:
    id: str
    version: int
    scene: str
    name: str
    trigger_keywords: tuple[str, ...]
    rules: dict[str, Any]
    references: tuple[dict[str, Any], ...]
    source: str = "builtin"
    active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


BUILTIN_PROFILES = (
    WritingStandardProfile(
        id="technical_arxiv",
        version=1,
        scene="technical",
        name="技术型报告 / arXiv-compatible",
        trigger_keywords=(
            "技术报告", "论文", "学术", "arxiv", "模型架构", "实验报告",
            "technical", "paper",
        ),
        rules={
            "required_sections": [
                "摘要", "引言", "相关工作", "方法", "实验设置", "结果与讨论",
                "局限", "结论",
            ],
            "abstract": "交代问题、方法、主要结果和边界，不引用未在正文验证的结论",
            "citations": "同一领域统一采用作者-年份或数字顺序制；arXiv标识保留版本号",
            "terminology": "首现定义术语和缩写；全文保持唯一译名；维护符号表",
            "formula": "独立公式使用LaTeX块 $$...$$，编号公式在正文逐一引用并解释变量",
            "experiments": "披露数据集、基线、指标、消融、统计不确定性和可复现配置",
            "prohibited": ["把arXiv收录等同同行评审", "只报最优结果", "隐去负面结果"],
            "reference_selection": (
                "按细分领域选取近期、同任务、可复现的arXiv论文作为结构参照；"
                "arXiv是预印本平台，不是统一文体标准，最终格式应服从目标会议或期刊"
            ),
        },
        references=(
            {
                "title": "arXiv TeX submission guidance",
                "url": "https://info.arxiv.org/help/submit_tex.html",
                "authority": "arXiv",
            },
            {
                "title": "References to and in arXiv documents",
                "url": "https://info.arxiv.org/help/faq/references.html",
                "authority": "arXiv",
            },
        ),
    ),
    WritingStandardProfile(
        id="industry_investment",
        version=1,
        scene="industry_investment",
        name="行业研究 / 投研报告",
        trigger_keywords=(
            "行业研究", "投研", "证券", "券商", "估值", "etf", "基金",
            "investment", "equity research",
        ),
        rules={
            "required_sections": [
                "核心观点", "行业框架", "市场空间与驱动", "竞争格局", "数据验证",
                "估值分析", "风险与催化", "结论与建议",
            ],
            "framework": "产业链—供需—竞争—盈利—估值—催化—风险闭环",
            "data_logic": "每项数据写明口径、期间、单位、来源，并完成同比/环比/同业比较",
            "conclusion_logic": "事实→驱动机制→盈利或政策传导→情景判断→可证伪条件",
            "valuation": (
                "按对象适用性选择PE/PB/EV-EBITDA/DCF/SOTP；披露关键假设、"
                "同业口径、敏感性和不适用条件，不输出无来源目标价"
            ),
            "broker_reference_policy": (
                "每个细分领域须基于有日期和来源的研究实力榜单或公开获奖记录，"
                "选取三家在该领域有代表性的券商旗舰报告；不得把通用名单冒充领域前三"
            ),
            "prohibited": ["无来源排名", "只给点估值不做敏感性", "把相关性写成因果"],
        },
        references=(),
    ),
    WritingStandardProfile(
        id="wechat_public_account",
        version=1,
        scene="public_account",
        name="公众号推文",
        trigger_keywords=(
            "公众号", "微信推文", "蓝v", "传播稿", "新媒体", "wechat",
            "public account",
        ),
        rules={
            "required_sections": ["标题", "导语", "核心叙事", "关键数据卡片", "结语与互动"],
            "headline": "具体对象+信息增量或认知冲突；不使用虚假悬念和绝对化标题",
            "rhythm": "前100字给结论或冲突；每300–500字设置小标题、案例或数据停顿",
            "interaction": "结尾给可回答的问题、收藏/转发理由；不得诱导或虚构身份背书",
            "layout": "短段落、三级以内标题、重点加粗克制；移动端图表需有替代文本",
            "media": "封面、信息图、引用卡片均记录来源、版权和适配尺寸",
            "creator_reference_policy": (
                "只使用平台可核验蓝V身份、领域匹配且有稳定原创记录的账号；"
                "记录账号主页、核验日期和样文链接，不把粉丝量等同专业性"
            ),
            "prohibited": ["标题党", "无来源截图", "虚构蓝V背书", "诱导分享"],
        },
        references=(),
    ),
    WritingStandardProfile(
        id="official_internal",
        version=1,
        scene="official_internal",
        name="官方公文 / 企业内参",
        trigger_keywords=(
            "公文", "内参", "政务", "报告", "请示", "通知", "函", "纪要",
            "监管", "领导", "official", "internal memo",
        ),
        rules={
            "required_sections": ["标题", "主送或阅读范围", "正文", "建议事项", "署名与日期"],
            "document_type": (
                "先判定文种；请示一文一事，报告不得夹带请示，通知/函/纪要按职权行文"
            ),
            "format": "版头、主体、版记及A4版式遵循GB/T 9704-2012；企业内参标注版本和阅读范围",
            "language": "准确、简明、庄重、可执行；机构名、数字、计量单位和政策名称使用规范全称",
            "confidentiality": (
                "涉密公文标注份号、密级和保密期限，只能在符合保密规定的系统中处理和传输"
            ),
            "prohibited": ["越级行文未抄送", "报告夹带请示", "在公共云处理国家秘密"],
        },
        references=(
            {
                "title": "党政机关公文处理工作条例",
                "url": "https://www.gov.cn/zhengce/2013-02/22/content_2640088.htm",
                "authority": "中国政府网",
            },
            {
                "title": "GB/T 9704-2012 党政机关公文格式",
                "url": (
                    "https://xb.njupt.edu.cn/_upload/article/files/fd/b9/"
                    "c197ce7e46b6aaf3975ef0208764/90db11e7-2645-4757-920a-9bb2b311ba20.pdf"
                ),
                "authority": "国家标准",
            },
        ),
    ),
)


class SQLiteWritingStandardStore:
    """Durable, queryable profile library with immutable version history."""

    def __init__(self, path: str | Path) -> None:
        self._memory = str(path) == ":memory:"
        self.path = Path(path)
        self._memory_connection: sqlite3.Connection | None = None
        if not self._memory:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()
        self._seed()

    def _connect(self) -> sqlite3.Connection:
        if self._memory:
            if self._memory_connection is None:
                self._memory_connection = sqlite3.connect(":memory:")
            db = self._memory_connection
        else:
            db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        if not self._memory:
            db.execute("PRAGMA journal_mode=WAL")
        return db

    def _init_schema(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS writing_standard_profiles (
                    id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    scene TEXT NOT NULL,
                    name TEXT NOT NULL,
                    trigger_keywords_json TEXT NOT NULL,
                    rules_json TEXT NOT NULL,
                    references_json TEXT NOT NULL,
                    source TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (id, version)
                );
                CREATE INDEX IF NOT EXISTS idx_writing_standard_active
                    ON writing_standard_profiles(scene, active, version);
                CREATE TABLE IF NOT EXISTS writing_standard_applications (
                    id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    profile_id TEXT NOT NULL,
                    profile_version INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def _seed(self) -> None:
        for profile in BUILTIN_PROFILES:
            self.upsert(profile, replace=False)

    def upsert(
        self, profile: WritingStandardProfile, *, replace: bool = False
    ) -> WritingStandardProfile:
        if not profile.id or not profile.scene or not profile.trigger_keywords:
            raise ValueError("写作标准必须包含 id、scene 和 trigger_keywords")
        if not isinstance(profile.rules, dict) or not profile.rules:
            raise ValueError("写作标准 rules 必须是非空对象")
        verb = "INSERT OR REPLACE" if replace else "INSERT OR IGNORE"
        with self._connect() as db:
            db.execute(
                f"""
                {verb} INTO writing_standard_profiles
                (id,version,scene,name,trigger_keywords_json,rules_json,
                 references_json,source,active,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    profile.id,
                    profile.version,
                    profile.scene,
                    profile.name,
                    json.dumps(profile.trigger_keywords, ensure_ascii=False),
                    json.dumps(profile.rules, ensure_ascii=False),
                    json.dumps(profile.references, ensure_ascii=False),
                    profile.source,
                    int(profile.active),
                    utc_now(),
                ),
            )
        return profile

    def register_custom(
        self,
        *,
        name: str,
        scene: str,
        trigger_keywords: list[str] | tuple[str, ...],
        rules: dict[str, Any],
        references: list[dict[str, Any]] | tuple[dict[str, Any], ...] = (),
        profile_id: str | None = None,
    ) -> WritingStandardProfile:
        clean_triggers = tuple(
            dict.fromkeys(
                " ".join(str(item).split()).lower()
                for item in trigger_keywords
                if str(item).strip()
            )
        )
        if not clean_triggers:
            raise ValueError("个性化写作标准至少需要一个调用触发词")
        profile_id = profile_id or f"custom_{uuid.uuid4().hex[:12]}"
        prior = self.get(profile_id, required=False)
        profile = WritingStandardProfile(
            id=profile_id,
            version=(prior.version + 1 if prior else 1),
            scene=scene.strip().lower(),
            name=name.strip(),
            trigger_keywords=clean_triggers,
            rules=rules,
            references=tuple(references),
            source="custom",
        )
        if not profile.name:
            raise ValueError("个性化写作标准 name 不能为空")
        with self._connect() as db:
            db.execute(
                "UPDATE writing_standard_profiles SET active=0 WHERE id=?",
                (profile_id,),
            )
        return self.upsert(profile)

    def get(
        self,
        profile_id: str,
        version: int | None = None,
        *,
        required: bool = True,
    ) -> WritingStandardProfile | None:
        query = "SELECT * FROM writing_standard_profiles WHERE id=?"
        params: list[Any] = [profile_id]
        if version is not None:
            query += " AND version=?"
            params.append(version)
        else:
            query += " AND active=1 ORDER BY version DESC LIMIT 1"
        with self._connect() as db:
            row = db.execute(query, params).fetchone()
        if row is None:
            if required:
                raise KeyError(f"写作标准不存在: {profile_id}")
            return None
        return self._decode(row)

    def list_profiles(self, *, active_only: bool = True) -> list[WritingStandardProfile]:
        query = "SELECT * FROM writing_standard_profiles"
        if active_only:
            query += " WHERE active=1"
        query += " ORDER BY source, scene, id, version DESC"
        with self._connect() as db:
            rows = db.execute(query).fetchall()
        return [self._decode(row) for row in rows]

    def resolve(self, query: str, explicit_id: str | None = None) -> WritingStandardProfile:
        if explicit_id:
            profile = self.get(explicit_id)
            assert profile is not None
            return profile
        normalized = query.lower()
        profiles = self.list_profiles()
        scored = [
            (
                sum(
                    3 if keyword == normalized else 1
                    for keyword in profile.trigger_keywords
                    if keyword in normalized
                ),
                profile.source == "custom",
                profile.version,
                profile,
            )
            for profile in profiles
        ]
        score, _, _, selected = max(
            scored, key=lambda item: (item[0], item[1], item[2], item[3].id)
        )
        if score:
            return selected
        fallback = self.get("industry_investment")
        assert fallback is not None
        return fallback

    def record_application(
        self, workflow_id: str, profile: WritingStandardProfile
    ) -> None:
        with self._connect() as db:
            db.execute(
                "INSERT INTO writing_standard_applications VALUES (?,?,?,?,?)",
                (
                    str(uuid.uuid4()),
                    workflow_id,
                    profile.id,
                    profile.version,
                    utc_now(),
                ),
            )

    def append_managed_rule(
        self, profile_id: str, *, proposal_id: str, rule: str
    ) -> WritingStandardProfile:
        current = self.get(profile_id)
        assert current is not None
        rules = json.loads(json.dumps(current.rules, ensure_ascii=False))
        managed = list(rules.get("managed_learnings", []))
        if not any(item.get("proposal_id") == proposal_id for item in managed):
            managed.append({"proposal_id": proposal_id, "rule": rule})
        rules["managed_learnings"] = managed
        return self.register_custom(
            name=current.name,
            scene=current.scene,
            trigger_keywords=current.trigger_keywords,
            rules=rules,
            references=current.references,
            profile_id=current.id,
        )

    @staticmethod
    def _decode(row: sqlite3.Row) -> WritingStandardProfile:
        return WritingStandardProfile(
            id=row["id"],
            version=int(row["version"]),
            scene=row["scene"],
            name=row["name"],
            trigger_keywords=tuple(json.loads(row["trigger_keywords_json"])),
            rules=json.loads(row["rules_json"]),
            references=tuple(json.loads(row["references_json"])),
            source=row["source"],
            active=bool(row["active"]),
        )
