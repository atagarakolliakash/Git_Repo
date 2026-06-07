from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


IMPORTANT_KEYWORDS = [
    "Senior Database Administrator",
    "Database Engineer",
    "SQL Server",
    "PostgreSQL",
    "MySQL",
    "Performance Tuning",
    "Query Optimization",
    "Execution Plans",
    "Index Tuning",
    "AWS RDS",
    "Azure SQL",
    "Cloud Databases",
    "Backup and Recovery",
    "High Availability",
    "Disaster Recovery",
    "Monitoring",
    "Automation",
    "DevOps",
    "Databricks",
    "SQL Server",
    "PostgreSQL",
    "MySQL",
    "Performance Tuning",
    "Backup and Recovery",
    "Database Administration",
    "AWS S3",
    "AWS Redshift",
    "AWS RDS",
    "AWS Lambda",
    "AWS IAM",
    "AWS Glue Crawler",
    "AWS DMS",
    "High Availability Solutions",
    "Replication",
    "Backup and Recovery",
    "Capacity Planning",
    "Python",
    "PySpark",
    "Data Warehousing",
    "Performance Monitoring",
    "Data Governance",
    "Medallion Architecture"
]


@dataclass
class ProfileAnalysis:
    profile_score: int
    searchability_score: int
    authority_score: int
    creator_score: int
    missing_keywords: list[str]
    strengths: list[str]
    gaps: list[str]
    recommendations: list[str]
    proposed_headline: str
    proposed_about: str


def load_profile(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as profile_file:
        return json.load(profile_file)


def _profile_text(profile: dict[str, Any]) -> str:
    parts: list[str] = []
    for value in profile.values():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(json.dumps(item, ensure_ascii=False) for item in value)
        elif isinstance(value, dict):
            parts.append(json.dumps(value, ensure_ascii=False))
    return "\n".join(parts).lower()


def analyze_profile(profile: dict[str, Any]) -> ProfileAnalysis:
    text = _profile_text(profile)
    missing_keywords = [keyword for keyword in IMPORTANT_KEYWORDS if keyword.lower() not in text]
    keyword_coverage = 1 - (len(missing_keywords) / len(IMPORTANT_KEYWORDS))

    has_featured = bool(profile.get("featured"))
    has_recommendations = bool(profile.get("recommendations"))
    has_activity = bool(profile.get("recent_posts"))
    has_metrics = any(token in text for token in ["%", "reduced", "improved", "optimized", "migrated", "uptime"])

    profile_score = int(55 + keyword_coverage * 25 + (5 if has_featured else 0) + (5 if has_metrics else 0))
    searchability_score = int(50 + keyword_coverage * 45)
    authority_score = int(58 + (12 if has_metrics else 0) + (10 if has_recommendations else 0) + (8 if has_featured else 0))
    creator_score = int(30 + (20 if has_activity else 0) + (10 if has_featured else 0))

    strengths = [
        "Nearly 9 years of database administration experience is a strong seniority signal.",
        "Database performance, reliability, and cloud operations are high-demand LinkedIn niches.",
        "Current follower/connection base is enough to start compounding content reach.",
    ]
    gaps = [
        "Profile needs more quantified outcomes such as latency reduced, incidents prevented, migrations completed, or cost saved.",
        "Featured section should show proof assets: case studies, checklists, technical guides, or project summaries.",
        "Creator visibility is limited unless original posts and expert comments become consistent.",
    ]
    if missing_keywords:
        gaps.append("Important recruiter and search keywords are missing or not prominent enough.")

    recommendations = [
        "Rewrite the headline around role, niche, platforms, and outcomes.",
        "Rewrite About with a clear positioning statement, proof bullets, technical stack, and CTA.",
        "Add 3 Featured assets: database health checklist, query tuning case study, and cloud database reliability playbook.",
        "Rewrite each experience bullet as outcome + technology + business impact.",
        "Request 3 recommendations from a manager, architect, and developer/stakeholder.",
        "Publish 4 posts per week across performance tuning, cloud databases, DBA career growth, and AI automation.",
    ]

    proposed_headline = (
        "Senior Database Administrator | SQL Server, PostgreSQL & Cloud Databases | "
        "Performance Tuning, HA/DR, AWS/Azure, Automation"
    )
    proposed_about = (
        "I am a Senior Database Administrator with nearly 9 years of experience helping teams keep production "
        "databases fast, reliable, secure, and scalable.\n\n"
        "My work focuses on SQL Server, PostgreSQL, MySQL, cloud databases, performance tuning, backup and recovery, "
        "HA/DR, monitoring, and automation. I enjoy solving slow query problems, improving database reliability, "
        "supporting migrations, and helping engineering teams make safer data decisions.\n\n"
        "Core areas: SQL Server, PostgreSQL, MySQL, AWS RDS, Azure SQL, query optimization, execution plans, index "
        "tuning, disaster recovery, database monitoring, DevOps automation, and cloud database operations.\n\n"
        "I use this profile to share practical lessons from real production database work: performance tuning, "
        "reliability, cloud cost control, automation, and career growth for database engineers."
    )

    return ProfileAnalysis(
        profile_score=min(profile_score, 100),
        searchability_score=min(searchability_score, 100),
        authority_score=min(authority_score, 100),
        creator_score=min(creator_score, 100),
        missing_keywords=missing_keywords,
        strengths=strengths,
        gaps=gaps,
        recommendations=recommendations,
        proposed_headline=proposed_headline,
        proposed_about=proposed_about,
    )


def write_report(analysis: ProfileAnalysis, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "profile_approval_report.md"
    report_path.write_text(_render_report(analysis), encoding="utf-8")
    return report_path


def _render_report(analysis: ProfileAnalysis) -> str:
    missing = "\n".join(f"- {keyword}" for keyword in analysis.missing_keywords) or "- None"
    strengths = "\n".join(f"- {item}" for item in analysis.strengths)
    gaps = "\n".join(f"- {item}" for item in analysis.gaps)
    recommendations = "\n".join(f"- [ ] {item}" for item in analysis.recommendations)

    return f"""# LinkedIn Profile Approval Report

## Scores

| Area | Score |
|---|---:|
| Profile Optimization | {analysis.profile_score}/100 |
| Searchability | {analysis.searchability_score}/100 |
| Technical Authority | {analysis.authority_score}/100 |
| Creator Visibility | {analysis.creator_score}/100 |

## Strengths

{strengths}

## Gaps

{gaps}

## Missing / Weak Keywords

{missing}

## Proposed Headline

```text
{analysis.proposed_headline}
```

## Proposed About Section

```text
{analysis.proposed_about}
```

## Approval Checklist

{recommendations}
"""
