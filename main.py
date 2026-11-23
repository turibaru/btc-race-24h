import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "vendor"))

import makefun_bars

SYMBOL = "CBBTC"
M = 5
ENTRY_BPS = 20
TRAIL_BPS = 300
STOP_BPS = 200
COOLDOWN = 120
INSURANCE_BAR = 1320
MAX_SLIP_BPS = 300

closes = []
entry_close = None
peak = 0
cooldown_until = -1
insured = False
trades = 0


def on_batch(state, batch):
    global entry_close, peak, cooldown_until, insured, trades

    close = state.close(SYMBOL)
    if close is None:
        return []
    closes.append(close)
    if state.warming_up:
        return []

    holding = state.positions.get(SYMBOL)
    qty = holding.qty if holding is not None else 0

    if qty > 0 and entry_close is None:
        entry_close = close
        peak = close
    if qty > 0:
        peak = max(peak, close)

    if len(closes) < M + 1:
        return []

    ret5 = (close - closes[-M - 1]) * 10000 // closes[-M - 1]

    if qty == 0:
        if state.seq <= cooldown_until:
            return []
        if ret5 >= ENTRY_BPS:
            notional = min(state.cash, state.weight_room(SYMBOL))
            if notional <= 0:
                return []
            trades += 1
            return [{"side": "buy", "symbol": SYMBOL,
                     "notional_quote_units": notional,
                     "max_slippage_bps": MAX_SLIP_BPS}]
        if trades == 0 and state.seq >= INSURANCE_BAR and not insured:
            notional = min(state.cash, state.weight_room(SYMBOL))
            if notional <= 0:
                return []
            insured = True
            trades += 1
            return [{"side": "buy", "symbol": SYMBOL,
                     "notional_quote_units": notional,
                     "max_slippage_bps": MAX_SLIP_BPS}]
        return []

    trail_bps = (peak - close) * 10000 // peak
    ret_e = (close - entry_close) * 10000 // entry_close
    if trail_bps >= TRAIL_BPS or ret_e <= -STOP_BPS:
        cooldown_until = state.seq + COOLDOWN
        entry_close = None
        peak = 0
        return [{"side": "sell", "symbol": SYMBOL, "qty": qty,
                 "max_slippage_bps": MAX_SLIP_BPS}]
    return []


makefun_bars.run(on_batch)
