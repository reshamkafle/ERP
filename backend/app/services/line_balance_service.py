"""Line balancing: takt time calculation and greedy station assignment."""

from decimal import Decimal

from app.models.garment_planning import LineBalanceAssignment, LineBalanceSession
from app.schemas.garment_planning import (
    LineBalanceAssignmentRead,
    LineBalanceCalculateIn,
    LineBalanceCalculateResult,
    LineBalanceOperationIn,
    LineBalanceStationLoad,
)


def _effective_smv(op: LineBalanceOperationIn) -> Decimal:
    return op.smv_minutes


def calculate_line_balance(payload: LineBalanceCalculateIn) -> LineBalanceCalculateResult:
    """Greedy largest-first assignment to minimize station load imbalance."""
    ops = sorted(payload.operations, key=lambda o: _effective_smv(o), reverse=True)
    n_stations = payload.operators_count
    if n_stations < 1:
        n_stations = 1

    target_qty = payload.target_quantity
    if target_qty <= 0:
        target_qty = Decimal("1")

    takt = payload.available_minutes / target_qty

    station_loads: list[Decimal] = [Decimal("0")] * n_stations
    assignments: list[LineBalanceAssignmentRead] = []

    for op in ops:
        smv = _effective_smv(op)
        min_idx = min(range(n_stations), key=lambda i: station_loads[i])
        station_loads[min_idx] += smv
        assignments.append(
            LineBalanceAssignmentRead(
                id=0,
                session_id=0,
                routing_operation_id=op.routing_operation_id,
                operation_definition_id=op.operation_definition_id,
                operation_name=op.operation_name,
                station_no=min_idx + 1,
                assigned_smv=smv,
                operator_ref=None,
            ),
        )

    max_load = max(station_loads) if station_loads else Decimal("0")
    total_smv = sum(station_loads)
    bottleneck = station_loads.index(max_load) + 1 if station_loads else 1

    if total_smv > 0 and max_load > 0:
        efficiency = (total_smv / (max_load * n_stations)) * Decimal("100")
    else:
        efficiency = Decimal("100")

    loads_out: list[LineBalanceStationLoad] = []
    for i, load in enumerate(station_loads):
        util = (load / takt * Decimal("100")) if takt > 0 else Decimal("0")
        loads_out.append(
            LineBalanceStationLoad(station_no=i + 1, total_smv=load, utilization_pct=util.quantize(Decimal("0.01"))),
        )

    return LineBalanceCalculateResult(
        calculated_takt_minutes=takt.quantize(Decimal("0.0001")),
        line_efficiency_pct=efficiency.quantize(Decimal("0.01")),
        bottleneck_station=bottleneck,
        assignments=assignments,
        station_loads=loads_out,
    )


def build_session_from_calculate(
    payload: LineBalanceCalculateIn,
    *,
    production_plan_id: int | None,
    production_order_id: int | None,
    sewing_line_id: int | None,
    target_output_per_hour: Decimal,
) -> tuple[LineBalanceSession, list[LineBalanceAssignment]]:
    result = calculate_line_balance(payload)
    session = LineBalanceSession(
        production_plan_id=production_plan_id,
        production_order_id=production_order_id,
        sewing_line_id=sewing_line_id,
        target_output_per_hour=target_output_per_hour,
        available_minutes=payload.available_minutes,
        target_quantity=payload.target_quantity,
        operators_count=payload.operators_count,
        calculated_takt_minutes=result.calculated_takt_minutes,
        line_efficiency_pct=result.line_efficiency_pct,
        bottleneck_station=result.bottleneck_station,
    )
    assignments = [
        LineBalanceAssignment(
            routing_operation_id=a.routing_operation_id,
            operation_definition_id=a.operation_definition_id,
            operation_name=a.operation_name,
            station_no=a.station_no,
            assigned_smv=a.assigned_smv,
            operator_ref=a.operator_ref,
        )
        for a in result.assignments
    ]
    return session, assignments


def recalc_session_metrics(session: LineBalanceSession) -> None:
    """Recompute efficiency after manual assignment overrides."""
    if not session.assignments:
        return
    n_stations = session.operators_count or 1
    station_loads: dict[int, Decimal] = {i: Decimal("0") for i in range(1, n_stations + 1)}
    for a in session.assignments:
        st = min(max(a.station_no, 1), n_stations)
        station_loads[st] = station_loads.get(st, Decimal("0")) + a.assigned_smv

    max_load = max(station_loads.values()) if station_loads else Decimal("0")
    total_smv = sum(station_loads.values())
    session.bottleneck_station = max(station_loads, key=lambda k: station_loads[k]) if station_loads else 1

    if total_smv > 0 and max_load > 0:
        session.line_efficiency_pct = (total_smv / (max_load * n_stations)) * Decimal("100")
    else:
        session.line_efficiency_pct = Decimal("100")

    if session.target_quantity and session.target_quantity > 0:
        session.calculated_takt_minutes = session.available_minutes / session.target_quantity
