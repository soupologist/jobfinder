# j\*bfinder

## Background

As I write this, I'm about to enter the tech world as a fresher. I know that after a year, opportunities will open up, and I need to be prepared accordingly.

This tool is to help me know when the companies I'm interested in have openings I'm eligible for.

## Approach

### Greenhouse

Lot of companies use Greenhouse. The idea is to keep track of these and use the Greenhouse API in order to fetch listings and store them.

Problem: I've noticed that Cockroach Labs calls the role for entry level engineers as Member of Technical Staff, this is in direct contradiction to most companies where MTS is seen as a much more senior level.

What we have currently is a script that can go through the Greenhouse API with a variety of tokens, each token for a particular company. And the filter is purely on the basis of the name of the role.

### Google

Google doesn't run on Greenhouse and has no public jobs API. Its careers site (careers.google.com/jobs/results) does, however, server-render full job cards — title, location, qualifications, job id — in the initial HTML response, and supports deep-linkable pagination via a `page` query param. `google_jobs.py` scrapes that HTML with BeautifulSoup and normalizes it into the same shape the Greenhouse jobs use, so the rest of the pipeline (title/location filters, the DB) doesn't need to know the source.

This is undocumented, Google-internal markup, so it's more brittle than a real API — it can change without notice. If the expected structure disappears, the scraper raises instead of quietly returning zero jobs.

I don't want the scraper running every time we do a fetch and it should probably only run once a day. 

### Lever and Ashby

A bunch of the other companies I care about (CRED, Meesho, Zeta, UiPath, etc.) run on Lever or Ashby instead of Greenhouse. Both expose the same kind of clean public JSON API Greenhouse does — one request per company returns every open posting, full description included — so `lever_jobs.py` and `ashby_jobs.py` follow the exact same fetch-and-normalize pattern as the Greenhouse code.

### Zoho Recruit

Qure.ai's careers site runs on Zoho Recruit, whose official API needs the company's own OAuth credentials. The public careers page does server-render every open job, description included, as JSON in a hidden `<input>`, so `zoho_jobs.py` reads that instead. For these rows the `token` in `companies.csv` is the careers hostname (e.g. `career.qure.ai`), so any other company on Zoho Recruit is just another row.

`companies.csv` now has an `ats` column so a company's row says which fetcher (`greenhouse`, `lever`, `ashby`, `zoho`, or the separate Google path) to use. One catch: Lever/Ashby job ids are UUID strings, not the small integers Greenhouse and Google use, so the `seen_jobs` id column had to widen from `INTEGER` to `TEXT` to hold either.

## The Plan

I want to have this setup so that I can look at it every once in a while, and I'll see the latest job openings, but those that are relevant to me and my skill level. So, that means we will turn this into a cron job, regularly running and silently watching.

The good thing is, it doesn't matter how fast our retrieval is but how detailed it is and accurate it is. Which is why the next stage of our pipeline will be to go one layer deeper and see what the job actually entails, and decide whether this is a good fit for me or not.
