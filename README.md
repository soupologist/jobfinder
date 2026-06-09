# j\*bfinder

## Background

As I write this, I'm about to enter the tech world as a fresher. I know that after a year, opportunities will open up, and I need to be prepared accordingly.

This tool is to help me know when the companies I'm interested in have openings I'm eligible for.

## Approach

### Greenhouse

Lot of companies use Greenhouse. The idea is to keep track of these and use the Greenhouse API in order to fetch listings and store them.

Problem: I've noticed that Cockroach Labs calls the role for entry level engineers as Member of Technical Staff, this is in direct contradiction to most companies where MTS is seen as a much more senior level.

What we have currently is a script that can go through the Greenhouse API with a variety of tokens, each token for a particular company. And the filter is purely on the basis of the name of the role.

I want to have this setup so that I can look at it every once in a while, and I'll see the latest job openings, but those that are relevant to me and my skill level. So, that means we will turn this into a cron job, regularly running and silently watching.

The good thing is, it doesn't matter how fast our retrieval is but how detailed it is and accurate it is. Which is why the next stage of our pipeline will be to go one layer deeper and see what the job actually entails, and decide whether this is a good fit for me or not.
