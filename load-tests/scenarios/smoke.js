import { sleep } from 'k6';
import { login, authHeaders } from '../lib/auth.js';
import { getJson, postJson, thinkTime, weightedPick } from '../lib/helpers.js';
import { default as mixedDefault, setup as mixedSetup } from './mixed-workload.js';

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8000';

export const options = {
  stages: [
    { duration: '1m', target: 5 },
    { duration: '1m', target: 5 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.05'],
  },
};

export function setup() {
  return mixedSetup();
}

export default function (data) {
  mixedDefault(data);
}
