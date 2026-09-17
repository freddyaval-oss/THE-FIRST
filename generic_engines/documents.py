"""Configurable record-to-document processing."""

from __future__ import annotations

from dataclasses import dataclass
from string import Formatter
from typing import Any, Callable, Mapping


class ValidationError(ValueError):
    """Raised when one or more record fields fail validation."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


@dataclass(frozen=True)
class FieldRule:
    required: bool = False
    converter: Callable[[Any], Any] | None = None
    predicate: Callable[[Any], bool] | None = None
    message: str = "invalid value"


class DocumentPipeline:
    """Normalize and validate records before rendering a text document."""

    def __init__(
        self,
        rules: Mapping[str, FieldRule],
        derived: Mapping[str, Callable[[dict[str, Any]], Any]] | None = None,
    ) -> None:
        self.rules = dict(rules)
        self.derived = dict(derived or {})

    def process(self, record: Mapping[str, Any]) -> dict[str, Any]:
        output = dict(record)
        errors: list[str] = []
        for field, rule in self.rules.items():
            value = output.get(field)
            if rule.required and (value is None or value == ""):
                errors.append(f"{field}: required")
                continue
            if value is None:
                continue
            if rule.converter:
                try:
                    value = rule.converter(value)
                    output[field] = value
                except (TypeError, ValueError) as exc:
                    errors.append(f"{field}: conversion failed ({exc})")
                    continue
            if rule.predicate and not rule.predicate(value):
                errors.append(f"{field}: {rule.message}")
        if errors:
            raise ValidationError(errors)
        for field, calculation in self.derived.items():
            output[field] = calculation(dict(output))
        return output

    def render(self, template: str, record: Mapping[str, Any]) -> str:
        processed = self.process(record)
        required = {name for _, name, _, _ in Formatter().parse(template) if name}
        missing = sorted(name for name in required if name not in processed)
        if missing:
            raise ValidationError([f"{name}: missing template value" for name in missing])
        return template.format_map(processed)
