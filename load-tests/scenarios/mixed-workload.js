import { sleep } from 'k6';
import { login, authHeaders } from '../lib/auth.js';
import {
  getJson,
  ok,
  pickRandom,
  postJson,
  thinkTime,
  todayIso,
  weightedPick,
} from '../lib/helpers.js';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const VOLUME_MODE = __ENV.VOLUME_MODE === '1';
const LIST_LIMIT = VOLUME_MODE ? '200' : '50';

export const options = {
  stages: [
    { duration: '3m', target: 200 },
    { duration: '12m', target: 200 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],
    'http_req_duration{scenario:read}': ['p(95)<800'],
    'http_req_duration{scenario:reports}': ['p(95)<800'],
    'http_req_duration{scenario:checkout}': ['p(95)<2000'],
    'http_req_duration{scenario:write}': ['p(95)<2000'],
  },
};

export function setup() {
  const token = login(BASE_URL, __ENV.ADMIN_EMAIL, __ENV.ADMIN_PASSWORD);
  const headers = authHeaders(token);

  let productsRes = getJson(BASE_URL, '/api/v1/sales/products?limit=50', headers, 'read');
  let products = [];
  if (productsRes.status === 200) {
    products = JSON.parse(productsRes.body).items || [];
  }

  if (products.length === 0) {
    const sku = `LOAD-${Date.now()}`;
    const createRes = postJson(
      BASE_URL,
      '/api/v1/inventory',
      {
        sku,
        name: `Load Test Product ${sku}`,
        lifecycle_status: 'ACTIVE',
        initial_stock: 10000,
        price: '19.99',
        cost_price: '8.00',
        low_stock_threshold: 10,
      },
      headers,
      'write',
    );
    if (createRes.status >= 200 && createRes.status < 300) {
      const p = JSON.parse(createRes.body);
      products = [{ id: p.id, sku: p.sku, price: p.price }];
    }
  }

  const suppliersRes = getJson(BASE_URL, '/api/v1/suppliers?limit=20', headers, 'read');
  const suppliers =
    suppliersRes.status === 200 ? JSON.parse(suppliersRes.body).items || [] : [];

  const customersRes = getJson(BASE_URL, '/api/v1/customers?limit=20', headers, 'read');
  const customers =
    customersRes.status === 200 ? JSON.parse(customersRes.body).items || [] : [];

  const pmRes = getJson(BASE_URL, '/api/v1/payment-methods', headers, 'read');
  const paymentMethods = pmRes.status === 200 ? JSON.parse(pmRes.body) : [];

  const rollsRes = getJson(BASE_URL, '/api/v1/material-rolls?limit=10', headers, 'read');
  const rolls =
    rollsRes.status === 200 ? JSON.parse(rollsRes.body).items || [] : [];

  return {
    token,
    products,
    suppliers,
    customers,
    paymentMethods,
    rolls,
  };
}

function runReads(headers) {
  getJson(BASE_URL, `/api/v1/inventory?limit=${LIST_LIMIT}`, headers, 'read');
  getJson(BASE_URL, '/api/v1/search?q=test&limit=20', headers, 'read');
  getJson(BASE_URL, '/api/v1/sales?limit=50', headers, 'read');
  getJson(BASE_URL, '/api/v1/sales/products?limit=50', headers, 'read');
  getJson(BASE_URL, '/api/v1/crm/leads?limit=50', headers, 'read');
  getJson(
    BASE_URL,
    '/api/v1/erp-modules/finance/records?limit=50',
    headers,
    'read',
  );
  getJson(
    BASE_URL,
    '/api/v1/manufacturing/production-orders?limit=50',
    headers,
    'read',
  );
}

function runReports(headers) {
  getJson(BASE_URL, '/api/v1/dashboard/summary', headers, 'reports');
  getJson(BASE_URL, '/api/v1/reports/sales', headers, 'reports');
  getJson(BASE_URL, '/api/v1/reports/stock-value', headers, 'reports');
  getJson(BASE_URL, '/api/v1/reports/top-products', headers, 'reports');
}

function runCheckout(data, headers) {
  const product = pickRandom(data.products);
  if (!product) return;
  const res = postJson(
    BASE_URL,
    '/api/v1/sales/checkout',
    {
      items: [{ product_id: product.id, quantity: 1 }],
      confirm: true,
    },
    headers,
    'checkout',
  );
  ok(res, 'checkout');
}

function runPurchase(data, headers) {
  const supplier = pickRandom(data.suppliers);
  const product = pickRandom(data.products);
  if (!supplier || !product) return;
  const createRes = postJson(
    BASE_URL,
    '/api/v1/purchases',
    {
      supplier_id: supplier.id,
      items: [{ product_id: product.id, quantity: 2 }],
    },
    headers,
    'write',
  );
  if (createRes.status >= 200 && createRes.status < 300) {
    const purchase = JSON.parse(createRes.body);
    postJson(
      BASE_URL,
      `/api/v1/purchases/${purchase.id}/confirm`,
      {},
      headers,
      'write',
    );
  }
}

function runPayment(data, headers) {
  const customer = pickRandom(data.customers);
  const pm = pickRandom(data.paymentMethods);
  if (!customer || !pm) return;
  postJson(
    BASE_URL,
    '/api/v1/payments/receive',
    {
      customer_id: customer.id,
      payment_method_id: pm.id,
      amount: '10.00',
      payment_date: todayIso(),
      reference: `LOAD-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    },
    headers,
    'write',
  );
}

function runScan(data, headers) {
  const roll = pickRandom(data.rolls);
  if (!roll) return;
  const identifier = roll.barcode || roll.roll_number || roll.rfid_tag;
  if (!identifier) return;
  const body =
    roll.barcode != null
      ? { barcode: roll.barcode }
      : roll.roll_number != null
        ? { roll_number: roll.roll_number }
        : { rfid_tag: roll.rfid_tag };
  postJson(BASE_URL, '/api/v1/material-rolls/scan', body, headers, 'write');
}

export default function (data) {
  const headers = authHeaders(data.token);
  const bucket = weightedPick({
    transactional: 0.4,
    reporting: 0.3,
    search: 0.2,
    scan: 0.1,
  });

  if (bucket === 'transactional') {
    const action = weightedPick({ checkout: 0.5, purchase: 0.3, payment: 0.2 });
    if (action === 'checkout') runCheckout(data, headers);
    else if (action === 'purchase') runPurchase(data, headers);
    else runPayment(data, headers);
  } else if (bucket === 'reporting') {
    runReports(headers);
  } else if (bucket === 'search') {
    runReads(headers);
  } else {
    runScan(data, headers);
  }

  sleep(thinkTime());
}
