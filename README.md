# RAG Agent 工具协同平台 Demo

- **基于企业级 RAG Agent 工具协同项目演进背景的个人脱敏复现 Demo。**
- **用于验证 Python 3.10 → Python 3.11 技术栈迭代后的依赖兼容性、Windows 本地运行和核心链路。**
- **全部数据均为虚构和脱敏数据。**
- **不是原公司源码。**
- **不是生产代码，也不代表原生产系统已完成 Python 3.11 升级。**

这是一个企业级项目演进验证口径的个人脱敏 CLI Demo，当前只完成本地 Chroma 持久化、中文向量检索、文档 metadata 过滤和可复现最小验证链路。当前仅有 6 篇虚构知识文档；工具调用、LangGraph 编排、MCP 和评测仍未实现，不能据此宣称该 Demo 已达到企业生产级。

## 当前已验证结果

- 依赖锁定并验证：`chromadb==1.5.9`、`sentence-transformers==5.6.0`、`torch==2.12.1`、`transformers==5.12.1`。
- 模型固定为 `BAAI/bge-small-zh-v1.5`，revision 为 `7999e1d3359715c523056ef9478215996d62a620`，512 维，CPU 推理。
- 一条 bootstrap 流程退出码为 0，并完成依赖安装、健康检查、虚构数据生成和 Chroma 入库。
- 18 个测试退出码为 0；两次独立入库后的 collection count 均为 `6`，说明相同文档 ID 的 upsert 可重复执行。
- 独立 support 查询的 top1 为 `troubleshooting-guide`，score 为 `0.546444`；public 查询结果 visibility 仅为 `public`；admin 查询结果仅为 `admin-operations`。

这些是当前冻结验收结果，不等同于生产可用性、真实业务权限安全性或完整 RAG 质量评测。

## 技术口径与边界

Chroma 是本项目在 Windows 上运行的免 Docker 本地持久化 Demo，便于演示最小检索链路。生产口径是 Milvus 2.x；两者在部署方式、规模、运维和查询能力上存在差异，本 Demo 未在 Milvus 上验证，不能把 Chroma 结果表述为 Milvus 验证结果。

检索函数把 `visibility` 放入 Chroma 的 metadata `where` 条件，在查询阶段限制候选范围。命令行的 `--visibility` 只是检索边界输入，不是可信的角色鉴权；角色到 visibility 的映射及真正的身份认证后续实现。

`score = 1 - cosine distance` 是用于相对排序的分数，不是概率，也不是置信度。当前只有 6 篇文档，不能据此宣称通用召回率、Hit@5、MRR 或线上质量。

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
& .\.venv\Scripts\python.exe .\scripts\search.py --query "知识中心检索变慢如何处理" --visibility public --visibility support --top-k 5
```

多个可见性值可重复传入 `--visibility`。示例中的值仍是调用方提供的边界，不代表角色已被认证或授权。

## 数据与代码位置

- `data/knowledge/`：6 篇带固定 front matter 的虚构知识文档，visibility 分布为 `public=3`、`support=2`、`admin=1`。
- `src/retrieval/chroma_store.py`：Markdown 解析、400 字符分块、模型加载、归一化 embedding、Chroma upsert/query、metadata 过滤和 score 转换。
- `scripts/ingest.py`：独立入库 CLI。
- `scripts/search.py`：独立检索 CLI。
- `scripts/bootstrap.ps1`：项目环境、依赖、健康检查、数据生成与入库的一键入口。

## 依赖、来源与许可证

| 包 | 锁定版本 | 来源 | 发布日期 | 许可证 |
|---|---:|---|---|---|
| ChromaDB | 1.5.9 | [PyPI 发行页](https://pypi.org/project/chromadb/1.5.9/) | 2026-05-05 | Apache-2.0 |
| Sentence Transformers | 5.6.0 | [PyPI 发行页](https://pypi.org/project/sentence-transformers/5.6.0/) | 2026-06-16 | Apache-2.0 |
| PyTorch | 2.12.1 | [PyPI 发行页](https://pypi.org/project/torch/2.12.1/) | 2026-06-17 | BSD-style |
| Transformers | 5.12.1 | [PyPI 发行页](https://pypi.org/project/transformers/5.12.1/) | 2026-06-15 | Apache-2.0 |
| BGE small zh v1.5 | revision `7999e1d…` | [Hugging Face 固定提交](https://huggingface.co/BAAI/bge-small-zh-v1.5/commit/7999e1d3359715c523056ef9478215996d62a620) | 2023-10-12 | MIT |

项目自身采用 [MIT License](LICENSE)。`requirements.txt` 锁定的是四个直接依赖；传递依赖由 pip 解析，当前还不是完整 lockfile 或 SBOM。

## 版本说明

历史企业项目在 2024—2025 年期间采用 Python 3.10、早期 LangGraph 0.x、Milvus 2.x 和 BGE-M3 口径。当前脱敏验证 Demo 的实际环境为 Python 3.11.16 x64，用于验证从 Python 3.10 向 Python 3.11 迁移时，当前依赖组合在 Windows 本地环境中的兼容性与核心链路。

当前证据只证明该 Demo 环境能够在 Python 3.11 本地运行并通过已列测试，不证明原生产环境已经升级到 Python 3.11，也不证明生产迁移验收已经完成。Chroma 仍只是 Windows 与免 Docker 约束下的本地替代方案，本 Demo 没有完成 Milvus 迁移验证。后续 LangGraph interrupt/checkpointer 和 MCP SDK 会采用其演进后的 API 写法，因此不能把 Demo API、版本或单机部署方式等同于历史生产实现。
