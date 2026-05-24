export type TmsFieldType =
  | "text"
  | "number"
  | "date"
  | "datetime-local"
  | "textarea"
  | "select"
  | "checkbox"

export type TmsFieldDef = {
  path: string
  label: string
  type?: TmsFieldType
  placeholder?: string
  options?: { value: string; label: string }[]
  colSpan?: 1 | 2
}

export type TmsTabDef = {
  id: string
  title: string
  description?: string
  fields?: TmsFieldDef[]
  isLineItems?: boolean
}

const emptyOption = { value: "", label: "—" }

export const TMS_SHIPMENT_TYPES = [
  "OUTBOUND",
  "INBOUND",
  "PARCEL",
  "LTL",
  "TRUCKLOAD",
  "INTERMODAL",
] as const

export const TMS_SERVICE_LEVELS = [
  "STANDARD",
  "EXPEDITED",
  "ECONOMY",
  "OVERNIGHT",
  "SAME_DAY",
] as const

export const TMS_TRANSPORT_MODES = ["ROAD", "AIR", "OCEAN", "PARCEL", "RAIL"] as const

export const TMS_STATUS_OPTIONS = [
  "PLANNED",
  "TENDERED",
  "IN_TRANSIT",
  "DELIVERED",
  "EXCEPTION",
  "CANCELLED",
] as const

export const TMS_PACKAGING_TYPES = ["CARTON", "PALLET", "CRATE", "DRUM", "BAG", "LOOSE"] as const

export const TMS_PAYMENT_STATUSES = ["UNPAID", "PENDING", "PAID", "DISPUTED"] as const

const shipmentTypeOptions = [
  emptyOption,
  ...TMS_SHIPMENT_TYPES.map((v) => ({
    value: v,
    label: v.charAt(0) + v.slice(1).toLowerCase().replace("_", " "),
  })),
]

const serviceLevelOptions = [
  emptyOption,
  ...TMS_SERVICE_LEVELS.map((v) => ({
    value: v,
    label: v.charAt(0) + v.slice(1).toLowerCase(),
  })),
]

const transportModeOptions = [
  emptyOption,
  ...TMS_TRANSPORT_MODES.map((v) => ({
    value: v,
    label: v.charAt(0) + v.slice(1).toLowerCase(),
  })),
]

const statusOptions = TMS_STATUS_OPTIONS.map((v) => ({
  value: v,
  label: v
    .split("_")
    .map((w) => w.charAt(0) + w.slice(1).toLowerCase())
    .join(" "),
}))

const packagingOptions = [
  emptyOption,
  ...TMS_PACKAGING_TYPES.map((v) => ({
    value: v,
    label: v.charAt(0) + v.slice(1).toLowerCase(),
  })),
]

const paymentStatusOptions = [
  emptyOption,
  ...TMS_PAYMENT_STATUSES.map((v) => ({
    value: v,
    label: v.charAt(0) + v.slice(1).toLowerCase(),
  })),
]

const hazmatOptions = [
  emptyOption,
  { value: "NO", label: "No" },
  { value: "YES", label: "Yes" },
]

const basicFields: TmsFieldDef[] = [
  { path: "reference", label: "Record reference" },
  { path: "title", label: "Title / summary", colSpan: 2 },
  { path: "basic.shipment_id", label: "Shipment ID / number" },
  { path: "basic.order_reference", label: "Order reference (ERP sales order)" },
  {
    path: "basic.shipment_type",
    label: "Shipment type",
    type: "select",
    options: shipmentTypeOptions,
  },
  { path: "basic.shipment_date", label: "Shipment date / ship by date", type: "date" },
  {
    path: "basic.requested_delivery_date",
    label: "Requested delivery date",
    type: "date",
  },
  {
    path: "basic.service_level",
    label: "Service level",
    type: "select",
    options: serviceLevelOptions,
  },
  {
    path: "basic.transport_mode",
    label: "Mode of transport",
    type: "select",
    options: transportModeOptions,
  },
  { path: "status", label: "Status", type: "select", options: statusOptions },
  { path: "description", label: "Description / notes", type: "textarea", colSpan: 2 },
]

const shipperFields: TmsFieldDef[] = [
  { path: "shipper.warehouse_code", label: "Ship from location / warehouse code" },
  { path: "shipper.street", label: "Street", colSpan: 2 },
  { path: "shipper.city", label: "City" },
  { path: "shipper.state", label: "State / province" },
  { path: "shipper.zip", label: "Zip / postal code" },
  { path: "shipper.country", label: "Country" },
  { path: "shipper.contact_name", label: "Contact name (shipper)" },
  { path: "shipper.contact_phone", label: "Contact phone (shipper)" },
  { path: "shipper.loading_appointment", label: "Loading appointment", type: "date" },
  { path: "shipper.loading_time_window", label: "Loading time window" },
]

const consigneeFields: TmsFieldDef[] = [
  { path: "consignee.ship_to_location", label: "Ship to / customer location", colSpan: 2 },
  { path: "consignee.street", label: "Street", colSpan: 2 },
  { path: "consignee.city", label: "City" },
  { path: "consignee.state", label: "State / province" },
  { path: "consignee.zip", label: "Zip / postal code" },
  { path: "consignee.country", label: "Country" },
  { path: "consignee.contact_name", label: "Contact name (consignee)" },
  { path: "consignee.contact_phone", label: "Contact phone (consignee)" },
  { path: "consignee.delivery_appointment", label: "Delivery appointment", type: "date" },
  { path: "consignee.delivery_time_window", label: "Delivery time window" },
]

export const tmsLineItemFields: TmsFieldDef[] = [
  { path: "item_number", label: "Item number / SKU" },
  { path: "item_description", label: "Item description", colSpan: 2 },
  { path: "quantity", label: "Quantity", type: "number" },
  { path: "weight_per_unit", label: "Weight per unit", type: "number" },
  { path: "weight_total", label: "Weight total", type: "number" },
  { path: "length", label: "Length", type: "number" },
  { path: "width", label: "Width", type: "number" },
  { path: "height", label: "Height", type: "number" },
  { path: "volume", label: "Volume", type: "number" },
  {
    path: "packaging_type",
    label: "Packaging type",
    type: "select",
    options: packagingOptions,
  },
  {
    path: "hazardous_material",
    label: "Hazardous material",
    type: "select",
    options: hazmatOptions,
  },
]

const carrierFields: TmsFieldDef[] = [
  { path: "carrier.carrier_name", label: "Carrier name" },
  { path: "carrier.carrier_code", label: "Carrier code" },
  { path: "carrier.carrier_service", label: "Carrier service / method" },
  { path: "carrier.quoted_rate", label: "Quoted / negotiated rate", type: "number" },
  { path: "carrier.freight_cost", label: "Freight cost", type: "number" },
  {
    path: "carrier.accessorial_charges",
    label: "Accessorial charges (fuel, liftgate, residential, etc.)",
    type: "textarea",
    colSpan: 2,
  },
  { path: "carrier.tracking_number", label: "Tracking number (PRO, AWB, etc.)" },
]

const complianceFields: TmsFieldDef[] = [
  { path: "compliance.bol_number", label: "Bill of lading (BOL) number" },
  {
    path: "compliance.customs_compliance_data",
    label: "Customs / trade compliance data",
    type: "textarea",
    colSpan: 2,
  },
  { path: "compliance.insurance_value", label: "Insurance value", type: "number" },
  {
    path: "compliance.special_instructions",
    label: "Special instructions / notes",
    type: "textarea",
    colSpan: 2,
  },
  {
    path: "compliance.label_requirements",
    label: "Label requirements (carrier-specific)",
    type: "textarea",
    colSpan: 2,
  },
]

const trackingFields: TmsFieldDef[] = [
  { path: "tracking.current_status", label: "Current status" },
  { path: "tracking.eta", label: "ETA (estimated time of arrival)", type: "datetime-local" },
  {
    path: "tracking.actual_pickup_datetime",
    label: "Actual pickup date/time",
    type: "datetime-local",
  },
  {
    path: "tracking.actual_delivery_datetime",
    label: "Actual delivery date/time",
    type: "datetime-local",
  },
  { path: "tracking.pod_reference", label: "Proof of delivery (POD) reference" },
  {
    path: "tracking.exception_reason",
    label: "Exception reason (if any)",
    type: "textarea",
    colSpan: 2,
  },
]

const financialFields: TmsFieldDef[] = [
  { path: "financial.freight_bill_amount", label: "Freight bill amount", type: "number" },
  { path: "financial.carrier_invoice_number", label: "Invoice number (from carrier)" },
  {
    path: "financial.payment_status",
    label: "Payment status",
    type: "select",
    options: paymentStatusOptions,
  },
  { path: "financial.cost_center", label: "Cost center / department code" },
  {
    path: "financial.custom_fields",
    label: "User-defined / custom fields",
    type: "textarea",
    colSpan: 2,
  },
]

export const TMS_FORM_TABS: TmsTabDef[] = [
  {
    id: "basic",
    title: "Basic Information",
    description: "Shipment header and lifecycle status.",
    fields: basicFields,
  },
  {
    id: "shipper",
    title: "Shipper / Origin",
    description: "Ship-from location, address, and loading window.",
    fields: shipperFields,
  },
  {
    id: "consignee",
    title: "Consignee / Destination",
    description: "Ship-to location, address, and delivery window.",
    fields: consigneeFields,
  },
  {
    id: "line_items",
    title: "Line Items",
    description: "SKU, quantity, weight, dimensions, and packaging.",
    isLineItems: true,
  },
  {
    id: "carrier",
    title: "Carrier & Rating",
    description: "Carrier, rates, accessorials, and tracking.",
    fields: carrierFields,
  },
  {
    id: "compliance",
    title: "Compliance & Docs",
    description: "BOL, customs, insurance, and label requirements.",
    fields: complianceFields,
  },
  {
    id: "tracking",
    title: "Tracking & Execution",
    description: "ETA, actual pickup/delivery, POD, and exceptions.",
    fields: trackingFields,
  },
  {
    id: "financial",
    title: "Financial / Audit",
    description: "Freight bill, invoice, payment, and cost center.",
    fields: financialFields,
  },
]

export const TMS_PHASE1_FEATURES = new Set(["shipments"])

export const TMS_LINKED_ROUTES = ["/sales", "/warehouse", "/customers", "/inventory"] as const
