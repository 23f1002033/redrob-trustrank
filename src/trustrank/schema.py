from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

TODAY = date(2026, 6, 23)


def _s(v: Any) -> str:
    return "" if v is None else str(v).strip()


def _num(v: Any, default: float | None = None) -> float | None:
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else default


def _iso(d: Any) -> date | None:
    try:
        return date.fromisoformat(str(d))
    except (TypeError, ValueError):
        return None


@dataclass
class Role:
    company: str = ""
    title: str = ""
    start_date: str = ""
    end_date: str | None = None
    duration_months: int = 0
    is_current: bool = False
    industry: str = ""
    company_size: str = ""
    description: str = ""

    @classmethod
    def from_raw(cls, d: dict) -> "Role":
        d = d or {}
        return cls(
            company=_s(d.get("company")),
            title=_s(d.get("title")),
            start_date=_s(d.get("start_date")),
            end_date=d.get("end_date"),
            duration_months=int(_num(d.get("duration_months"), 0) or 0),
            is_current=bool(d.get("is_current")),
            industry=_s(d.get("industry")),
            company_size=_s(d.get("company_size")),
            description=_s(d.get("description")),
        )

    def calendar_months(self) -> int:
        """Months actually spanned by start_date -> end_date (or today)."""
        s = _iso(self.start_date)
        if not s:
            return 0
        e = _iso(self.end_date) or TODAY
        return max(0, (e.year - s.year) * 12 + (e.month - s.month))


@dataclass
class Education:
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    start_year: int | None = None
    end_year: int | None = None
    tier: str = "unknown"

    @classmethod
    def from_raw(cls, d: dict) -> "Education":
        d = d or {}
        return cls(
            institution=_s(d.get("institution")),
            degree=_s(d.get("degree")),
            field_of_study=_s(d.get("field_of_study")),
            start_year=_num(d.get("start_year")),
            end_year=_num(d.get("end_year")),
            tier=_s(d.get("tier")) or "unknown",
        )


@dataclass
class Skill:
    name: str = ""
    proficiency: str = ""
    endorsements: int = 0
    duration_months: int = 0

    @classmethod
    def from_raw(cls, d: dict) -> "Skill":
        d = d or {}
        return cls(
            name=_s(d.get("name")),
            proficiency=_s(d.get("proficiency")).lower(),
            endorsements=int(_num(d.get("endorsements"), 0) or 0),
            duration_months=int(_num(d.get("duration_months"), 0) or 0),
        )


@dataclass
class Candidate:
    candidate_id: str = ""
    # profile
    name: str = ""
    headline: str = ""
    summary: str = ""
    location: str = ""
    country: str = ""
    years_experience: float = 0.0
    current_title: str = ""
    current_company: str = ""
    current_industry: str = ""
    # blocks
    roles: list[Role] = field(default_factory=list)
    education: list[Education] = field(default_factory=list)
    skills: list[Skill] = field(default_factory=list)
    signals: dict = field(default_factory=dict)
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_raw(cls, d: dict) -> "Candidate":
        d = d or {}
        p = d.get("profile", {}) or {}
        return cls(
            candidate_id=_s(d.get("candidate_id")),
            name=_s(p.get("anonymized_name")),
            headline=_s(p.get("headline")),
            summary=_s(p.get("summary")),
            location=_s(p.get("location")),
            country=_s(p.get("country")),
            years_experience=float(_num(p.get("years_of_experience"), 0.0) or 0.0),
            current_title=_s(p.get("current_title")),
            current_company=_s(p.get("current_company")),
            current_industry=_s(p.get("current_industry")),
            roles=[Role.from_raw(r) for r in (d.get("career_history") or [])],
            education=[Education.from_raw(e) for e in (d.get("education") or [])],
            skills=[Skill.from_raw(s) for s in (d.get("skills") or [])],
            signals=d.get("redrob_signals", {}) or {},
            raw=d,
        )

    def descriptions(self) -> list[str]:
        return [r.description.lower() for r in self.roles if r.description]

    def all_description_text(self) -> str:
        return " ".join(self.descriptions())

    def current_role(self) -> Role | None:
        for r in self.roles:
            if r.is_current:
                return r
        return self.roles[0] if self.roles else None
