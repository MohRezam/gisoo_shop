import http from 'k6/http'
import { check, sleep } from 'k6'

/**
 * Production-safe load for ~1 vCPU / 2GB RAM app servers.
 * Run this FROM your laptop (not on the same tiny VPS).
 *
 *   k6 run -e BASE_URL=https://YOUR-DOMAIN loadtests/shop_prod.js
 */

const BASE_URL = (__ENV.BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

export const options = {
  scenarios: {
    prod_max: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 10 },  // warm-up
        { duration: '1m', target: 25 },   // normal-busy
        { duration: '1m', target: 40 },   // max realistic for 1CPU/2GB
        { duration: '30s', target: 0 },   // cool-down
      ],
      gracefulRampDown: '20s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.05'],       // <5% errors
    http_req_duration: ['p(95)<3000'],    // 95% under 3s
  },
}

const PATHS = [
  '/api/home/v1/about/',
  '/api/home/v1/banner/slides/',
  '/api/home/v1/home/sliders/',
  '/api/home/v1/social-links/',
  '/api/products/v1/',
  '/api/products/v1/filters/',
  '/api/products/v1/categories/',
  '/api/products/v1/brands/',
  '/api/products/v1/hair/types/',
  '/api/products/v1/hair/problems/',
]

export default function () {
  const path = PATHS[Math.floor(Math.random() * PATHS.length)]
  const res = http.get(`${BASE_URL}${path}`, {
    tags: { name: path },
    timeout: '15s',
  })
  check(res, {
    'status 2xx': (r) => r.status >= 200 && r.status < 300,
  })
  sleep(0.5 + Math.random() * 0.5)
}

export function handleSummary(data) {
  const failed = ((data.metrics?.http_req_failed?.values?.rate ?? 0) * 100).toFixed(2)
  const p95 = (data.metrics?.http_req_duration?.values['p(95)'] ?? 0).toFixed(1)
  const reqs = data.metrics?.http_reqs?.values?.count ?? 'n/a'
  const vus = data.metrics?.vus_max?.values?.max ?? 'n/a'
  return {
    'loadtests/results/shop_prod_summary.json': JSON.stringify(data, null, 2),
    stdout: [
      '=== Gisoo production load summary ===',
      `BASE_URL: ${BASE_URL}`,
      `http_reqs: ${reqs}`,
      `failed: ${failed}%`,
      `p95: ${p95} ms`,
      `vus_max: ${vus}`,
    ].join('\n') + '\n',
  }
}
