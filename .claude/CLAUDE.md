# TopMoneyApps — rules for automated publishing

This repository is the live website topmoneyapps.com. It is served by GitHub Pages
(behind Cloudflare) straight from the `main` branch: every push to `main` is live
within minutes. There is no staging site, so every rule below exists to keep
mistakes off the live site.

Owner and editor: Mike Van Kempen. Every article is published under his byline.

## What a scheduled run does

1. Sync: `git pull --rebase origin main` (a shallow clone is fine).
2. Pick 4 topics (see "Choosing topics").
3. For each topic: research, write the page, wire it into the site.
4. Run `python3 _automation/check_site.py <new files>` and fix everything it reports.
   An article that still fails, or whose facts could not be verified, is dropped,
   not published. Publishing fewer than 4 is fine; publishing something wrong is not.
5. Add one line per published article to `_automation/published-log.md`
   (and one line per dropped topic, with the reason).
6. Commit everything in one commit: `Publish: <slug>, <slug>, ...` and push to `main`.
   If the push is rejected, `git pull --rebase origin main` and push once more.
7. End with a short summary: each new URL, its title, and anything dropped and why.

## Choosing topics

- Start with `_automation/topic-ideas.md`. Take the first unclaimed ideas, then mark
  them done there. When fewer than 20 ideas remain, add 20 new ones before writing.
- Before claiming a topic, check it is not already covered: search the repo for the
  topic's main keywords (`grep -il`) and read `_automation/published-log.md`.
  Do not publish a page whose main search query overlaps an existing page
  (keyword cannibalization). If an existing page covers it, skip the topic.
- Good topics answer one specific question people search for: statistics with a
  government or primary source ("average water bill by state"), explainers
  ("Roth IRA vs. traditional IRA"), how-tos ("how to freeze your credit"),
  current-year rules ("2026 tax brackets"), and head-to-head comparisons of apps
  that already have a score in `_automation/scores.json`.
- Prefer what is timely for today's date (tax season, open enrollment, year-end).

## Never publish (log the topic as "needs Mike" instead)

- Any page that is mainly about Acorns, or that compares Acorns head-to-head with
  another app. Acorns may appear inside broader lists like any other app, using its
  score from `scores.json`.
- Personalized advice, buy/sell calls on individual stocks or coins, price
  predictions, or claims about future returns.
- Medical, legal or immigration advice; anything about gambling strategy.
- Reviews or testimonials written as if from real users, invented quotes, or
  claims that TopMoneyApps or Mike personally tested something ("we tested",
  "in our testing", "hands-on") — the automated pipeline has not tested anything.
- Pages that change the scores, rankings, the homepage (`index.html`), `about.html`,
  or any existing page's verdict. Rankings change only when Mike updates the
  scoring sheet.

## Facts and sources (the most important rules)

- Every number, rate, price, limit, date and claim about a company comes from a
  source you opened in this run with WebSearch/WebFetch. Never state a figure from
  memory. If you cannot confirm a figure, leave it out.
- Prefer primary sources: government (IRS, BLS, Federal Reserve, Census, SSA, CFPB,
  FDIC, SEC, EIA, state agencies), the company's own pages, then major outlets.
- Rates, prices and fees are dated in the text ("3.55% APY as of November 2026").
- Every article ends with a Sources section listing at least 3 external sources you
  actually used, linked.
- Rankings of apps follow `_automation/scores.json` exactly (score order, then the
  tie-break rule). Show scores as "TopMoneyApps score 4.13/5" and link
  `about.html#scores`. Apps not in `scores.json` get no score and no numbered rank;
  describe them, don't rank them.
- Star ratings shown for apps are Apple App Store figures, labeled as such, with the
  month they were checked.
- Be neutral. Give the trade-offs and fees for every app, including the ones we
  like. No hype words ("best ever", "game-changer", "unbeatable").

## Page structure (copy from a template, never from scratch)

Copy the closest existing page and replace its content, keeping its `<head>`
boilerplate, CSS, nav, author box, footer, FAQ script and the ELI promo banner:

- Statistics page: `emergency-fund-statistics-2026.html`
- Explainer or how-to: `hsa-vs-fsa.html` or `how-to-build-credit-from-scratch.html`
- App comparison: `acorns-vs-alinea.html` (structure only — do not reuse its text)

Every new page must have:

- File name: lowercase-hyphenated slug ending in `.html`; add `-2026` only when the
  content is year-specific.
- `<title>` under ~65 characters before ` | TopMoneyApps`; meta description of
  about 120–160 characters (never over 200); canonical `https://topmoneyapps.com/<file>`; Open Graph tags with
  `og:image` `https://topmoneyapps.com/tma-cover-photo.png`; the Google tag
  `G-W1RSS2P0EM` exactly as in the template.
- JSON-LD: `Article` (author Person "Mike Van Kempen", url
  `https://topmoneyapps.com/author-mike-van-kempen.html`; `datePublished` and
  `dateModified` = today), `BreadcrumbList`, and `FAQPage` whose questions and answers
  match the visible FAQ word for word. Stats pages may add `Dataset`.
- Exactly one `<h1>`; byline "By Mike Van Kempen" and "Updated <Month Year>".
- An answer-first opening paragraph (the direct answer in the first two sentences).
- `<!-- geo:takeaways -->` Key Takeaways block with 3–5 bullets, each a complete,
  quotable fact.
- Clear H2 sections, at least one table or list where it helps, 900–1,800 words.
- `<!-- geo:sources -->` Sources block (see above).
- 3–6 FAQs.
- At least 3 links to related existing pages, plus a "related" block.
- Affiliate links: Robinhood links use `https://join.robinhood.com/michaev48/` with
  `rel="sponsored noopener"`. Other app links go to the official site with
  `rel="sponsored noopener" target="_blank"`. Pages with any `rel="sponsored"` link
  keep the template's affiliate disclosure.

## Wiring a new page into the site

For each published page:

1. `sitemap.xml`: add a `<url>` entry (lastmod = today, changefreq monthly,
   priority 0.8).
2. `llms.txt`: add one line `- <Title>: https://topmoneyapps.com/<file>` in the
   matching list.
3. `llms-full.txt`: add a block in the same format as its neighbors
   (`### Title`, `URL:`, `Title:`, `Author:`, `Updated:`, `Summary:` with the key
   facts and numbers, `Key FAQs:`).
4. Add a link card to exactly one hub page:
   - investing topics → `investing-guides.html` (matching section)
   - statistics → `stats.html` (matching section)
   - app comparisons and reviews → `comparisons.html`
   - everything else → `money-guides.html` (the section whose `data-hub-section`
     fits: budgeting, credit, taxes, housing, insurance, saving, planning)
5. Add a link to the new page from 1–2 closely related existing pages (in their
   related/"more guides" block only — do not rewrite their content).

## Quality gate

`python3 _automation/check_site.py <file> [<file> ...]` must print `ALL CHECKS PASSED`
before you commit. It checks the structure above, the sitemap/llms/hub wiring,
broken internal links and valid JSON-LD across the whole site. Never edit the
checker to make a page pass.

## Writing style

Plain, specific, short sentences. Second person ("you"). Numbers over adjectives.
No emojis in body text. US spelling. Explain jargon the first time it appears.
