import { check } from 'k6';
import http from 'k6/http';

export function thinkTime(minSec = 3, maxSec = 8) {
  return minSec + Math.random() * (maxSec - minSec);
}

export function pickRandom(arr) {
  if (!arr || arr.length === 0) return null;
  return arr[Math.floor(Math.random() * arr.length)];
}

export function ok(res, name) {
  return check(res, {
    [`${name} status 2xx`]: (r) => r.status >= 200 && r.status < 300,
  });
}

export function getJson(baseUrl, path, headers, tag) {
  return http.get(`${baseUrl}${path}`, {
    headers,
    tags: { scenario: tag },
  });
}

export function postJson(baseUrl, path, body, headers, tag) {
  return http.post(`${baseUrl}${path}`, JSON.stringify(body), {
    headers,
    tags: { scenario: tag },
  });
}

export function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

/** Weighted random: returns key from weights object (values sum to ~1). */
export function weightedPick(weights) {
  const roll = Math.random();
  let cumulative = 0;
  for (const [key, weight] of Object.entries(weights)) {
    cumulative += weight;
    if (roll <= cumulative) return key;
  }
  return Object.keys(weights)[0];
}
