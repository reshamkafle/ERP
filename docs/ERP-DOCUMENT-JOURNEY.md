# ERP Document Journey

End-to-end document flow for apparel / manufacturing / export operations. Each linked file is a placeholder for future templates and field definitions.

---

## 1. Product definition

| Step | Document | File |
|------|----------|------|
| 1.1 | Tech Packs / Spec Sheets | [tech-packs-spec-sheets.md](documents/tech-packs-spec-sheets.md) |
| 1.2 | Bill of Materials (BOM) | [bill-of-materials.md](documents/bill-of-materials.md) |

## 2. Procurement

| Step | Document | File |
|------|----------|------|
| 2.1 | Purchase Orders (POs) | [purchase-orders.md](documents/purchase-orders.md) |

## 3. Inbound & quality

| Step | Document | File |
|------|----------|------|
| 3.1 | Goods Received Note (GRN) | [goods-received-note.md](documents/goods-received-note.md) |
| 3.2 | Inspection Reports / Quality Certificates | [inspection-reports-quality-certificates.md](documents/inspection-reports-quality-certificates.md) |
| 3.3 | Lab Test Reports / Compliance Certificates | [lab-test-reports-compliance.md](documents/lab-test-reports-compliance.md) |

## 4. Production & internal stock

| Step | Document | File |
|------|----------|------|
| 4.1 | Manufacturing / Production Orders / Work Orders / Cut Tickets | [manufacturing-production-orders.md](documents/manufacturing-production-orders.md) |
| 4.2 | Stock Transfer / Issue Slips | [stock-transfer-issue-slips.md](documents/stock-transfer-issue-slips.md) |
| 4.3 | Inventory Adjustments / Cycle Count Reports | [inventory-adjustments-cycle-count.md](documents/inventory-adjustments-cycle-count.md) |

## 5. Fulfillment & outbound warehouse

| Step | Document | File |
|------|----------|------|
| 5.1 | Pick Lists / Packing Slips | [pick-lists-packing-slips.md](documents/pick-lists-packing-slips.md) |
| 5.2 | Packing List | [packing-list.md](documents/packing-list.md) |
| 5.3 | Shipping Marks / Carton Labels | [shipping-marks-carton-labels.md](documents/shipping-marks-carton-labels.md) |
| 5.4 | Advance Shipping Notice (ASN) | [advance-shipping-notice.md](documents/advance-shipping-notice.md) |

## 6. Export & trade finance

| Step | Document | File |
|------|----------|------|
| 6.1 | Commercial Invoice | [commercial-invoice.md](documents/commercial-invoice.md) |
| 6.2 | Invoices (outgoing) and Debit/Credit Notes | [invoices-debit-credit-notes.md](documents/invoices-debit-credit-notes.md) |
| 6.3 | Bill of Lading (BOL) | [bill-of-lading.md](documents/bill-of-lading.md) |
| 6.4 | Certificate of Origin (COO) | [certificate-of-origin.md](documents/certificate-of-origin.md) |
| 6.5 | Export Declaration / Shipping Bill | [export-declaration-shipping-bill.md](documents/export-declaration-shipping-bill.md) |
| 6.6 | Letter of Credit (LC) documents | [letter-of-credit.md](documents/letter-of-credit.md) |
| 6.7 | Bill of Exchange | [bill-of-exchange.md](documents/bill-of-exchange.md) |

## 7. Delivery, settlement & costing

| Step | Document | File |
|------|----------|------|
| 7.1 | Proof of Delivery (POD) | [proof-of-delivery.md](documents/proof-of-delivery.md) |
| 7.2 | Payment records (e.g., against LC or TT) | [payment-records.md](documents/payment-records.md) |
| 7.3 | Cost sheets / Landed Cost calculations (including freight, duty) | [cost-sheets-landed-cost.md](documents/cost-sheets-landed-cost.md) |

---

## Quick sequence (all steps)

1. Tech Packs / Spec Sheets  
2. Bill of Materials (BOM)  
3. Purchase Orders (POs)  
4. Goods Received Note (GRN)  
5. Inspection Reports / Quality Certificates  
6. Lab Test Reports / Compliance Certificates  
7. Manufacturing / Production Orders / Work Orders / Cut Tickets  
8. Stock Transfer / Issue Slips  
9. Inventory Adjustments / Cycle Count Reports  
10. Pick Lists / Packing Slips  
11. Packing List  
12. Shipping Marks / Carton Labels  
13. Advance Shipping Notice (ASN)  
14. Commercial Invoice  
15. Invoices (outgoing) and Debit/Credit Notes  
16. Bill of Lading (BOL)  
17. Certificate of Origin (COO)  
18. Export Declaration / Shipping Bill  
19. Letter of Credit (LC) documents  
20. Bill of Exchange  
21. Proof of Delivery (POD)  
22. Payment records  
23. Cost sheets / Landed Cost calculations  

---

## Sales order linkage

Outbound journey documents (pick lists, packing lists, commercial invoices, proof of delivery, payment records) can reference a confirmed sales order via `erp_documents.sale_id` → `sales.id`. Create the sales order in **Sales orders** (`/sales`), confirm it to release stock, then attach fulfillment and billing documents to the same `sale_id` for traceability.
