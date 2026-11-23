# NBA Wins Draft 2026-27

A self-updating standings site for the wins draft. Every morning a GitHub Action pulls the current NBA standings, saves them to `data/`, and the page recalculates everything (standings, projections, odds, draft grades) in the browser.

## One-time setup (about five minutes)

1. **Create the repo.** On github.com, click **New repository**, name it something like `nba-wins-draft`, keep it **Public** (GitHub Pages is free for public repos), and create it.
2. **Upload these files.** On the new repo page choose **Add file → Upload files**, drag in everything from this folder, including the hidden `.github` folder, and commit. (If your file browser hides `.github`, upload it with the whole folder or turn on hidden files first.)
3. **Turn on Pages.** Go to **Settings → Pages**, under *Build and deployment* set Source to **Deploy from a branch**, pick `main` and `/ (root)`, save. In a minute or two the site is live at `https://<your-username>.github.io/nba-wins-draft/`.
4. **Allow the bot to commit.** Go to **Settings → Actions → General**, scroll to *Workflow permissions*, choose **Read and write permissions**, save.
5. **Run it once.** Open the **Actions** tab, click **Update standings**, then **Run workflow**. When it finishes green, the data is current. From then on it runs itself every day at 9:00 UTC.

Send Cole and Joey the Pages URL. That's it.

## Editing things

- **Vegas lines** live in `config.json` under `lines`. Change a number, commit, done.
- **Owners, colors, game pieces, draft order** are in `config.json` too.
- **If a day's update fails** (ESPN feed hiccup), the Action shows red in the Actions tab and the site keeps showing yesterday's data. Re-run it from the Actions tab.
- To force a refresh any time: Actions → Update standings → Run workflow.

## Files

- `index.html` — the whole site (one file)
- `config.json` — picks, lines, owners
- `data/standings.json` — current team records (written by the bot)
- `data/history.json` — one snapshot per owner per day, for the chart and the weekly scoreboard (written by the bot)
- `scripts/update.py` — fetches standings from ESPN
- `.github/workflows/update.yml` — the daily schedule
