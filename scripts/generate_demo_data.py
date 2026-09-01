"""Generate deterministic fictional demo data using only the standard library."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import PROJECT_PATHS
from src.data_schema import KnowledgeDocument, Product, Visibility


PRODUCT_FIELDS = ("product_id", "name", "service_status", "status_message")
TICKET_FIELDS = (
    "ticket_id",
    "idempotency_key",
    "created_at",
    "role",
    "product_id",
    "summary",
    "status",
)

PRODUCTS = (
    Product(
        "smart-assist",
        "智达科技智能助手（虚构演示产品）",
        "operational",
        "智达科技虚构演示状态：服务运行正常。",
    ),
    Product(
        "knowledge-hub",
        "智达科技知识中心（虚构演示产品）",
        "degraded",
        "智达科技虚构演示状态：部分检索响应较慢。",
    ),
    Product(
        "service-console",
        "智达科技服务控制台（虚构演示产品）",
        "maintenance",
        "智达科技虚构演示状态：正在计划维护。",
    ),
)

DOCUMENTS = (
    KnowledgeDocument(
        "product-manual",
        "智达科技智能助手产品手册",
        "产品手册",
        Visibility.PUBLIC,
        "smart-assist",
        """# 智达科技智能助手产品手册

本文档及所述产品均为虚构演示数据。

智能助手提供知识查询、结果摘要和来源提示。用户应核对重要信息，不应把演示回答视为真实业务承诺。""",
    ),
    KnowledgeDocument(
        "service-terms",
        "智达科技演示服务条款",
        "服务条款",
        Visibility.PUBLIC,
        "smart-assist",
        """# 智达科技演示服务条款

本文档及全部条款均为虚构演示数据，不构成真实合同。

演示服务仅用于功能学习。使用者应避免提交个人信息、密钥或真实业务资料。""",
    ),
    KnowledgeDocument(
        "common-faq",
        "智达科技知识中心常见问题",
        "FAQ",
        Visibility.PUBLIC,
        "knowledge-hub",
        """# 智达科技知识中心常见问题

本文档及问答均为虚构演示数据。

## 为什么回答会附带来源？

来源提示用于展示回答依据，使用者仍需自行判断内容是否适用。""",
    ),
    KnowledgeDocument(
        "troubleshooting-guide",
        "智达科技知识中心故障处理",
        "故障处理",
        Visibility.SUPPORT,
        "knowledge-hub",
        """# 智达科技知识中心故障处理

本文档及故障场景均为虚构演示数据。

当检索响应较慢时，客服可先确认服务状态，再建议用户缩短问题并重试。不得要求用户提供密码或密钥。""",
    ),
    KnowledgeDocument(
        "support-playbook",
        "智达科技内部客服资料",
        "内部客服资料",
        Visibility.SUPPORT,
        "service-console",
        """# 智达科技内部客服资料

本文档、流程和角色均为虚构演示数据。

客服应先确认问题摘要与产品，再记录可复现步骤。涉及管理员权限的事项必须升级处理。""",
    ),
    KnowledgeDocument(
        "admin-operations",
        "智达科技管理员资料",
        "管理员资料",
        Visibility.ADMIN,
        "service-console",
        """# 智达科技管理员资料

本文档及管理流程均为虚构演示数据。

管理员变更服务状态前应复核影响范围并保留操作说明。演示资料不包含真实账号、地址或连接信息。""",
    ),
)


def _markdown(document: KnowledgeDocument) -> str:
    metadata = document.metadata
    front_matter = "\n".join(
        (
            "---",
            f"doc_id: {metadata['doc_id']}",
            f"title: {document.title}",
            f"category: {metadata['category']}",
            f"visibility: {metadata['visibility']}",
            f"product_id: {metadata['product_id']}",
            "---",
        )
    )
    return f"{front_matter}\n\n{document.content}\n"


def _write_csv(path: Path, fields: tuple[str, ...], rows: tuple[object, ...]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: getattr(row, field) for field in fields})


def generate(output_dir: Path) -> tuple[Path, ...]:
    output_dir = output_dir.resolve()
    knowledge_dir = output_dir / "knowledge"
    knowledge_dir.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for document in sorted(DOCUMENTS, key=lambda item: item.doc_id):
        path = knowledge_dir / f"{document.doc_id}.md"
        path.write_text(_markdown(document), encoding="utf-8", newline="\n")
        written.append(path)

    products_path = output_dir / "products.csv"
    _write_csv(products_path, PRODUCT_FIELDS, tuple(sorted(PRODUCTS, key=lambda item: item.product_id)))
    written.append(products_path)

    tickets_path = output_dir / "tickets.csv"
    _write_csv(tickets_path, TICKET_FIELDS, ())
    written.append(tickets_path)
    return tuple(written)


def main() -> int:
    parser = argparse.ArgumentParser(description="生成智达科技确定性虚构演示数据。")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_PATHS["data"],
        help="输出目录，默认使用项目内 data 目录。",
    )
    args = parser.parse_args()
    written = generate(args.output_dir)
    print(f"已生成 {len(written)} 个智达科技虚构演示数据文件：{args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
