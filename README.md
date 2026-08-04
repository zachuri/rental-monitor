# rental-monitor

![rental-monitor hero](docs/hero.png)

A GitHub Actions template that watches rental listings in your target
neighborhood and opens a GitHub Issue whenever new listings appear. Powered
by the [Rentcast API](https://rentcast.io). No code changes required — just
edit a config file, set one secret, and push.

[![Use this template](https://img.shields.io/badge/Use_this_template-2ea44f?style=for-the-badge&logo=github)](../../generate)

---

## How it works

1. A daily cron job (or manual trigger) calls the Rentcast long-term rental
   listings API for your configured ZIP code or circular search area.
2. Results are filtered by optional street names and per-bedroom price caps.
3. Listings not seen before are recorded in `data/seen-listings.json`.
4. A GitHub Issue is opened with a digest of every new listing.
5. A heartbeat file (`data/last-run.json`) is committed on every run so you
   can tell the monitor is alive even when there are no new listings.

---

## Setup (under 10 minutes)

### 1. Create your repository from this template

Click **Use this template** above and create a new **private** repository.

> Private is recommended because `data/seen-listings.json` (listing IDs) and
> the raw API artifacts are committed or uploaded to the repo.

### 2. Get a Rentcast API key

1. Sign up at [app.rentcast.io](https://app.rentcast.io)
2. Go to **API** in the sidebar and copy your key.

The free tier provides enough requests for personal daily monitoring.

### 3. Add the secret

In your new repository:

1. Go to **Settings → Secrets and variables → Actions → New repository secret**
2. Name: `RENTCAST_API_KEY`
3. Value: your Rentcast API key

### 4. Edit `monitor-config.yml`

Open `monitor-config.yml` and update the values for your target area. This
private copy uses a circular Orange County search so several nearby cities fit
in one API request:

```yaml
search:
  latitude: 33.739224
  longitude: -117.858379
  radius: 18               # Miles

streets: []                # Empty means the entire search area

price_caps:                # Max total monthly rent per bedroom count
  2br: YOUR_2BR_CAP
  3br: YOUR_3BR_CAP

bedrooms: "2:3"            # Bedroom range for the API query
```

### 5. Push

Commit and push your `monitor-config.yml` changes. The **Setup Validation**
workflow triggers automatically whenever `monitor-config.yml` is pushed to
`main` and will open a GitHub Issue if anything is missing.

> **Using the default config?** If you are happy with the Newport Coast sample
> values and have not edited `monitor-config.yml`, the path-filtered trigger
> will not fire. In that case, go to **Actions → Setup Validation → Run
> workflow** and trigger it manually to confirm your secret is in place.

Once setup passes, wait for the next scheduled run (8 AM Pacific by default)
or trigger the **Rental Monitor** workflow manually from the **Actions** tab.

---

## Adjusting the schedule

Edit the `cron` expression in `.github/workflows/monitor.yml`:

```yaml
- cron: '0 15 * * *'  # 8 AM Pacific (UTC-7 PDT)
```

Use [crontab.guru](https://crontab.guru/) to generate the right expression
for your timezone.

### Monthly request guard

This private copy enforces a hard limit of **50 RentCast requests per calendar
month**. Before every scheduled, manual, or dry run, the workflow reserves one
request in `data/api-usage.json`. At 50, further API calls are skipped until the
next UTC calendar month. The guard covers requests made by this repository; it
cannot count requests made elsewhere with the same API key.

---

## Ad-hoc runs and dry runs

From **Actions → Rental Monitor → Run workflow** you can:

- **Override zip code**: test a different ZIP without editing the config.
- **Dry run**: fetch and filter listings, log matches, but do **not** open
  issues or update `seen-listings.json`. It still uses one RentCast request,
  but avoids issue and repository-write side effects while testing the config.

---

## Failure notifications

If the workflow errors (e.g., API key expired, Rentcast outage), it
automatically opens a GitHub Issue labeled `monitor-failure` with a link to
the failed run. You will never mistake silence for success.

---

## Local testing with the fixture

A synthetic fixture at `data/fixtures/oc-sample-response.json` covers the
area-wide and price-cap behavior in this private configuration. You can test
the full pipeline locally without making any API calls:

```bash
./simulate.sh data/fixtures/oc-sample-response.json
tests/test_build_search_query.sh
tests/test_oc_simulation.sh
```

Expected: the query-builder and area-wide simulation tests pass. The simulated
monitor accepts two in-budget fixtures and excludes the over-cap fixture.

---

## Repository layout

```
.
├── .github/
│   └── workflows/
│       ├── monitor.yml          # Daily rental monitor
│       └── setup.yml            # One-shot setup validation
├── data/
│   ├── fixtures/
│   │   └── sample-response.json # Synthetic listings for local testing
│   ├── last-run.json            # Heartbeat: written on every run
│   └── seen-listings.json       # IDs + first-seen dates; committed by workflow
├── LICENSE
├── NOTICE
├── README.md
└── monitor-config.yml           # Your configuration — edit this
```

---

## Data and privacy

See [NOTICE](NOTICE) for details on Rentcast attribution and personal-use
scope. Key points:

- `data/seen-listings.json` stores **only listing IDs and first-seen dates**,
  not full listing data.
- The raw Rentcast API response is uploaded as an Actions artifact with a
  7-day retention period and is never committed.
- This tool is for **personal, non-commercial use only**.

---

## License

MIT — see [LICENSE](LICENSE).
