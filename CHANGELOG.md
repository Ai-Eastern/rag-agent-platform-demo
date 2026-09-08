# Changelog

## v0.1.1-platform-core — 2026-09-09

README 新增中性项目展示层，覆盖业务定位、使用者、业务链路、个人贡献和演示入口；技术证据、评测数字、SHA 值、命令与限制均保留并移至后文。

本次仅为文档发布，不增加产品能力，也不提升证据层级。

## v0.1.0-platform-core — 2026-09-08

个人脱敏的 Windows/Python 3.11 平台核心 CLI Demo 发布说明。

### Included

- 复用现有 `scripts\search.py`：中文向量检索与查询阶段 visibility 过滤。
- 复用现有 `scripts\demo.py`：LangGraph 人工复核、`start`/`resume` 和本地 SQLite checkpoint。
- 复用现有 `scripts\mcp_smoke.py`：通过本地 stdio 发现并调用只读 `get_service_status` 工具。
- 保留虚构知识文档、虚构评测合同、fail-closed 演示身份和工具权限边界。

### Evidence recorded before this release

- 截至 2026-09-05，MCP 接入登记了 `TL-COMPILE`、focused unittest（`Ran 2 tests`、`OK`）、local stdio smoke，以及 `TL-BOUNDARY-STATIC`；该记录的证据层级为 `CHECK_LINT + TEST + 本地 stdio SERVICE_API`。
- README 中列出的检索、工作流、离线缓存和评测数字均保留其原登记日期、数据范围和报告说明；本次文档变更不重新解释为新鲜验证。

### Bounded release verification packet

技术负责人转交的 V1 验证包记录：

- health check exit 0：Python 3.11.16 x64，托管路径为项目内；RAG、LangGraph、MCP、模型和外部服务仍由 health check 单独标记为未验证。
- `compileall src/scripts/tests` exit 0。
- focused MCP unittest exit 0：`Ran 2 tests in 3.457s`、`OK`、failures=0。
- local stdio MCP smoke exit 0：只暴露 `get_service_status`，`status=ok`、`user_id=readonly-demo`、`product_id=smart-assist`、`field_count=4`。
- 复制快照后的离线 search CLI exit 0：`support-demo`、`allowed_visibilities=[public,support]`、5 条结果；源 `runtime/chroma` 五文件 SHA manifest 前后一致。
- `demo.py --help` exit 0：公开 `start`/`resume`，未执行工作流。

证据层级为 `CHECK_LINT + focused TEST + read-only CLI + local stdio SERVICE_API`。这组证据不证明生产、GUI/设备、真实 MCP 客户端、外部 API/服务、真实数据、用户验收，或超出上述限定测试/冒烟范围的 `create_ticket` 不可达性。

### Limits

- 这是个人脱敏 CLI Demo，不是原公司源码，也不是生产代码；不证明生产部署、生产 IAM/安全、GUI、设备、真实客户端、真实业务数据或用户验收。
- Chroma 是 Windows 免 Docker 的本地替代方案，不等同于 Milvus 生产验证；虚构评测和封闭 T2Retrieval 子集不能代表真实业务质量或官方完整 benchmark。
- MCP annotations 是客户端提示，不是 enforcement；适配器不注册 `create_ticket`，也不绕过人工复核执行副作用工作流。
- `SERVICE_API` 仅指登记的本地 stdio 路径，不代表第三方客户端生态或外部业务 API 已接入。
