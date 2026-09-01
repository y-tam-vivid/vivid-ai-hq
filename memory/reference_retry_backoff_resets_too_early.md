---
name: reference_retry_backoff_resets_too_early
description: 再試行の間隔を「繋がった」でリセットすると、繋がった直後に拒否される障害では永久に最短間隔で叩き続ける。自分の速すぎる再接続が自分で拒否を作る
metadata:
  type: reference
---

**2026-09-02 06:29 実測（ロビン・毎朝の棚卸しで発見）。**
Slack Socket Mode の常駐が、**19秒間に9回**続けて接続と切断を繰り返した。

```
06:29:38  disconnect要求: warning              ← Slack側の定期的な張り直し（正常）
06:29:40  WebSocket接続完了 → too_many_websockets
06:29:42  WebSocket接続完了 → too_many_websockets
     …（同じ形で計8回）…
06:29:57  WebSocket接続完了 → 接続確立（hello受信）   ← 9回目でようやく収束
```

**★9行すべてが「1秒後に再接続」。指数バックオフは一度も効いていない。**

## なぜ効かなかったか（`slack_socket.py:664-708` 実測）

```python
url = open_connection()
ws  = WSClient(url)
log('WebSocket接続完了')
backoff = 1            # ★ここでリセットしている
state.connected = True
while True:
    msg = ws.recv()    # ← 実際に使えるかどうかは、この先で分かる
```

**リセットの位置が「ソケットが開いた時点」で、「安定して通信できた時点」ではない。**
Slack は**開かせてから**`too_many_websockets` で切る。したがって毎回
`backoff = 1` を通ってから落ちる ＝ **1秒間隔の無限ループになりうる。**

そして原因は Slack ではなくこちら側 ── **1秒で張り直すので、
Slack から見ると古いソケットがまだ生きている。**
`too_many_websockets` は**自分の速すぎる再接続が自分で作った拒否**。
今回19秒で抜けたのは運で、収束を保証する仕組みは無い。

## 型として（Slackに限らない）

- **★バックオフのリセットは「接続できた」ではなく「一定時間、正常に使えた」で行う。**
  接続直後に拒否される障害は、この1行の位置だけで無限リトライになる。
  目安：最初のメッセージを1件受け取る／`hello` 相当を受ける／N秒生存する、のどれか。
- **★リトライが速いこと自体が障害の原因になりうる。** 相手側が資源（接続数・レート）を
  数えている場合、こちらの善意の即時再試行が上限に当たる。
  **失敗の原因を相手のせいにする前に、自分の間隔を見る。**
- **★「1秒後に再接続」が連続で並んでいたら、バックオフは壊れている。**
  正しく効いていれば 1→2→4→8… と**ログの数字が増える**。
  同じ数字が並ぶログは、それ自体が症状。
- **上限（`min(backoff*2, 300)`）があっても意味がない。** 到達する前にリセットされる。
  上限の有無ではなく**リセット条件**を読むこと。

## 見つけ方

```
grep '秒後に再接続' <log> | tail -20     ★数字が単調増加しているか目で見る
                                        同じ数字が3つ以上並べば黒
```

**★ここは「切れた回数」を数えても分からない。** 切れること自体は正常
（[[reference_slack_tokens_and_socket_mode]]「disconnect は異常ではない」）。
異常なのは**間隔が伸びないこと**。件数ではなく間隔の列を見る。

## いま直っていない

`~/.vivid-relay/slack_socket.py` は git 管理外（[[reference_fix_where_git_reaches]]）。
**★担当＝ピタゴラス（コード変更）。** 直すのは `backoff = 1` の1行の位置だけ
（`WSClient` 直後から、最初の `recv()` 成功後へ移す）。
検査はステラ（[[cross-check]] 型・作った本人は検査しない）。

関連 [[reference_ran_is_not_succeeded]]（down_since は再試行ごとにリセットしない・同じ根）
[[reference_heartbeat_proves_life_not_results]] [[reference_a_warning_nobody_owns]]
