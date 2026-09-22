import http from 'k6/http'
import { check, sleep } from 'k6'
import { Rate } from 'k6/metrics'

/**
 * Shorter smoke load (use when validating harness / CI).
 * Heavy scenario: shop_read.js
 */

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000'

export const options = {
  scenarios: {
    smoke: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '15s', target: 30 },
        { duration: '20s', target: 80 },
        { duration: '15s', target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.95'],
  },
}

const failRate = new Rate('gisoo_fail_rate')

export default function () {
  const paths = [
    '/api/home/v1/about/',
    '/api/products/v1/',
    '/api/products/v1/filters/',
  ]
  const path = paths[Math.floor(Math.random() * paths.length)]
  const res = http.get(`${BASE_URL}${path}`, { tags: { name: path }, timeout: '10s' })
  const ok = check(res, { '2xx': (r) => r.status >= 200 && r.status < 300 })
  failRate.add(!ok)
  sleep(0.2)
}

export function handleSummary(data) {
  return {
    'loadtests/results/shop_smoke_summary.json': JSON.stringify(data, null, 2),
    stdout: [
      '=== Gisoo k6 smoke summary ===',
      `http_reqs: ${data.metrics?.http_reqs?.values?.count ?? 'n/a'}`,
      `failed: ${((data.metrics?.http_req_failed?.values?.rate ?? 0) * 100).toFixed(2)}%`,
      `p95: ${(data.metrics?.http_req_duration?.values['p(95)'] ?? 0).toFixed(1)} ms`,
      `vus_max: ${data.metrics?.vus_max?.values?.max ?? 'n/a'}`,
    ].join('\n') + '\n',
  }
}
