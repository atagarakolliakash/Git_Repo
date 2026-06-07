from __future__ import annotations

import argparse
from pathlib import Path

from .approval_queue import ApprovalQueue
from .config import load_settings
from .content_engine import generate_calendar
from .linkedin_client import LinkedInClient
from .profile_analyzer import analyze_profile, load_profile, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Approval-first LinkedIn growth agents")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze = subparsers.add_parser("analyze-profile", help="Analyze a profile snapshot and write approval report")
    analyze.add_argument("--profile-json", required=True, type=Path)
    analyze.add_argument("--out", default=Path("reports"), type=Path)

    seed = subparsers.add_parser("seed-calendar", help="Seed the post approval queue")
    seed.add_argument("--days", default=30, type=int)

    subparsers.add_parser("list-posts", help="List queued posts")

    approve = subparsers.add_parser("approve-post", help="Approve a queued post")
    approve.add_argument("--id", required=True, type=int)

    reject = subparsers.add_parser("reject-post", help="Reject a queued post")
    reject.add_argument("--id", required=True, type=int)

    subparsers.add_parser("publish-next-approved", help="Publish the next approved due post")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = load_settings()
    queue = ApprovalQueue(settings.database_path)

    if args.command == "analyze-profile":
        profile = load_profile(args.profile_json)
        analysis = analyze_profile(profile)
        report_path = write_report(analysis, args.out)
        print(f"Wrote approval report: {report_path}")
        return

    if args.command == "seed-calendar":
        added = queue.add_posts(generate_calendar(args.days))
        print(f"Added {added} draft posts to approval queue.")
        return

    if args.command == "list-posts":
        for post in queue.list_posts():
            print(f"[{post.id}] {post.due_date} | {post.status:<9} | {post.content_type:<16} | {post.topic}")
        return

    if args.command == "approve-post":
        queue.approve(args.id)
        print(f"Approved post {args.id}.")
        return

    if args.command == "reject-post":
        queue.reject(args.id)
        print(f"Rejected post {args.id}.")
        return

    if args.command == "publish-next-approved":
        post = queue.next_approved_due()
        if not post:
            print("No approved due posts found.")
            return

        client = LinkedInClient(settings)
        published_urn = client.publish_text_post(post.content)
        if not published_urn.startswith("dry-run"):
            queue.mark_published(post.id, published_urn)
            print(f"Published post {post.id}: {published_urn}")
        else:
            print("Dry run: post was not sent to LinkedIn.")
            print()
            print(post.content)
        return


if __name__ == "__main__":
    main()
