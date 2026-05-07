# Sam PTO Calculator

Track your Paid Time Off accrual and usage. Two flavors:

- **`index.html`** — web app with a calendar UI. Works on phone and desktop. No install.
- **`pto_tracker.py`** — original command-line version.

## Web app (recommended)

### Run locally
Just double-click `index.html` (or open it in any browser). All data is stored in your browser's `localStorage` — nothing is sent anywhere.

### Host on GitHub Pages (so your phone can use it)

1. Create a new GitHub repo named `Sam-PTO-Calculator` and push these files to it.
2. On GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch → Branch: `main` / root → Save**.
3. Wait ~30 seconds, then visit `https://<your-username>.github.io/Sam-PTO-Calculator/`.
4. On your phone: open that URL in Safari/Chrome. Tap the share button → **Add to Home Screen** for an app-like icon.

**Note on data:** Each device stores its own data locally. Your phone and laptop will not sync. If you want sync later, we can add an export/import button or a cloud backend.

### Features
- Month grid calendar, one tap to inspect any day
- Tap a day → see balance, accrued, used, and add or remove vacation
- Live summary cards: current balance, lifetime accrued, lifetime used
- Vacation days highlighted in orange; today is ringed; days before your start date are dimmed
- Mobile-friendly, dark theme, no dependencies

### Settings
Tap the gear icon (top right) to change start date, hours per week, or accrual rate. The danger zone there can wipe all data.

**Common accrual rates:**
- `0.0385` ≈ 2 weeks/year (80 hrs)
- `0.0577` ≈ 3 weeks/year (120 hrs)
- `0.0769` ≈ 4 weeks/year (160 hrs)
- `0.0962` ≈ 5 weeks/year (200 hrs)

## Command-line version

```bash
python3 pto_tracker.py
```

Same logic, terminal interface. Data lives in `pto_data.json` next to the script.

## How balance is calculated

```
Daily Hours Worked = Hours per Week ÷ 7
Daily PTO Earned   = Daily Hours Worked × Accrual Rate
Balance(date)      = (days since start × Daily PTO Earned) − vacation hours used on or before date
```

Hours are spread evenly across all 7 days for simplicity, so PTO accrues continuously (including weekends).
