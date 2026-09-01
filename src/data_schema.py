"""Stable standard-library data contracts for the fictional demo dataset."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


_STABLE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$")
SERVICE_STATUSES = frozenset({"operational", "degraded", "maintenance"})


class Visibility(str, Enum):
    PUBLIC = "public"
    SUPPORT = "support"
    ADMIN = "admin"


def _required_text(name: str, value: str) -> str:
    if not isinstance(value, str) or not (cleaned := value.strip()):
        raise ValueError(f"{name} 必须是非空文本。")
    return cleaned


def _stable_id(name: str, value: str) -> str:
    cleaned = _required_text(name, value)
    if not _STABLE_ID.fullmatch(cleaned):
        raise ValueError(f"{name} 必须为 3-64 位小写字母、数字或连字符。")
    return cleaned


@dataclass(frozen=True)
class KnowledgeDocument:
    doc_id: str
    title: str
    category: str
    visibility: Visibility
    product_id: str
    content: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "doc_id", _stable_id("doc_id", self.doc_id))
        object.__setattr__(self, "title", _required_text("title", self.title))
        object.__setattr__(self, "category", _required_text("category", self.category))
        try:
            visibility = Visibility(self.visibility)
        except (TypeError, ValueError) as exc:
            raise ValueError("visibility 必须是 public、support 或 admin。") from exc
        object.__setattr__(self, "visibility", visibility)
        object.__setattr__(self, "product_id", _stable_id("product_id", self.product_id))
        object.__setattr__(self, "content", _required_text("content", self.content))

    @property
    def metadata(self) -> dict[str, str]:
        return {
            "doc_id": self.doc_id,
            "visibility": self.visibility.value,
            "category": self.category,
            "product_id": self.product_id,
        }


@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    service_status: str
    status_message: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "product_id", _stable_id("product_id", self.product_id))
        object.__setattr__(self, "name", _required_text("name", self.name))
        status = _required_text("service_status", self.service_status)
        if status not in SERVICE_STATUSES:
            raise ValueError("service_status 必须是 operational、degraded 或 maintenance。")
        object.__setattr__(self, "service_status", status)
        object.__setattr__(
            self, "status_message", _required_text("status_message", self.status_message)
        )
