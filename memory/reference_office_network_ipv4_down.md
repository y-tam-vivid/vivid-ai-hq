---
name: reference_office_network_ipv4_down
description: 「一部のサイトだけ開かない」はルーターのIPv4側断の型。IPv6で届くサイト(Zoom/Google/Notion)だけ動く。2026-10-01 MacBookの居る192.168.0.x網で実測
metadata:
  type: reference
---

**症状**：Zoom・Google・Notion は開くのに、GitHub など多くが開かない。Wi-Fiでも有線でも同じ。
スマホもWi-Fiを切る（＝モバイル回線へ逃がす）と動く。

**実測（2026-10-01・MacBook／ルーター 192.168.0.1）**
- ルーターまで：ping・TCP80 とも通る（LAN内は正常）
- IPv4で外へ：8.8.8.8/1.1.1.1 への ping 0%・`curl -4` 全滅・traceroute は1ホップ目から無応答
- IPv6で外へ：`curl -6 google` 200・IPv6のDNS(ルーター/Google)は正常応答
- → **IPv6を持つサイトだけ開き、IPv4しか無いサイト(github.com 等)が落ちる**
- Wi-Fi(en0)・有線(en5) 両方で同じ ＝ MacBook の問題ではなく**ルーター/回線のIPv4側**
- Tailscale を切っても変化なし（無実を確認済み）。SYNC_STATUS の github 22番タイムアウトも同じ原因

**切り分けコマンド**：`curl -4 -m 8 https://www.google.com` と `curl -6 ...` を並べる。
v6だけ通ればルーター側。

**直し方（人の手）**：ONU→ルーターの順に電源を抜き、1分置いてONU→ルーターの順に入れる。
直らなければ回線事業者のIPv4（IPv4 over IPv6/PPPoE）障害を確認。

**経過（2026-10-01）**：ONU→ルーター再起動では直らず（再起動直後もIPv4全滅・IPv6は200）。
★ルーターの時計が 2024-08-14 のまま（HTTPのDate）＝外の時刻サーバーへIPv4で届いていない傍証。

**注意**：`ssh mini` は Tailscale 経由（mini は同じLANに居ない）。mini が動く＝この網は無関係。
