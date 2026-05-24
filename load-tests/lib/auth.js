import http from 'k6/http';
import { fail } from 'k6';

/**
 * Login via POST /auth/login and return JWT from HttpOnly cookie (access_token).
 * Login is only called from setup() — never per-VU — to avoid 5/min rate limit.
 */
export function login(baseUrl, email, password) {
  const res = http.post(
    `${baseUrl}/api/v1/auth/login`,
    JSON.stringify({ email, password }),
    { headers: { 'Content-Type': 'application/json' }, tags: { scenario: 'auth' } },
  );
  if (res.status !== 200) {
    fail(`login failed: ${res.status} ${res.body}`);
  }
  const cookies = res.cookies['access_token'];
  if (!cookies || cookies.length === 0) {
    fail('login response missing access_token cookie');
  }
  return cookies[0].value;
}

export function authHeaders(token) {
  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
}
