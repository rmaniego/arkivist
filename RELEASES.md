# Release Tags

## Notes

### Archivist package

- **Package Name**: Archivist
- **Short Code**: AK
- **First Release Tag**: AK.010.001

## Release Tags

On **2026-07-04** the weekly release tags were reconstructed retroactively from the
repository's commit history, so the `00Z` build numbers reflect the actual development
timeline rather than starting from the day tagging began.

### How the tags were derived

- **Week boundaries** follow ISO-8601 (Monday–Sunday) in a standard 52-week year.
- **Maintenance branch `Y`** tracks the published package's minor version at each
  commit (`1.0.x` → `AK.010`, `1.1.x` → `AK.011`, and so on); each branch's `00Z`
  build numbering resets to `001` and increments by one for **each subsequent ISO
  week that contains at least one commit**. Weeks with no commits are skipped and
  do **not** consume a build number (see the gaps below).
- **Releases are cut on Friday.** Each tag is annotated, points to the **last commit
  of its ISO week** (that week's release cut), and is dated on the week's Friday —
  clamped forward to the commit date on the rare week whose work only landed on the
  weekend, so a tag never predates the commit it marks.
- The repository's very first commit predates the `1.0.0` version stamp by two hours
  and falls in the same ISO week, so it belongs to the `AK.010` branch.
- Bucketing uses each commit's **committer date**.

### Branch overview

| Branch | Version line | Builds | Span |
| --- | --- | --- | --- |
| `AK.010` | 1.0.x | 13 | 2020-W45 → 2021-W25 |
| `AK.011` | 1.1.x | 3 | 2022-W11 → 2022-W14 |
| `AK.012` | 1.2.x | 4 | 2022-W15 → 2022-W45 |
| `AK.013` | 1.3.x | 2 | 2022-W45 → 2022-W47 |
| `AK.014` | 1.4.x | 1 | 2026-W27 |

> 2022-W45 closes with two release cuts: `AK.012.004` on the last `1.2.x` commit and
> `AK.013.001` on the first `1.3.x` cut, since the version bump resets `00Z` to `001`
> mid-week.

### AK.010 (v1.0.x)

| Tag | ISO week | Release (Fri) | Commit |
| --- | --- | --- | --- |
| `AK.010.001` | 2020-W45 | 2020-11-08 | `a752b06` |
| `AK.010.002` | 2020-W46 | 2020-11-15 | `9990e37` |
| `AK.010.003` | 2020-W49 | 2020-12-06 | `ec8b530` |
| `AK.010.004` | 2020-W50 | 2020-12-13 | `75363cb` |
| `AK.010.005` | 2020-W51 | 2020-12-18 | `46a3930` |
| `AK.010.006` | 2020-W52 | 2020-12-26 | `e8b05cf` |
| `AK.010.007` | 2021-W01 | 2021-01-08 | `99e9089` |
| `AK.010.008` | 2021-W12 | 2021-03-26 | `c1a57d6` |
| `AK.010.009` | 2021-W15 | 2021-04-16 | `6819e5d` |
| `AK.010.010` | 2021-W21 | 2021-05-28 | `41afb06` |
| `AK.010.011` | 2021-W22 | 2021-06-04 | `7deb6a2` |
| `AK.010.012` | 2021-W23 | 2021-06-11 | `7211477` |
| `AK.010.013` | 2021-W25 | 2021-06-25 | `35079c0` |

### AK.011 (v1.1.x)

| Tag | ISO week | Release (Fri) | Commit |
| --- | --- | --- | --- |
| `AK.011.001` | 2022-W11 | 2022-03-18 | `ebf7331` |
| `AK.011.002` | 2022-W13 | 2022-04-01 | `6365c46` |
| `AK.011.003` | 2022-W14 | 2022-04-08 | `a7c28a6` |

### AK.012 (v1.2.x)

| Tag | ISO week | Release (Fri) | Commit |
| --- | --- | --- | --- |
| `AK.012.001` | 2022-W15 | 2022-04-16 | `0b653eb` |
| `AK.012.002` | 2022-W16 | 2022-04-22 | `48300be` |
| `AK.012.003` | 2022-W17 | 2022-04-29 | `a3a2881` |
| `AK.012.004` | 2022-W45 | 2022-11-11 | `4e8a622` |

### AK.013 (v1.3.x)

| Tag | ISO week | Release (Fri) | Commit |
| --- | --- | --- | --- |
| `AK.013.001` | 2022-W45 | 2022-11-11 | `6efbbd8` |
| `AK.013.002` | 2022-W47 | 2022-11-25 | `2a6f391` |

### AK.014 (v1.4.x)

| Tag | ISO week | Release (Fri) | Commit |
| --- | --- | --- | --- |
| `AK.014.001` | 2026-W27 | 2026-07-04 | `4b48980` |

Current release: **`AK.014.001`**.
