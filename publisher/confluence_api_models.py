"""Pydantic models for Confluence REST API response validation."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator


class ConfluenceApiValidationError(RuntimeError):
    """Raised when a Confluence API JSON body does not match the expected schema."""


def validate_response_payload(data: object, model_cls: type[BaseModel], context: str) -> BaseModel:
    try:
        return model_cls.model_validate(data)
    except ValidationError as e:
        raise ConfluenceApiValidationError(
            f"{context}: API response did not match expected shape — {e}"
        ) from e


class ConfluenceSpaceRef(BaseModel):
    model_config = ConfigDict(extra="allow")

    key: str | None = None


class ParentPageResponse(BaseModel):
    """GET /content/{id}?expand=space"""

    model_config = ConfigDict(extra="allow")

    space: ConfluenceSpaceRef | None = None


class CreatedPageResponse(BaseModel):
    """POST /content/ (create page)"""

    model_config = ConfigDict(extra="allow")

    id: str

    @field_validator("id", mode="before")
    @classmethod
    def _id_as_str(cls, v: object) -> str:
        if v is None:
            raise ValueError("id is required")
        return str(v)


class SearchResultContent(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    title: str

    @field_validator("id", mode="before")
    @classmethod
    def _id_as_str(cls, v: object) -> str:
        if v is None:
            raise ValueError("content id is required")
        return str(v)


class SearchResultItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    content: SearchResultContent


class SearchResponse(BaseModel):
    """GET /search?cql=..."""

    model_config = ConfigDict(extra="allow")

    results: list[SearchResultItem]


class AttachmentResultItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str

    @field_validator("id", mode="before")
    @classmethod
    def _id_as_str(cls, v: object) -> str:
        if v is None:
            raise ValueError("attachment id is required")
        return str(v)


class AttachmentResponse(BaseModel):
    """POST .../child/attachment"""

    model_config = ConfigDict(extra="allow")

    results: list[AttachmentResultItem]

    @field_validator("results")
    @classmethod
    def _non_empty_results(cls, v: list[AttachmentResultItem]) -> list[AttachmentResultItem]:
        if not v:
            raise ValueError("results must contain at least one attachment")
        return v
