import argparse
import sys

from store import VALID_STATUSES, clean_jobs, delete_job, get_jobs, update_status

_STATUS_LABEL = {
    "new":          "🆕  new",
    "applied":      "✅  applied",
    "skipped":      "⏭️   skipped",
    "interviewing": "🔄  interviewing",
    "rejected":     "❌  rejected",
    "offer":        "🎉  offer",
}


def cmd_list(args):
    jobs = get_jobs(args.status)
    if not jobs:
        print("No jobs found.")
        return

    print(f"\n{'ID':<12} {'STATUS':<16} {'COMPANY':<22} {'TITLE':<42} SEEN")
    print("-" * 110)
    for j in jobs:
        label = _STATUS_LABEL.get(j["status"], j["status"])
        seen  = (j["first_seen"] or "")[:10]
        print(f"{j['id']:<12} {label:<16} {j['company'][:20]:<22} {j['title'][:40]:<42} {seen}")

    by_status: dict[str, int] = {}
    for j in jobs:
        by_status[j["status"]] = by_status.get(j["status"], 0) + 1
    summary = "  ".join(f"{k}: {v}" for k, v in sorted(by_status.items()))
    print(f"\nTotal: {len(jobs)}  ({summary})")


def cmd_set(args):
    ok = update_status(args.id, args.status)
    if ok:
        print(f"✅  Job {args.id} → {args.status}")
    else:
        print(f"⚠️   No job found with id {args.id}")
        sys.exit(1)


def cmd_delete(args):
    ok = delete_job(args.id)
    if ok:
        print(f"🗑️   Deleted job {args.id}")
    else:
        print(f"⚠️   No job found with id {args.id}")
        sys.exit(1)


def cmd_clean(args):
    n = clean_jobs(args.status, args.older_than)
    qualifier = f" older than {args.older_than} days" if args.older_than else ""
    print(f"🧹  Deleted {n} '{args.status}' job(s){qualifier}.")


def main():
    parser = argparse.ArgumentParser(description="Manage the jobs DB")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List jobs (optionally filtered by status)")
    p_list.add_argument("--status", choices=VALID_STATUSES, help="Filter by status")
    p_list.set_defaults(func=cmd_list)

    p_set = sub.add_parser("set", help="Update a job's status")
    p_set.add_argument("id", type=int, help="Job ID")
    p_set.add_argument("status", choices=VALID_STATUSES)
    p_set.set_defaults(func=cmd_set)

    p_del = sub.add_parser("delete", help="Delete a single job by ID")
    p_del.add_argument("id", type=int, help="Job ID")
    p_del.set_defaults(func=cmd_delete)

    p_clean = sub.add_parser("clean", help="Bulk-delete jobs by status")
    p_clean.add_argument("status", choices=VALID_STATUSES, help="Status to purge")
    p_clean.add_argument("--older-than", type=int, metavar="DAYS", dest="older_than",
                         help="Only delete if first seen more than N days ago")
    p_clean.set_defaults(func=cmd_clean)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
