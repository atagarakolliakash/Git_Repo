from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class DraftPost:
    due_date: date
    topic: str
    content_type: str
    hook: str
    body: str
    cta: str
    hashtags: str

    @property
    def full_text(self) -> str:
        return "\n\n".join([self.hook, self.body, self.cta, self.hashtags]).strip()


TOPICS = [
    (
        "Slow SQL Query Diagnosis",
        "Educational",
        "A SQL query does not become slow overnight.",
        "It becomes slow quietly. First it takes 2 seconds, then 20 seconds, then 5 minutes. My first step is not to add an index. I check what changed, what the execution plan says, whether estimates are wrong, and whether the query is reading more data than it needs.",
        "What is the most painful query optimization problem you have faced?",
        "#SQL #DatabasePerformance #SQLServer #PostgreSQL",
    ),
    (
        "Backup vs Recovery",
        "Educational",
        "A backup you have never restored is only a hope.",
        "Backup success is not the goal. Recovery confidence is the goal. Every production database needs tested restores, clear RPO/RTO, documented steps, ownership, and regular review.",
        "When did your team last test a database restore?",
        "#DatabaseAdministration #DisasterRecovery #CloudDatabases #SRE",
    ),
    (
        "AI for DBAs",
        "Industry Insight",
        "AI will not replace good DBAs.",
        "But DBAs who use AI well will move faster. AI can summarize execution plans, review scripts, generate test ideas, and explain logs. Production judgment still belongs to the engineer because context, recovery, risk, and business impact matter.",
        "How are you using AI in database work today?",
        "#AI #DBA #DatabaseEngineering #Automation",
    ),
    (
        "Indexing Myths",
        "Technical Deep Dive",
        "Indexes are powerful, but they are not free.",
        "Every index has a write cost, storage cost, maintenance cost, and ownership cost. Before adding one, ask which query pattern needs it, how often it runs, and how improvement will be measured.",
        "What is your rule before adding a new index?",
        "#SQL #DatabaseOptimization #PostgreSQL #SQLServer",
    ),
    (
        "Cloud Database Cost",
        "Industry Insight",
        "Cloud database bills rarely explode because of one big mistake.",
        "They grow through oversized instances, unused replicas, excessive IOPS, storage bloat, bad queries, long retention, and missing cleanup. Performance tuning is often cost optimization in disguise.",
        "What cloud database cost surprised you the most?",
        "#AWS #Azure #CloudDatabases #FinOps",
    ),
    (
        "DBA Career Growth",
        "Career Growth",
        "The fastest way to grow as a database engineer is not learning every database.",
        "It is learning how databases fail. Learn execution plans, indexing tradeoffs, locks, backups, replication, monitoring, and how to explain risk. Diagnostic thinking compounds for your entire career.",
        "What database skill gave you the biggest career return?",
        "#CareerGrowth #DBA #DatabaseEngineering #SQL",
    ),
]


def generate_calendar(days: int = 30, start_date: date | None = None) -> list[DraftPost]:
    start = start_date or date.today()
    posts: list[DraftPost] = []
    for offset in range(days):
        topic = TOPICS[offset % len(TOPICS)]
        posts.append(
            DraftPost(
                due_date=start + timedelta(days=offset),
                topic=topic[0],
                content_type=topic[1],
                hook=topic[2],
                body=topic[3],
                cta=topic[4],
                hashtags=topic[5],
            )
        )
    return posts
