# X (@topmoneyapps) posting rules

Posts go out through Buffer (organization "My organization", X channel
"topmoneyapps", channel ID `6b065b458541f09ecb966de5`). Buffer's free plan holds
at most 10 scheduled posts at a time, so a refill run tops the queue back up.

## What a refill run does

1. `git pull --rebase origin main`.
2. In Buffer, list this channel's posts with status `scheduled`. Count them and find
   the latest scheduled time. If any post has status `error`, include it in the summary.
3. Add new articles to the queue: any page in `sitemap.xml` that is not in
   `_automation/social-queue.txt` and is not excluded below goes into the queue
   right after the last article already posted, so new articles go out soon.
4. Fill the queue back up to 10 scheduled posts. Each new post is scheduled one hour
   after the previous one, on the hour, in America/Chicago time (`customScheduled`,
   `schedulingType: automatic`). If nothing is scheduled, start at the next full hour.
5. Take articles in `social-queue.txt` order, starting after the last slug in
   `_automation/social-log.md` whose cycle column is a number (pool posts, below,
   do not move this pointer). After the last article, wrap to the top and increase
   the cycle number by 1.
5a. Apply the daily mix (next section) while filling the slots.
6. Append one line per scheduled post to `social-log.md`, commit
   (`Social: schedule <n> posts`) and push to `main`.
7. Finish with a short summary sent to Mike: how many posts were scheduled, the time
   range they cover, and any Buffer errors.

## Daily mix: one Monarch post and one life-insurance post every day

Every calendar day (America/Chicago) must have at least one post linking to a
Monarch page and at least one linking to a life-insurance page. These pages carry
Mike's affiliate links.

- **Monarch pool**: every page whose HTML links `monarchmoney.sjv.io`, except
  `index.html` (find them with `grep -l 'monarchmoney.sjv.io' *.html`). Rotate in
  this order, then any new pages alphabetically: `monarch-money-review.html`,
  `ynab-vs-monarch-money.html`, `monarch-vs-empower.html`,
  `copilot-vs-monarch-money.html`, `best-budgeting-apps.html`,
  `best-budgeting-app-couples.html`, `best-ai-budgeting-apps-2026.html`,
  `best-app-track-net-worth.html`, `best-budgeting-method.html`.
- **Life-insurance pool**: `life-insurance-guide.html`,
  `life-insurance-calculator.html`, `trust-and-will-review.html`, then, once
  published, every page from the "Life insurance (priority)" section of
  `_automation/topic-ideas.md` (marked `[x]`) and any other new page with
  `life-insurance` in its file name, in the order they were published.
- How to apply it: for each day you schedule posts on, check `social-log.md` for
  rows dated that day with cycle `pool:life` or `pool:monarch` (and for queue rows
  that happen to be a pool page). If the day has no life-insurance post, the first
  slot you schedule that day between 9:00 AM and 8:00 PM goes to the next page in
  the life-insurance pool; if it has no Monarch post, the next such slot goes to the
  next page in the Monarch pool. Those slots replace the regular queue article for
  that hour; the queue simply continues in the following slot.
- Rotation: pick the pool page after the last one logged with that pool's cycle
  value, wrapping to the top. Skip a page that was posted (by pool or queue) in the
  previous 2 days and take the next one.
- Log pool posts with cycle `pool:monarch` or `pool:life`.
- Captions follow every rule below. Pool pages repeat often (the life-insurance
  pool every 3 days), so each post must use a different takeaway or angle than that
  page's earlier posts in `social-log.md`, and never repeat earlier text. The link
  is the article page, never the affiliate link itself.
- Life-insurance posts state facts from the page only: no claims about what anyone
  should buy, no prices or quotes not on the page, no fear-based hooks.

## Writing each post

- Facts come only from the article's own Key Takeaways (or, if it has none, its
  meta description and first paragraph). These were sourced when the article was
  published. Never add a number or claim that is not on the page.
- Structure: a hook or striking fact, one or two short sentences, a blank line,
  a short call to action ending in the link, then 1–2 relevant hashtags.
- Link format: `https://topmoneyapps.com/<file>?utm_source=x&utm_medium=social&utm_campaign=article_cycle`
- Length: at most 280 characters, counting the link as 23 characters.
- Every post must be new text. On a second or later cycle, use a different angle
  and, where possible, a different takeaway than the article's earlier posts in
  `social-log.md` (a question, a myth vs. fact, a surprising comparison, a
  checklist item). Never post the same text twice.
- Tone: plain, specific, curious. No clickbait that the article does not back up,
  no hype words, no promises about returns, no advice to buy or sell anything.
  At most one emoji, and usually none.
- Hashtags: 1–2, broad and relevant (#PersonalFinance, #Investing, #Taxes,
  #Retirement, #Budgeting, #Credit, #SocialSecurity...). Never trending tags
  unrelated to the post.

## Never post

- Pages about Acorns (Mike works there): any file with `acorns` in its name.
- Legal pages, hubs, redirect stubs, the homepage or the author page.
- Anything during a breaking news event that would make the post look tone-deaf;
  if in doubt, skip that hour and note it.
