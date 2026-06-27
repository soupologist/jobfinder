from fetch_jobs import get_matching_jobs, print_jobs
from store import get_seen_ids, mark_seen
from llm import filter_fresher_friendly


def main():
    jobs = get_matching_jobs()
    seen = get_seen_ids()

    new_jobs = [j for j in jobs if j["id"] not in seen]
    new_jobs = filter_fresher_friendly(new_jobs)

    print_jobs(new_jobs, label="NEW")

    if new_jobs:
        mark_seen(new_jobs)
        print(f"\n✅ Marked {len(new_jobs)} jobs as seen.")


if __name__ == "__main__":
    main()
