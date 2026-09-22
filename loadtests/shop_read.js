import http from 'k6/http'
import { check, sleep } from 'k6'
import { Rate, Trend } from 'k6/metrics'

/**
 * Heavy read-oriented load against Gisoo storefront APIs.
 *
 * Usage:
 *   k6 run -e BASE_URL=http://127.0.0.1:8000 loadtests/shop_read.js
 */

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000'

export const options = {
  scenarios: {
    heavy_traffic: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 50 },
        { duration: '1m', target: 120 },
        { duration: '1m', target: 200 },
        { duration: '30s', target: 0 },
      ],
      gracefulRampDown: '20s',
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.1'],
    http_req_duration: ['p(95)<3000'],
  },
}

const failRate = new Rate('gisoo_fail_rate')
const homeDuration = new Trend('gisoo_home_ms')

export default function () {
  const endpoints = [
    '/api/home/v1/banner/slides/',
    '/api/home/v1/home/sliders/',
    '/api/home/v1/about/',
    '/api/home/v1/social-links/',
    '/api/products/v1/',
    '/api/products/v1/filters/',
    '/api/products/v1/categories/',
    '/api/products/v1/brands/',
    '/api/products/v1/hair/types/',
    '/api/products/v1/hair/problems/',
  ]

  const path = endpoints[Math.floor(Math.random() * endpoints.length)]
  const res = http.get(`${BASE_URL}${path}`, {
    tags: { name: path },
    timeout: '15s',
  })

  const ok = check(res, {
    'status is 2xx/3xx': (r) => r.status >= 200 && r.status < 400,
  })
  failRate.add(!ok)
  if (path.includes('about') || path.includes('banners')) {
    homeDuration.add(res.timings.duration)
  }

  sleep(0.3 + Math.random() * 0.7)
}

export function handleSummary(data) {
  return {
    'loadtests/results/shop_read_summary.json': JSON.stringify(data, null, 2),
    stdout: textSummary(data),
  }
}

function textSummary(data) {
  const m = data.metrics || {}
  const lines = [
    '=== Gisoo k6 shop_read summary ===',
    `http_reqs: ${m.http_reqs?.values?.count ?? 'n/a'}`,
    `http_req_failed: ${((m.http_req_failed?.values?.rate ?? 0) * 100).toFixed(2)}%`,
    `http_req_duration p95: ${(m.http_req_duration?.values['p(95)'] ?? 0).toFixed(1)} ms`,
    `vus_max: ${m.vus_max?.values?.max ?? 'n/a'}`,
    `gisoo_fail_rate: ${((m.gisoo_fail_rate?.values?.rate ?? 0) * 100).toFixed(2)}%`,
  ]
  return lines.join('\n') + '\n'
}
