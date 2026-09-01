# RAG Agent 工具协同平台 Demo

- **基于企业级 RAG Agent 工具协同项目演进背景的个人脱敏复现 Demo。**
- **用于验证 Python 3.10 → Python 3.11 技术栈迭代后的依赖兼容性、Windows 本地运行和核心链路。**
- **全部数据均为虚构和脱敏数据。**
- **不是原公司源码。**
- **不是生产代码，也不代表原生产系统已完成 Python 3.11 升级。**

这是一个企业级项目演进验证口径的个人脱敏 CLI Demo。本仓库当前聚焦 Windows 环境下的中文向量检索、查询阶段 metadata 权限过滤、本地工具治理，以及 LangGraph 人工复核与跨进程恢复；不能据此宣称该 Demo 已达到企业生产级。

## 当前已验证结果

- 8 个直接依赖已锁定并验证：ChromaDB、Sentence Transformers、PyTorch、Transformers、Pydantic、LangGraph 1.2.7、LangGraph SQLite Checkpoint 3.1.0、PyArrow 24.0.0。
- 模型固定为 `BAAI/bge-small-zh-v1.5`，revision 为 `7999e1d3359715c523056ef9478215996d62a620`，512 维，CPU 推理。
- 一条 bootstrap 流程退出码为 0，并完成依赖安装、健康检查、虚构数据生成和 Chroma 入库。
- 根验收 43 项退出码为 0；其中新增 10 项工作流与双进程证据。两次独立入库后的 collection count 均为 `6`，说明相同文档 ID 的 upsert 可重复执行。
- 三个身份的独立 CLI 查询已验证：`readonly-demo` 结果仅含 `public`，`support-demo` 仅含 `public/support`，`admin-demo` 可含 `public/support/admin`。support 查询 top1 为 `troubleshooting-guide`，score 为 `0.546444`。
- 工具与工作流已验证权限前置拦截、Pydantic 参数拒绝、SQLite 唯一约束、同进程重放、两个新 Python 进程重放和双进程并发竞争；同一幂等键只保留一个 `ticket_id`，后续返回 `reused=true`。
- 人工复核链路已验证：副作用工具在 `interrupt` 后才执行；第一个进程返回 `interrupted` 且未建单，第二个新进程使用相同 `thread_id` 和 `Command(resume=...)` 恢复。拒绝不建单，批准建单。
- T2Retrieval 准备器独立测试 15/15 通过；固定 revision 为 `921dd3af6e78d1ae7ee0368aa8d7eaee02c8f08e`，raw 三文件合计 158,846,936 bytes（约 151.5 MiB，页面标称约 159 MB）。本地子集包含 60 个 query 与 3,000 个唯一文档，正例缺失为 0；`corpus.jsonl` SHA-256 为 `6faaf1dd4e344832974667ab827a90a726d5d74795456b11c1df611c2e0dcaa9`，`eval.json` SHA-256 为 `f537297441e329586c7f8a1019aab2ac7716deb61f399c33f61d382103af2c0c`。这些是子集准备证据，尚未运行 Hit@5/MRR，也不填写预设分数。

这些是当前冻结验收结果，不等同于生产可用性、真实业务权限安全性或完整 RAG 质量评测。

## 技术口径与边界

Chroma 是本项目在 Windows 上运行的免 Docker 本地持久化 Demo，便于演示最小检索链路。生产口径是 Milvus 2.x；两者在部署方式、规模、运维和查询能力上存在差异，本 Demo 未在 Milvus 上验证，不能把 Chroma 结果表述为 Milvus 验证结果。

检索函数把可信演示上下文产生的 visibility allowlist 放入 Chroma 的 metadata `where` 条件，在查询阶段限制候选范围，不先召回全部文档再删除。CLI 只接受 `--user-id`，不接受调用方自行传入 role 或 visibility。

当前身份层是三个硬编码演示用户的 fail-closed 映射，不是登录系统、Token 校验或生产 IAM。工具入口会再次核验上下文和角色；这只能证明 Demo 内部权限合同有效，不能证明真实身份认证已经完成。

`score = 1 - cosine distance` 是用于相对排序的分数，不是概率，也不是置信度。6 篇虚构知识仍用于功能链路；外部 T2Retrieval 60×3,000 子集已准备，但评测脚本尚未接入、尚未产生指标，不能称官方完整 T2Ranking 分数或政企业务质量。

## 外部检索评测数据准备

子集来源为 [MTEB 官方 T2Retrieval 分发](https://huggingface.co/datasets/mteb/T2Retrieval/tree/921dd3af6e78d1ae7ee0368aa8d7eaee02c8f08e)，固定 revision 为 `921dd3af6e78d1ae7ee0368aa8d7eaee02c8f08e`，许可证为 Apache-2.0。原始 [THUIR/T2Ranking](https://github.com/THUIR/T2Ranking) 是更大的完整基线；本 Demo 采用约 159 MB 的同源轻量分发，以控制 Windows 本地时间与磁盘占用。

```powershell
& .\.venv\Scripts\python.exe .\scripts\prepare_t2retrieval.py
```

产物位于 `data/external/t2retrieval/raw` 与 `data/external/t2retrieval/subset`。准备器校验文件 size 与 SHA-256，使用项目内路径、流式大小上限、`.part` 文件和原子替换；固定 seed 抽样并先完成正例闭包，manifest 最后提交。外部数据来自搜索日志或网页文本；Apache-2.0 不自动消除隐私和第三方内容边界。本子集只用于技术检索对照，不映射用户、权限或工具评测。

## 快速开始

前置条件：Windows、PowerShell、Python **3.11 x64**。在项目根目录执行一条 bootstrap：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\bootstrap.ps1
```

该命令会创建或复用项目内 `.venv`，安装锁定依赖，运行健康检查，生成 6 篇虚构知识文档，并将它们写入项目内持久化 Chroma。默认数据位于 `data/`，索引位于 `runtime/chroma/`，均为本地生成物。

如需显式指定基础解释器，可在命令末尾追加 `-BasePython "<Python 3.11 x64 的 python.exe 完整路径>"`。

bootstrap 首次触发模型下载时，模型会缓存到项目内 `.cache/`。如果下载失败，可只为当前 PowerShell 进程设置镜像后重试，不要使用 `setx` 修改持久环境：

```powershell
$env:HF_ENDPOINT = "https://hf-mirror.com"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\bootstrap.ps1
```

Windows 没有 symlink 权限时，Hugging Face 缓存仍可工作，但可能占用更多磁盘空间。

入库完成后，可用新进程执行检索示例：

```powershell
& .\.venv\Scripts\python.exe .\scripts\search.py --query "知识中心检索变慢如何处理" --user-id support-demo --top-k 5
```

可用演示身份及代码执行的权限如下：

| user_id | 角色 | 可检索 visibility | `get_service_status` | `create_ticket` |
|---|---|---|---:|---:|
| `admin-demo` | admin | public、support、admin | 允许 | 允许 |
| `support-demo` | support | public、support | 允许 | 允许 |
| `readonly-demo` | readonly | public | 允许 | 拒绝 |

`create_ticket` 是副作用工具，公开 CLI 通过 LangGraph 人工复核后才允许调用；不能绕过复核直接创建。普通知识问答和 `get_service_status` 不触发 interrupt；readonly 创建工单会在复核/工具前被拒绝。

## 人工复核演示

第一个 PowerShell 进程启动工作流，在副作用调用前暂停：

```powershell
& .\.venv\Scripts\python.exe .\scripts\demo.py start --thread-id demo-ticket-001 --user-id support-demo --query "请为智能助手创建工单" --product-id smart-assist --idempotency-key demo-ticket-001
```

预期返回 `status=interrupted`；此时 checkpoint 已保存，但尚未创建工单。请在新的 PowerShell 进程中用相同 `thread_id` 恢复：

```powershell
& .\.venv\Scripts\python.exe .\scripts\demo.py resume --thread-id demo-ticket-001 --decision approve
```

将 `approve` 改为 `reject` 可验证人工拒绝，结果是不创建工单。`start` 与 `resume` 必须复用同一个 `thread_id`；该标识用于定位本地 SQLite checkpoint。

默认 checkpoint 数据库为 `runtime/checkpoints.sqlite`，默认工单数据库为 `runtime/tickets.sqlite`；二者都只用于本地 Demo。

## 工具治理设计

- Pydantic 输入模型拒绝额外字段，统一去除首尾空白，并限制 product ID、摘要和幂等键边界。
- 工具入口执行权限检查；readonly 或伪造上下文在读取产品、创建目录或打开 SQLite 前即被拒绝。
- 稳定错误码包括 `validation_error`、`permission_denied`、`product_not_found`、`database_busy` 和 `internal_error`；普通错误消息不包含 SQL 或本机绝对路径。
- 工单表对 `idempotency_key` 建立 `UNIQUE` 约束。`BEGIN IMMEDIATE`、插入和唯一冲突后的首次 ticket 查询处于同一事务，避免事务外“先查再写”的竞争窗口。

## 数据与代码位置

- `data/knowledge/`：6 篇带固定 front matter 的虚构知识文档，visibility 分布为 `public=3`、`support=2`、`admin=1`。
- `src/retrieval/chroma_store.py`：Markdown 解析、400 字符分块、模型加载、归一化 embedding、Chroma upsert/query、metadata 过滤和 score 转换。
- `src/auth/context.py`：三个虚构演示身份、角色和 visibility allowlist 的不可变映射。
- `src/tools/platform_tools.py`：工具 Schema、静态声明、权限检查、错误映射、服务状态读取和 SQLite 幂等工单。
- `src/agent/workflow.py`：StateGraph 节点、可信上下文、检索、工具决策、权限、人工复核、工具执行、回答和 SQLite checkpoint。
- `scripts/ingest.py`：独立入库 CLI。
- `scripts/search.py`：独立检索 CLI。
- `scripts/prepare_t2retrieval.py`：固定 revision 的外部检索评测子集准备 CLI。
- `scripts/demo.py`：`start`/`resume` 两命令的公开工作流 CLI；异常只输出通用“工作流执行失败”。
- `scripts/bootstrap.ps1`：项目环境、依赖、健康检查、数据生成与入库的一键入口。

## 依赖、来源与许可证

| 包 | 锁定版本 | 来源 | 发布日期 | 许可证 |
|---|---:|---|---|---|
| ChromaDB | 1.5.9 | [PyPI 发行页](https://pypi.org/project/chromadb/1.5.9/) | 2026-05-05 | Apache-2.0 |
| Sentence Transformers | 5.6.0 | [PyPI 发行页](https://pypi.org/project/sentence-transformers/5.6.0/) | 2026-06-16 | Apache-2.0 |
| PyTorch | 2.12.1 | [PyPI 发行页](https://pypi.org/project/torch/2.12.1/) | 2026-06-17 | BSD-style |
| Transformers | 5.12.1 | [PyPI 发行页](https://pypi.org/project/transformers/5.12.1/) | 2026-06-15 | Apache-2.0 |
| Pydantic | 2.12.5 | [PyPI 发行页](https://pypi.org/project/pydantic/2.12.5/) | 2025-11-26 | MIT |
| LangGraph | 1.2.7 | [PyPI 发行页](https://pypi.org/project/langgraph/1.2.7/) | 2026-06-30 | MIT |
| LangGraph Checkpoint SQLite | 3.1.0 | [PyPI 发行页](https://pypi.org/project/langgraph-checkpoint-sqlite/3.1.0/) | 2026-05-12 | MIT |
| PyArrow | 24.0.0 | [PyPI 发行页](https://pypi.org/project/pyarrow/24.0.0/) | 2026-04-21 | Apache-2.0 |
| BGE small zh v1.5 | revision `7999e1d…` | [Hugging Face 固定提交](https://huggingface.co/BAAI/bge-small-zh-v1.5/commit/7999e1d3359715c523056ef9478215996d62a620) | 2023-10-12 | MIT |

项目自身采用 [MIT License](LICENSE)。`requirements.txt` 锁定 8 个直接依赖；传递依赖由 pip 解析，当前还不是完整 lockfile 或 SBOM。

## 版本说明

历史企业项目在 2024—2025 年期间采用 Python 3.10、早期 LangGraph 0.x、Milvus 2.x 和 BGE-M3 口径。当前脱敏验证 Demo 的实际环境为 Python 3.11.16 x64，LangGraph 使用演进后的 `1.2.7` interrupt/checkpointer API，用于验证当前依赖组合在 Windows 本地环境中的兼容性与核心链路。

当前证据只证明该 Demo 在 Python 3.11 本地通过已列验证，不证明原生产环境已经升级到 Python 3.11，也不证明生产迁移验收已经完成。LangGraph 1.2.7 与 SQLite checkpoint 3.1.0 只证明本地 Demo 的 interrupt、恢复和检查点链路，不证明生产升级或生产级持久化。Chroma 仍只是 Windows 与免 Docker 约束下的本地替代方案，本 Demo 没有完成 Milvus 迁移验证。
