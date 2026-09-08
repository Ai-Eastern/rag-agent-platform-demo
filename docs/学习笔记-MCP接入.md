# 学习笔记：MCP 接入

## 1. 这次接入解决什么问题

MCP 提供一个可被本地客户端发现和调用的工具协议。本 Demo 只做最小接入：使用官方 Python MCP SDK `mcp==2.1.1`，通过本地 stdio 暴露一个只读查询工具 `get_service_status`。它用于教学和协议链路演示，不是生产服务改造。

官方口径：SDK v2 为稳定线，要求 Python `>=3.10`，项目自身和 SDK 采用 MIT 许可。PyPI 发行使用 Trusted Publishing，官方来源提交为 `0921d94a74db900dccd2d534842aa7b6160542d2`。可从 [Python SDK 仓库](https://github.com/modelcontextprotocol/python-sdk)、[PyPI 发行页](https://pypi.org/project/mcp/2.1.1/) 和本项目 [LICENSE](../LICENSE) 交叉查看。

## 2. 本地运行

在项目根目录、已有项目虚拟环境中运行：

```powershell
& .\.venv\Scripts\python.exe .\src\mcp_server.py
```

另一个 PowerShell 窗口可运行本地 stdio 冒烟脚本：

```powershell
& .\.venv\Scripts\python.exe .\scripts\mcp_smoke.py
```

stdio 的关键点是：子进程 stdout 保留给协议消息，服务日志不能混入 stdout；客户端应按 MCP 协议完成初始化、工具发现、调用和关闭。冒烟脚本的结果仍须由技术负责人统一登记，本文不提前把静态结构描述写成 TEST 或 SERVICE 结论。

## 3. 可信身份流

调用方只发送两个业务字段：`user_id` 和 `product_id`。服务端按下面的顺序处理：

```text
user_id
  -> resolve_user(user_id)
  -> 得到不可变的 UserContext（role + allowed_visibilities）
  -> get_service_status(context, product_id)
```

`resolve_user` 只接受三个虚构演示身份，未知身份 fail closed。调用方永远不能通过参数传入 `role` 或 `visibility` 来扩大权限；参数模型也拒绝额外字段。`get_service_status` 继续执行现有可信上下文检查，并返回 `product_id`、`name`、`service_status`、`status_message` 四个字符串字段。

## 4. 工具边界

- MCP 工具列表只有 `get_service_status`，且它是只读工具。
- `create_ticket` 不在 MCP 适配器中注册、导入或间接调用。
- MCP annotations（如 `readOnlyHint`、`destructiveHint`、`idempotentHint`、`openWorldHint`）是客户端可参考的 advisory hints，不是 enforcement；权限 enforcement 由可信身份解析和现有工具入口完成。
- 该适配器不绕过 LangGraph 的 interrupt/人工复核，不改变既有工具权限合同。

## 5. 证据边界

截至 2026-09-05，技术负责人登记的 D4 证据为：`TL-COMPILE` exit 0；focused unittest exit 0，`Ran 2 tests`、`OK`；local stdio smoke exit 0，输出 `{"status":"ok","tool_names":["get_service_status"],"call":{"tool":"get_service_status","user_id":"readonly-demo","product_id":"smart-assist","field_count":4}}`；`TL-BOUNDARY-STATIC` exit 0。因此本地结论提升到 `CHECK_LINT + TEST + 本地 stdio SERVICE_API`。

这只覆盖已登记的本地验证路径，不证明第三方客户端生态、生产安全/IAM、GUI、设备、真实数据/外部业务 API 或用户验收；也不把静态 SDK 配置扩写成生产服务验收。

因此，本文“不证明”以下事项：生产部署可用、生产身份认证安全、真实业务数据权限、第三方客户端兼容性、模型/GPU能力、Milvus能力，以及绕过人工复核执行副作用工作流。
