# k6 report (live local backend)

Backend: Django `runserver` + SQLite (`LOCAL_DB_ENABLED=True`) on `127.0.0.1:8000`
(Postgres/Docker were not available on this machine.)

## Heavy test (`shop_read.js`, up to 200 VUs)

| Metric | Value |
|--------|--------|
| Requests | 8876 |
| Failed | ~99.5% (timeouts) |
| p95 | ~15s |
| Max VUs | 200 |

Local `runserver` + SQLite cannot sustain this load.

## Light test (`shop_light.js`, up to 20 VUs)

| Metric | Value |
|--------|--------|
| Requests | 108 |
| Failed | 0% |
| Checks passed | 100% |
| Avg latency | ~4.1s |
| p95 | ~6.4s |
| Max VUs | 20 |

All responses OK; site is slow under even moderate concurrent load on this local stack.
