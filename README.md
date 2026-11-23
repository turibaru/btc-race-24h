# BTC Race 24h — trend-hold 120

[![make.fun](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/c/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/turibaru/btc-race-24h/rank.svg)](https://make.fun/c/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/turibaru/btc-race-24h/reward.svg)](https://make.fun/c/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

Owner: turibaru — wallet 7sVBY4mXtDdPNcBdfnoGysT5FRKv1YRmQz6UR9eSt7rF

## Strategi

Bot "trend-hold 120" untuk cbBTC (CBBTC) ini masuk sekali saat tren terkonfirmasi — return 120-bar dari close mencapai +50 bps — lalu menahan posisi melewati chop datar, dan keluar hanya saat pembalikan besar: return 120-bar turun ke −150 bps atau trailing drawdown dari peak mencapai 300 bps. Setelah keluar, bot cooldown 120 bar sebelum boleh masuk lagi, dan bila sampai bar ke-1320 belum ada satu pun trade, bot mengambil entry asuransi all-in agar memenuhi guardrail minimal satu trade di balapan. Semua hitungan memakai aritmetika integer murni (tanpa float, tanpa clock, tanpa randomness), sehingga hasilnya deterministik byte-for-byte.

Hasil replay jendela dev (1.440 bar, 22–23 Nov 2026): net PnL **+$31,17** dengan 1 trade dan max drawdown 1,98% — di atas gate dev $0 dengan margin besar.

Kompetisi: [Race a BTC trading bot live for 24 hours — make.fun](https://make.fun/c/btc-race-24h-20261123-0511)
