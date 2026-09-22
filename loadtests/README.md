# k6 load tests for Gisoo Center

## Prerequisites

- Install [k6](https://k6.io/docs/get-started/installation/)
- API running locally (default `http://127.0.0.1:8000`)

## Run heavy traffic

```bash
k6 run -e BASE_URL=http://127.0.0.1:8000 loadtests/shop_read.js
```

Windows (PowerShell):

```powershell
k6 run -e BASE_URL=http://127.0.0.1:8000 .\loadtests\shop_read.js
```

Summary JSON is written to `loadtests/results/shop_read_summary.json`.
