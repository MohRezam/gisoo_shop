import http from 'k6/http'
import { check, sleep } from 'k6'

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000'

export const options = {
  scenarios: {
    light: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '10s', target: 10 },
        { duration: '20s', target: 20 },
        { duration: '10s', target: 0 },
      ],
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.2'],
    http_req_duration: ['p(95)<5000'],
  },
}

export default function () {
  const paths = [
    '/api/home/v1/about/',
    '/api/home/v1/banner/slides/',
    '/api/products/v1/',
    '/api/products/v1/filters/',
  ]
  const path = paths[Math.floor(Math.random() * paths.length)]
  const res = http.get(`${BASE_URL}${path}`, { tags: { name: path }, timeout: '10s' })
  check(res, { '2xx': (r) => r.status >= 200 && r.status < 300 })
  sleep(0.5)
}

export function handleSummary(data) {
  return {
    'loadtests/results/shop_light_summary.json': JSON.stringify(data, null, 2),
    stdout: [
      '=== Gisoo k6 light summary ===',
      `http_reqs: ${data.metrics?.http_reqs?.values?.count ?? 'n/a'}`,
      `failed: ${((data.metrics?.http_req_failed?.values?.rate ?? 0) * 100).toFixed(2)}%`,
      `p95: ${(data.metrics?.http_req_duration?.values['p(95)'] ?? 0).toFixed(1)} ms`,
      `avg: ${(data.metrics?.http_req_duration?.values?.avg ?? 0).toFixed(1)} ms`,
      `vus_max: ${data.metrics?.vus_max?.values?.max ?? 'n/a'}`,
    ].join('\n') + '\n',
  }
}
