"""BTC Race 24h — trend-hold 120.

Strategi: gerbang return 120-bar + trailing stop lebar + cooldown +
entry asuransi akhir hari. Aritmetika INTEGER murni (tanpa float,
tanpa clock, tanpa environment, tanpa randomness) sehingga dua
eksekusi atas data yang sama menghasilkan order yang sama byte-for-byte.

Aturan (per batch, setelah apply_batch):
- warming_up -> [] (riwayat close tetap dicatat).
- riwayat < 121 bar -> [] (return 120-bar belum terdefinisi).
- tidak pegang posisi:
  - seq <= cooldown_until -> [].
  - ret_bps >= +50 -> BELI all-in.
  - tanpa sinyal, trades == 0, seq >= 1320, belum insured -> BELI asuransi.
- pegang posisi:
  - peak = max(peak, close).
  - ret_bps <= -150 ATAU drawdown dari peak >= 300 bps -> JUAL semua.
  - selain itu TAHAN.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

# Parameter TETAP (spec section 3).
LB = 120
ENTRY_BPS = 50
EXIT_BPS = -150
TRAIL_BPS = 300
COOLDOWN = 120
INSURANCE_BAR = 1320
MAX_SLIP_BPS = 300
SYMBOL = "CBBTC"

# Riwayat close CBBTC (semua bar yang diterima, termasuk warmup).
closes = []
# State strategi.
in_position = False
peak = 0
cooldown_until = -1
insured = False
trades = 0


def on_batch(state, batch):
    """Satu reply per batch: kembalikan list order (boleh kosong)."""
    global in_position, peak, cooldown_until, insured, trades

    close = state.close(SYMBOL)
    if close is None:
        # Belum ada bar CBBTC: tanpa order dan tanpa append.
        return []
    closes.append(close)

    # 1. Warmup: catat close, jangan kirim order.
    if state.warming_up:
        return []

    # 2. Return 120-bar belum terdefinisi sebelum 121 close.
    if len(closes) < LB + 1:
        return []
    # Return 120-bar dari CLOSE, aritmetika INTEGER persis (floor division).
    ret_bps = (close - closes[-LB - 1]) * 10000 // closes[-LB - 1]

    if not in_position:
        # 3a. Cooldown setelah exit: jangan masuk dulu.
        if state.seq <= cooldown_until:
            return []
        # 3b. Entry: return 120-bar >= +50 bps -> BELI all-in.
        if ret_bps >= ENTRY_BPS:
            notional = min(state.cash, state.weight_room(SYMBOL))
            if notional <= 0:
                return []
            in_position = True
            peak = close
            trades += 1
            return [{"side": "buy", "symbol": SYMBOL,
                     "notional_quote_units": notional,
                     "max_slippage_bps": MAX_SLIP_BPS}]
        # 3c. Entry asuransi: 0 trade seharian, bar >= 1320, belum insured
        # -> BELI all-in (guardrail balapan menuntut >= 1 trade).
        if trades == 0 and state.seq >= INSURANCE_BAR and not insured:
            notional = min(state.cash, state.weight_room(SYMBOL))
            if notional <= 0:
                return []
            insured = True
            in_position = True
            peak = close
            trades += 1
            return [{"side": "buy", "symbol": SYMBOL,
                     "notional_quote_units": notional,
                     "max_slippage_bps": MAX_SLIP_BPS}]
        return []

    # 4. Pegang posisi: perbarui peak, cek exit, selain itu TAHAN.
    peak = max(peak, close)
    # 4a. Exit: return 120-bar <= -150 bps ...
    # 4b. ... ATAU trailing drawdown dari peak >= 300 bps -> JUAL semua.
    trail_bps = (peak - close) * 10000 // peak
    if ret_bps <= EXIT_BPS or trail_bps >= TRAIL_BPS:
        holding = state.positions.get(SYMBOL)
        if holding is None or holding.qty <= 0:
            return []
        in_position = False
        cooldown_until = state.seq + COOLDOWN
        trades += 1
        return [{"side": "sell", "symbol": SYMBOL,
                 "qty": holding.qty,
                 "max_slippage_bps": MAX_SLIP_BPS}]
    # 4c. Tidak ada kondisi keluar -> TAHAN (jangan keluar-masuk di chop).
    return []


makefun_bars.run(on_batch)
