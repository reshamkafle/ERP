# Goods Received Note (GRN)

## Fabric rolls at receipt

For roll-tracked raw materials (`roll_tracking_enabled` on the product):

1. Confirm the purchase order as usual.
2. Use **Fabric rolls → Receive roll** or `POST /v1/material-rolls/purchase-receive` to register each physical roll with length (meters/yards), dye lot, and warehouse location.
3. Print labels from the roll detail panel or `GET /v1/material-rolls/{id}/label/print`.

See [fabric-roll-lot-tracking.md](../fabric-roll-lot-tracking.md) for full field and API reference.
