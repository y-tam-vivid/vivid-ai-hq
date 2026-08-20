---
name: reference_two_sessions_built_the_same_thing
description: 別マシンのセッションへは SendMessage が届かない。二重実装を救うのは冪等性。着手宣言が最後の防波堤
metadata:
  node_type: memory
  type: reference
---

**別のマシンで動いているセッションとは、直接やり取りできない。** `ListAgents` に出るのは
**同じマシンのセッションだけ**で、`SendMessage` もそこへしか届かない。
相手が動いていることは `ssh <機械> 'ls /tmp/cc-socks/'` で分かるが、**話しかける手段は無い。**

**Why:** 2026-08-20、MacBook と Mac mini が **同じ「00_企業マスタ → Notion🏢顧客DB の upsert」を
別々に実装した。** どちらも着手宣言を先に書いていなかった。

```
00:09  MacBook  upsert を実行  382件 → 486件（補完309・新規104）
02:42  mini     notion_customer_upsert.py を本実行  → 更新0・新規0
                （＝MacBookが先に書き終えていたので、書くものが無かった）
```

**実害はゼロだった。冪等に作ってあったから助かっただけで、設計で防いだのではない。**
片方が「全部消してから作り直す」型だったら、もう片方の結果は消えていた。

**How to apply:**

```
連携の経路（上から順に試す。★1つで足りると思わない）
  ① WORKING.md へ着手宣言 → commit      正規の経路。ただし相手が pull 停止中だと届かない
  ② 相手のローカルへ直接ファイルを置く    確実。~/.vivid-relay/HANDOFF_*.md など
  ③ Notion（⑥／③）                     両者が見る場所。非同期でよいならここ
  ✕ SendMessage                        ★別マシンには届かない
```

- **相手が `git pull` 停止中なら ①も届かない。** 未コミットがあると ff-only が止まるため。
  こういうときは②を使う。**「commit したから伝わったはず」は成立しない。**
- **書くものは冪等に作る。** 2回走っても壊れないなら、二重実装は事故にならず「無駄」で済む。
  `update` は空欄補完のみ、`create` は突合してから、`clear`→`rebuild` は避ける。
- **着手宣言は「相手のため」ではなく「自分が後で誤解しないため」でもある。**
  2026-08-20 は両セッションとも宣言なしで走り、あとから WORKING.md を見て初めて
  同じものを作っていたと分かった。
- 機械側の補強 → `bin/vivid-sync.sh` が未コミットのファイル名を `SYNC_STATUS.md` へ書き出す
  （宣言を忘れても、触っている実態は見える）。関連 → [[reference_silent_sync_failure]]
