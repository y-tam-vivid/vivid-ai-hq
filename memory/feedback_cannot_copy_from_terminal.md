---
name: feedback_cannot_copy_from_terminal
description: Mac miniのターミナル画面からはコピーできない。チャットにコードやURLを出しても渡したことにならない
metadata:
  node_type: memory
  type: feedback
---

**Mac mini のターミナル（このチャット画面）からは、テキストをコピーできない。**

> 「二度と言わせるなよ。Mac miniはコピペできないっつってんねん。
>   だからここにコード貼っても俺は触れないんだよ。コピーできないんだよ。
>   これほんま何回も言ってるから、二度と言わせん」（2026-08-20 有璽氏）

**Why:** 有璽氏は MacBook で作業しており、mini のターミナル出力は「見えるが触れない」。
SSH越しだと Terminal.app のクリップボード（OSC52）も効かない
（→ [[project_macmini_remote_workhorse]]）。
**チャットに出した時点で「渡した」と思い込むのが誤り。** 見せただけ。

## How to apply ── 渡し方は3つだけ

```
✗  チャットにコードを貼る                触れない。渡していない
✗  チャットに長いURLを貼る                同上
✗  「◯◯の画面を開いて…を探して」        押す場所が特定できていない

✓  Slack DM へ送る                      MacBookのSlackからタップ・コピーできる
✓  Drive / Notion に置いてリンクを渡す    リンクはSlack経由でタップできる
✓  ★そもそも人の手を要らなくする          いちばん良い。下記
```

### ★最善は「渡さない」

人に何かを貼らせる時点で設計が負けている。自動で届く経路を先に探す。

| やりたいこと | 人に貼らせる（✗） | 自動で届く（✓） |
|---|---|---|
| 他機へフックを入れる | 「この1行を貼って」 | `bin/vivid-sync.sh` が15分ごとに走るので、そこで自動導入する |
| 他機へ設定を配る | 手順書を渡す | git に入れて `setup` を同期処理から呼ぶ |
| 他セッションへ申し送り | 「伝えておいて」 | `WORKING.md` に書く（毎ターン全機へ届く） |

## 同じ日に3回踏んだ（2026-08-20）

```
① Google Cloud の App Home 設定    「Messages Tabを探して」と文字で言った
                                    → 直リンクは bots.info で取れたのに調べなかった
② OAuth の認証URL                  チャットに長いURLを貼った
                                    → Drive/Notionに置き直した
③ setup_hooks.sh の実行            「この1行を貼ってください」とチャットに出した
                                    → ★フックが「コピーできない」と目の前に出していたのに踏んだ
```

**③が最悪。** PreToolUse フックが `hook_inject_memory.py` から
「有璽氏はチャット内のテキストをコピーできない。渡すものはクリックできるリンクにする」
と実際に表示していた。**見えていたのに適用しなかった。**

→ 出すだけでは足りない。**渡す手段そのものを自動化する**（上の表）。

関連 [[feedback_verify_before_declining]] [[reference_hooks_enforce_what_discipline_cannot]]
[[project_macmini_remote_workhorse]]
