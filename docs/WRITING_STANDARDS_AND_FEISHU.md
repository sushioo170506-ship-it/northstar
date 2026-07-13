# 分场景写作标准与飞书集成

## 1. 写作标准体系

代码事实源为 `standards_store.BUILTIN_PROFILES`，执行节点为 `writing_standards`。每个Profile均
包含稳定ID、不可变版本、场景、调用触发词、规则、依据来源和启用状态；运行时把实际使用的
Profile ID/版本写入产物元数据和应用审计。

| 一键调用ID | 场景 | 关键规范 | 参照核验 |
|---|---|---|---|
| `technical_arxiv` | 技术/学术报告 | 摘要、引言、相关工作、方法、实验、结果、局限、结论；术语表、LaTeX公式、复现实验 | 至少3篇同领域论文，记录arXiv ID、版本、URL和领域 |
| `industry_investment` | 行业/投研 | 产业链—供需—竞争—盈利—估值—催化—风险闭环；口径、敏感性和证伪条件 | 领域前三参照须有榜单来源、日期、报告链接和擅长领域 |
| `wechat_public_account` | 公众号 | 标题信息增量、前100字钩子、移动端节奏、互动与素材版权 | 蓝V主页、认证状态、样文和核验日期均可追溯 |
| `official_internal` | 公文/内参 | 文种、行文关系、版头/主体/版记、规范用语、阅读范围和密级 | 现行条例、GB/T 9704-2012及组织制度 |

arXiv是预印本平台，不提供跨学科统一的“完整写作规范”。本Profile以同领域论文结构和arXiv
技术提交要求为参照，目标会议/期刊模板仍具有最终优先级。券商和蓝V名单会变化，系统不会把
固定通用名单冒充“细分领域前三”；缺少核验字段时状态为`verification_required`。可通过
`extra.require_verified_reference_templates=true`把该状态升级为发布硬门。

官方/内参依据：

- [《党政机关公文处理工作条例》](https://www.gov.cn/zhengce/2013-02/22/content_2640088.htm)
- [GB/T 9704-2012《党政机关公文格式》](https://xb.njupt.edu.cn/_upload/article/files/fd/b9/c197ce7e46b6aaf3975ef0208764/90db11e7-2645-4757-920a-9bb2b311ba20.pdf)

技术报告依据：

- [arXiv TeX提交说明](https://info.arxiv.org/help/submit_tex.html)
- [arXiv引用标识说明](https://info.arxiv.org/help/faq/references.html)

## 2. 个性化标准的落地与调用

创建工作流时可同步注册个性化Profile：

```python
workflow_id = workflow.create({
    "topic": "董事会AI治理简报",
    "output_type": "内部政策简报",
    "extra": {
        "writing_standard": {
            "id": "board_ai_memo",
            "name": "董事会AI治理简报",
            "scene": "official_internal",
            "trigger_keywords": ["董事会", "AI治理简报"],
            "rules": {
                "required_sections": [
                    "标题", "主送或阅读范围", "正文", "建议事项", "责任人", "署名与日期"
                ],
                "language": "先结论后依据，每项建议写责任人和完成条件"
            },
            "references": []
        }
    }
})
```

编排器将其写入`standards.db`，并把`extra.writing_standard_profile`固定为新Profile ID。后续可：

```python
profiles = workflow.list_writing_standards()
workflow_id = workflow.create({
    "topic": "专题",
    "extra": {"writing_standard_profile": "board_ai_memo"}
})
```

同一ID再次注册会创建新版本并停用旧版本，不覆盖历史；已执行工作流仍记录当时版本。审核通过
的`experience_evolution`提案若路由至`writing_standards`，会同时进入Skill受控区和Profile的
`managed_learnings`，且仍要求人工`approved_by`。`standards.db`必须与`state.db`、`vectors.db`
一起备份。

## 3. 飞书对接前置配置

### 3.1 创建应用

1. 在飞书开放平台创建企业自建应用，记录App ID；App Secret只放Secret Manager。
2. 在“权限管理”申请最小权限：
   - `docx:document`（创建及编辑新版文档）；
   - `docx:document.block:convert`（Markdown转文档块）；
   - `sheets:spreadsheet`（写值、样式、冻结行和回读）；
   - 仅在需要指定或管理已有文件夹时追加相应Drive权限。
3. 个人测试可在开发者后台切换“测试版/测试企业”，以应用开发者自己的
   `user_access_token`免审调试支持的用户权限；正式面向企业成员发布时仍须提交管理员审核。
4. 如果写入个人空间，推荐完成OAuth并传入`user_access_token`；它的资源范围与授权用户一致。
   无人值守组织自动化可用`tenant_access_token`，但应用只能访问已授权资源或应用创建的文件夹。
5. 写入已有文档/文件夹时，将应用或授权用户设为可编辑协作者。目标租户、数据驻留、保留期和
   删除策略必须经过组织审批。

相关官方接口：

- [获取访问凭证](https://open.feishu.cn/document/server-docs/api-call-guide/calling-process/get-access-token)
- [创建新版文档](https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document/create)
- [Markdown转文档块](https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/document-docx/docx-v1/document/convert)
- [创建嵌套块](https://open.feishu.cn/document/docs/docs/document-block/create-2)
- [电子表格写值](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/write-data-to-a-single-range)
- [单元格样式](https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/set-cell-style)

### 3.2 凭证与实例化

不得把密钥写入`ReportConfig`、源码、日志或产物。应用身份示例：

```python
import os
from research_workflow import (
    FeishuApiClient, FeishuDocumentRenderer, ResearchReportOrchestrator,
)

client = FeishuApiClient(
    app_id=os.environ["FEISHU_APP_ID"],
    app_secret=os.environ["FEISHU_APP_SECRET"],
)
renderer = FeishuDocumentRenderer(
    client,
    title="研究报告",
    folder_token=os.environ.get("FEISHU_FOLDER_TOKEN"),
)
workflow = ResearchReportOrchestrator(
    "./data",
    document_renderer=renderer,
)
```

个人空间使用内置`FeishuOAuthClient`：

```python
from research_workflow import FeishuOAuthClient, FeishuApiClient

oauth = FeishuOAuthClient(app_id, app_secret, redirect_uri)
url, state = oauth.authorization_url()
# 浏览器打开url；飞书回调redirect_uri?code=...&state=...
token = oauth.exchange_code(code)
client = FeishuApiClient(
    access_token=token["access_token"],
    auth_mode="user_oauth",
)
# token含refresh_token时，可在过期前调用oauth.refresh(refresh_token)
```

OAuth接口为`https://open.feishu.cn/open-apis/authen/v2/oauth/token`，授权码仅可使用一次且
有效期短。App Secret、access_token和refresh_token只能放入Secret Manager或权限为600的
本地凭证文件，禁止进入ReportConfig、数据库、日志和Git。

工作流配置：

```json
{
  "topic": "行业研究",
  "output_format": "feishu",
  "confidentiality_level": "internal",
  "extra": {
    "feishu_target_tenant_confirmed": true,
    "feishu_data_residency_approved": true
  }
}
```

`public`可外发；`internal`必须同时满足上述两个审批标志；`secret/confidential/top_secret`
（秘密/机密/绝密）一律禁止飞书发布。该限制是应用安全边界，不代表系统具备涉密资质。

## 4. Markdown表格转换流程

1. `formatting`生成canonical Markdown，不把中间稿冒充飞书文档。
2. `publish`确认质量门和信息安全策略，调用`FeishuDocumentRenderer`。
3. 文本片段调用`/docx/v1/documents/blocks/convert`，移除只读`merge_info`，再创建嵌套块。
4. 每个GFM表格创建Docx `block_type=30`的Sheet Block。创建时行列上限为9；随后Sheets写值
   接口按完整范围写入全部行列。
5. `sheet.token`按最后一个下划线拆成`spreadsheet_token`和`sheet_id`。
6. 将标题行和数据写入原生单元格；`=...`写为公式类型，Markdown链接写为URL类型。
7. 批量设置全边框、表头加粗/底色、左中右对齐及整单元格粗体/斜体/代码底色，冻结首行。
8. 回读相同范围并比较二维数据；不一致则发布失败。成功返回飞书Docx URL和每个Sheet的
   token、sheet ID、range及`readback_verified=true`。

Markdown本身不表达Excel条件格式、合并单元格、筛选视图、列宽或任意CSS；这些不存在的样式
无法“保留”。系统无损保留全部单元格数据和GFM可表达的表头、对齐、整单元格粗斜体、代码、
链接和公式语义。生成的是原生Sheet，用户可直接编辑、筛选、排序和继续计算；不会转换成图片。

## 5. 验收标准

| 项目 | 通过条件 |
|---|---|
| 数据完整性 | 回读二维矩阵与写入矩阵一致；行列数、空单元格、换行和转义管道符不丢失 |
| 样式 | 表头、边框、GFM对齐、整单元格粗斜体/代码样式按映射生效 |
| 链接/公式 | 链接为可点击URL类型；`=...`为公式类型且可继续引用计算 |
| 可编辑性 | 产物是Docx内嵌Sheet Block，不是截图或HTML表格 |
| 筛选计算 | 用户可在飞书中开启筛选、排序，并新增/修改公式 |
| 结构 | Markdown标题、列表、引用和正文顺序不变；表格位于原文位置 |
| 安全 | 密钥不落库；涉密硬阻断；内部资料缺少租户/驻留审批时阻断 |
| 失败语义 | 鉴权、权限、限流、写值、样式或回读失败均令publish失败，不静默降级 |

自动化测试使用可注入Transport模拟飞书响应，验证端点、原生Sheet、公式/URL值、样式、冻结和
回读。真实租户验收还必须用非生产样例执行一次端到端冒烟测试；本仓库没有用户凭证，因此不
宣称已写入任何个人飞书空间。
