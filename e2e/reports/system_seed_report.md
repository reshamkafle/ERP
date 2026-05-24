# System Seed Report

- **Started:** 2026-05-23T14:21:09+00:00
- **Finished:** 2026-05-23T14:23:32+00:00
- **Target per type:** 1
- **Total attempted:** 27
- **Total succeeded:** 19
- **Total failed:** 8

## Results by document type

| Document type | Label | Attempted | Succeeded | Failed |
| --- | --- | ---: | ---: | ---: |
| customer | Customer | 1 | 1 | 0 |
| supplier | Supplier / Vendor | 1 | 1 | 0 |
| warehouse | Warehouse | 1 | 1 | 0 |
| location | Warehouse Location | 1 | 0 | 1 |
| sales_order | Sales Order | 1 | 0 | 1 |
| purchase_requisition | Purchase Requisition | 1 | 1 | 0 |
| purchase_order_procurement | Procurement PO Record | 1 | 1 | 0 |
| grn | Goods Receipt (GRN) | 1 | 1 | 0 |
| invoice_matching | Invoice Matching | 1 | 1 | 0 |
| purchase_order | Purchase (Quick Receive) | 1 | 0 | 1 |
| pos_sale | POS Checkout | 1 | 0 | 1 |
| trading_inventory | Trading Inventory | 1 | 1 | 0 |
| raw_material_inventory | Raw Material Inventory | 1 | 1 | 0 |
| finished_goods_inventory | Finished Goods Inventory | 1 | 1 | 0 |
| bill_of_materials | Bill of Materials | 1 | 1 | 0 |
| work_order | Production Order | 1 | 0 | 1 |
| crm_lead | CRM Lead | 1 | 1 | 0 |
| crm_opportunity | CRM Opportunity | 1 | 0 | 1 |
| crm_campaign | CRM Marketing Campaign | 1 | 0 | 1 |
| tms_shipment | TMS Shipment | 1 | 0 | 1 |
| module_warehouse_module | Module hub (warehouse_module) | 1 | 1 | 0 |
| module_sales_distribution | Module hub (sales_distribution) | 1 | 1 | 0 |
| module_projects | Module hub (projects) | 1 | 1 | 0 |
| module_platform | Module hub (platform) | 1 | 1 | 0 |
| module_finance | Module records (finance) | 1 | 1 | 0 |
| module_hcm | Module records (hcm) | 1 | 1 | 0 |
| module_scm | Module records (scm) | 1 | 1 | 0 |

## Errors

- **location #1:** Message: 
Stacktrace:
0   chromedriver                        0x000000010286cc40 cxxbridge1$str$ptr + 3221216
1   chromedriver                        0x0000000102864b1c cxxbridge1$str$ptr + 3188156
2   chromedriver                        0x00000001023278f4 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 75152
3   chromedriver                        0x000000010236fff8 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 371860
4   chromedriver                        0x00000001023af6f4 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 631696
5   chromedriver                        0x00000001023659c0 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 329308
6   chromedriver                        0x000000010282ab70 cxxbridge1$str$ptr + 2950672
7   chromedriver                        0x000000010282e2c8 cxxbridge1$str$ptr + 2964840
8   chromedriver                        0x000000010280f8a8 cxxbridge1$str$ptr + 2839368
9   chromedriver                        0x000000010282eb48 cxxbridge1$str$ptr + 2967016
10  chromedriver                        0x00000001028003d4 cxxbridge1$str$ptr + 2776692
11  chromedriver                        0x00000001028537ac cxxbridge1$str$ptr + 3117644
12  chromedriver                        0x000000010285390c cxxbridge1$str$ptr + 3117996
13  chromedriver                        0x0000000102864774 cxxbridge1$str$ptr + 3187220
14  libsystem_pthread.dylib             0x000000019233fc08 _pthread_start + 136
15  libsystem_pthread.dylib             0x000000019233aba8 thread_start + 8

  - Screenshot: `reports/screenshots/location-1.png`
- **sales_order #1:** Message: 
Stacktrace:
0   chromedriver                        0x000000010286cc40 cxxbridge1$str$ptr + 3221216
1   chromedriver                        0x0000000102864b1c cxxbridge1$str$ptr + 3188156
2   chromedriver                        0x00000001023278f4 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 75152
3   chromedriver                        0x000000010236fff8 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 371860
4   chromedriver                        0x00000001023af6f4 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 631696
5   chromedriver                        0x00000001023659c0 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 329308
6   chromedriver                        0x000000010282ab70 cxxbridge1$str$ptr + 2950672
7   chromedriver                        0x000000010282e2c8 cxxbridge1$str$ptr + 2964840
8   chromedriver                        0x000000010280f8a8 cxxbridge1$str$ptr + 2839368
9   chromedriver                        0x000000010282eb48 cxxbridge1$str$ptr + 2967016
10  chromedriver                        0x00000001028003d4 cxxbridge1$str$ptr + 2776692
11  chromedriver                        0x00000001028537ac cxxbridge1$str$ptr + 3117644
12  chromedriver                        0x000000010285390c cxxbridge1$str$ptr + 3117996
13  chromedriver                        0x0000000102864774 cxxbridge1$str$ptr + 3187220
14  libsystem_pthread.dylib             0x000000019233fc08 _pthread_start + 136
15  libsystem_pthread.dylib             0x000000019233aba8 thread_start + 8

  - Screenshot: `reports/screenshots/sales_order-1.png`
- **purchase_order #1:** Message: 
Stacktrace:
0   chromedriver                        0x000000010286cc40 cxxbridge1$str$ptr + 3221216
1   chromedriver                        0x0000000102864b1c cxxbridge1$str$ptr + 3188156
2   chromedriver                        0x00000001023278f4 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 75152
3   chromedriver                        0x000000010236fff8 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 371860
4   chromedriver                        0x00000001023af6f4 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 631696
5   chromedriver                        0x00000001023659c0 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 329308
6   chromedriver                        0x000000010282ab70 cxxbridge1$str$ptr + 2950672
7   chromedriver                        0x000000010282e2c8 cxxbridge1$str$ptr + 2964840
8   chromedriver                        0x000000010280f8a8 cxxbridge1$str$ptr + 2839368
9   chromedriver                        0x000000010282eb48 cxxbridge1$str$ptr + 2967016
10  chromedriver                        0x00000001028003d4 cxxbridge1$str$ptr + 2776692
11  chromedriver                        0x00000001028537ac cxxbridge1$str$ptr + 3117644
12  chromedriver                        0x000000010285390c cxxbridge1$str$ptr + 3117996
13  chromedriver                        0x0000000102864774 cxxbridge1$str$ptr + 3187220
14  libsystem_pthread.dylib             0x000000019233fc08 _pthread_start + 136
15  libsystem_pthread.dylib             0x000000019233aba8 thread_start + 8

  - Screenshot: `reports/screenshots/purchase_order-1.png`
- **pos_sale #1:** Message: 
Stacktrace:
0   chromedriver                        0x000000010286cc40 cxxbridge1$str$ptr + 3221216
1   chromedriver                        0x0000000102864b1c cxxbridge1$str$ptr + 3188156
2   chromedriver                        0x00000001023278f4 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 75152
3   chromedriver                        0x000000010236fff8 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 371860
4   chromedriver                        0x00000001023af6f4 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 631696
5   chromedriver                        0x00000001023659c0 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 329308
6   chromedriver                        0x000000010282ab70 cxxbridge1$str$ptr + 2950672
7   chromedriver                        0x000000010282e2c8 cxxbridge1$str$ptr + 2964840
8   chromedriver                        0x000000010280f8a8 cxxbridge1$str$ptr + 2839368
9   chromedriver                        0x000000010282eb48 cxxbridge1$str$ptr + 2967016
10  chromedriver                        0x00000001028003d4 cxxbridge1$str$ptr + 2776692
11  chromedriver                        0x00000001028537ac cxxbridge1$str$ptr + 3117644
12  chromedriver                        0x000000010285390c cxxbridge1$str$ptr + 3117996
13  chromedriver                        0x0000000102864774 cxxbridge1$str$ptr + 3187220
14  libsystem_pthread.dylib             0x000000019233fc08 _pthread_start + 136
15  libsystem_pthread.dylib             0x000000019233aba8 thread_start + 8

  - Screenshot: `reports/screenshots/pos_sale-1.png`
- **work_order #1:** Message: 

  - Screenshot: `reports/screenshots/work_order-1.png`
- **crm_opportunity #1:** Message: 

  - Screenshot: `reports/screenshots/crm_opportunity-1.png`
- **crm_campaign #1:** Message: element click intercepted: Element <button type="button" tabindex="0" data-slot="button" class="group/button inline-flex shrink-0 items-center justify-center border bg-clip-padding font-medium whitespace-nowrap transition-all outline-none select-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 active:not-aria-[haspopup]:translate-y-px disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20 dark:aria-invalid:border-destructive/50 dark:aria-invalid:ring-destructive/40 [&amp;_svg]:pointer-events-none [&amp;_svg]:shrink-0 border-border bg-background hover:bg-muted hover:text-foreground aria-expanded:bg-muted aria-expanded:text-foreground dark:border-input dark:bg-input/30 dark:hover:bg-input/50 h-7 gap-1 rounded-[min(var(--radius-md),12px)] px-2.5 text-[0.8rem] in-data-[slot=button-group]:rounded-lg has-data-[icon=inline-end]:pr-1.5 has-data-[icon=inline-start]:pl-1.5 [&amp;_svg:not([class*='size-'])]:size-3.5">...</button> is not clickable at point (803, 290). Other element would receive the click: <div>...</div>
  (Session info: chrome=148.0.7778.179); For documentation on this error, please visit: https://www.selenium.dev/documentation/webdriver/troubleshooting/errors#elementclickinterceptedexception
Stacktrace:
0   chromedriver                        0x000000010286cc40 cxxbridge1$str$ptr + 3221216
1   chromedriver                        0x0000000102864b1c cxxbridge1$str$ptr + 3188156
2   chromedriver                        0x00000001023278f4 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 75152
3   chromedriver                        0x0000000102375628 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 393924
4   chromedriver                        0x0000000102373e94 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 387888
5   chromedriver                        0x0000000102371f40 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 379868
6   chromedriver                        0x00000001023712e4 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 376704
7   chromedriver                        0x0000000102367448 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 336100
8   chromedriver                        0x0000000102366ec4 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 334688
9   chromedriver                        0x00000001023af6f4 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 631696
10  chromedriver                        0x00000001023659c0 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 329308
11  chromedriver                        0x000000010282ab70 cxxbridge1$str$ptr + 2950672
12  chromedriver                        0x000000010282e2c8 cxxbridge1$str$ptr + 2964840
13  chromedriver                        0x000000010280f8a8 cxxbridge1$str$ptr + 2839368
14  chromedriver                        0x000000010282eb48 cxxbridge1$str$ptr + 2967016
15  chromedriver                        0x00000001028003d4 cxxbridge1$str$ptr + 2776692
16  chromedriver                        0x00000001028537ac cxxbridge1$str$ptr + 3117644
17  chromedriver                        0x000000010285390c cxxbridge1$str$ptr + 3117996
18  chromedriver                        0x0000000102864774 cxxbridge1$str$ptr + 3187220
19  libsystem_pthread.dylib             0x000000019233fc08 _pthread_start + 136
20  libsystem_pthread.dylib             0x000000019233aba8 thread_start + 8

  - Screenshot: `reports/screenshots/crm_campaign-1.png`
- **tms_shipment #1:** Message: 
Stacktrace:
0   chromedriver                        0x000000010286cc40 cxxbridge1$str$ptr + 3221216
1   chromedriver                        0x0000000102864b1c cxxbridge1$str$ptr + 3188156
2   chromedriver                        0x00000001023278f4 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 75152
3   chromedriver                        0x000000010236fff8 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 371860
4   chromedriver                        0x00000001023af6f4 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 631696
5   chromedriver                        0x00000001023659c0 _RNvCsiKAbIcglKMQ_7___rustc35___rust_no_alloc_shim_is_unstable_v2 + 329308
6   chromedriver                        0x000000010282ab70 cxxbridge1$str$ptr + 2950672
7   chromedriver                        0x000000010282e2c8 cxxbridge1$str$ptr + 2964840
8   chromedriver                        0x000000010280f8a8 cxxbridge1$str$ptr + 2839368
9   chromedriver                        0x000000010282eb48 cxxbridge1$str$ptr + 2967016
10  chromedriver                        0x00000001028003d4 cxxbridge1$str$ptr + 2776692
11  chromedriver                        0x00000001028537ac cxxbridge1$str$ptr + 3117644
12  chromedriver                        0x000000010285390c cxxbridge1$str$ptr + 3117996
13  chromedriver                        0x0000000102864774 cxxbridge1$str$ptr + 3187220
14  libsystem_pthread.dylib             0x000000019233fc08 _pthread_start + 136
15  libsystem_pthread.dylib             0x000000019233aba8 thread_start + 8

  - Screenshot: `reports/screenshots/tms_shipment-1.png`

## Known gaps (not seeded)

- **Delivery Order:** No standalone create UI; only /sales?delivery_filter=open list filter.
- **Production Planning / MRP:** No bulk create UI; MRP runs are API-driven.
- **RAW / FINISHED inventory (bulk seed):** Multi-tab inventory form does not submit reliably for non-TRADING types in headless Chrome; seeded via API in system seed.
- **BOM garment SKUs (masters):** Manufacturing item master has no create UI; parent SKUs use DB helper before Selenium BOM lines.
