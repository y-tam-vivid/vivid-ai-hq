---
name: reference_make_it_impossible_not_detectable
description: 検出の精度を上げるのでなく、検出しなくて済む構造にする。1975年に「ブラックリストは原理的に不完全」と結論が出ている
metadata:
  type: reference
---

**★「捕まえられない」の答えは、外に既にあった。**（2026-08-29 クローバー博士が一次資料まで調査）
有璽氏「捕まえられないじゃなくて、どういう設計にしたらそれが回避できるのか」。

## 共通する答え ── 検出をやめて、不可能にする

```
いまやっていること   Bashコマンドを正規表現で解析し、危ないものを検出して止める
                     ＝ ブラックリスト方式（悪いものを列挙して弾く）
1975年の結論         ★これは原理的に不完全。Saltzer & Schroeder が名指しで否定している
                     "fail-safe defaults" ── アクセス判定は排除でなく**許可を基準にする**

  Saltzer, J.H. & Schroeder, M.D. (1975) "The Protection of Information in
  Computer Systems." Proceedings of the IEEE, 63(9), 1278-1308.
  http://web.mit.edu/Saltzer/www/publications/protection/
```

**シェル構文の完全解析は停止性問題の一種で、恒久的にすり抜けが残る。**
だから解析を諦め、**レイヤーを下げる**。

```
★具体の解（今すぐ実装できる形）
  ① 規範ファイル配下（.claude/skills/ 等）を、AIが実行するOSユーザーの
     書き込み権限から外形的に外す（ディレクトリを read-only にする）
     → python3 -c "open().write()" だろうと echo >> だろうと、
       どの経路で来ても OS カーネルが弾く。★検出ロジックを一切経由しない
  ② Bash 経由のファイル書き込みそのものを禁止し、
     Write/Edit ツールだけを書き込み経路として許可する
     （Claude Code 公式の permissions がこの形。deny に書き込み系の Bash を入れる）

★この操作自体を AI に与えてはいけない（クローバーの懸念）。人が1回設定する。
```

## 「申告」と「検出」の限界は、実証で数字が出ている

```
Anthropic 自身が公表   Claude Code auto mode の検出型ガードレール ★偽陰性率 17%
                       「慎重な人間レビューの完全な代替ではない」と明記
                       anthropic.com/engineering/claude-code-auto-mode

hearback problem       航空管制。復唱があっても誤りを検出できない。
（航空）                 「聞くべきものを聞いた」という期待バイアスで誤復唱を見逃す
                       ★沈黙・無反応は「確認できた」の証拠にならない
                       DOT/FAA/AR-98/17

WHO手術安全チェックリスト  オンタリオ州101病院の前向き研究。自己申告の遵守率90%超でも
（医療）                 死亡率・合併症とも有意差なし（p=0.13 / p=0.29）
                       ★「使った」という申告と「機能した」は別物
                       Urbach et al. (2014) NEJM 370, 1029-1038
```

**★「解消11件」の申告を突合したら7件だった**（[[feedback_never_write_an_unmeasured_number]]）は、
この外部研究が予告していた現象そのもの。**申告と実測は必ず分離して比較する。**

## 検査役の独立性 ── いまの cross-check は半分しか満たしていない

```
NASA IV&V   「技術的・管理的・財務的に独立した組織」が検証しなければならない
            （1986年チャレンジャー号事故後に制度化）
            ★いまの cross-check は**技術的独立性だけ**。同じ設計思想・同じ盲点を共有している

bias blind spot  人は自分より他人の方が偏見に影響されやすいと系統的に錯覚する。
                 ★仕組みを説明された後でも「自分の判断は客観的だ」と言い続ける
                 Pronin, Lin & Ross (2002) PSPB 28(3), 369-381
```

**打ち手（社内で足す層）**
- 検査役が**何を見逃したか**を定期棚卸しする層を1枚足す（IIA の外部評価型）
- 検査役だけは「同じ型で並べる」の例外とし、**意図的に異なる型で複数走らせる**（fresh eyes）
- 検査役は設計意図・ドキュメントを事前に読まず、**実データと実出力だけで判定**する

## ★分からなかったこと（正直に）

「検査を作った本人が、自分の想定した欠陥しか検出できない」に**直接効く外部知見は無かった**。
NASA IV&V と fresh eyes が最も近いが、既にやっている型の補強であって新しい解ではない。
**LLMエージェント特有の「検査コード自体に死角を埋め込む」問題は、学術的に未確立の分野。**

## 適用しないと判断したもの

```
監査法人の強制ローテーション   実証研究128本のレビューで単一の結論が出ていない
two-person rule               Germanwings後に導入され、複数の航空会社が撤回。
                              1人退出→もう1人入室の間にドアが開く時間が延びた
                              ＝★単純な多重化は別のリスクを生む
eBPF / gVisor のフル導入       研究段階・今回には過剰。設計思想だけ転用する
```

## Normalization of Deviance ── いま社内で起きている可能性

逸脱が即座に破局を招かない限り、組織はそれを「正常」として受け入れていく
（Vaughan, D. (1996) *The Challenger Launch Decision*）。
**★確認手続きは導入した瞬間ではなく、運用が続く中で骨抜きになる。**
社内では「規範文書が長大化して読まれなくなる」という形で既に進行している
（[[reference_delivered_but_unread]]）。


## ★★作る必要が無かった。Claude Code 本体に既にある（2026-08-29 クローバー E調査）

**OSカーネルレベルで書き込みを拒否する機能が、公式に実装済みだった。**
私たちは同じものを正規表現で自作していた。

```json
settings.json
{"sandbox": {"enabled": true, "filesystem": {
  "denyWrite": ["~/.claude/settings.json"],
  "denyRead":  ["~/.claude/credentials.json"]
}}}
```

macOS は Seatbelt、Linux は seccomp を使う。**`python3 -c "open().write()"` だろうと
`echo >>` だろうと、どの経路で来ても OS が弾く。** settings.json 自体への書き込みも
全スコープで既定拒否（＝自分でポリシーを緩められない設計）。
出典: https://code.claude.com/docs/en/sandboxing

```
★既知バグ（2026年時点・採用前に実測が要る）
  相対パスは無効化され絶対パスのみ有効          Issue #50454
  denyWrite 配下で denyRead がすり抜ける         Issue #53209
★注意   広い deny は、その中の狭い allow の例外を無効化する
        ＝ ホワイトリストとブラックリストを混ぜると事故る（実務記事群で共通の注記）
```

### ★ここから引く教訓

**「無い」と判断する前に、公式ドキュメントを見る。**
[[feedback_use_the_team_not_alone]] の「①スキル ②bin/ ③pip ④過去実績の grep で数える」に
**⑤公式ドキュメント**を足す。**自作した検問は、公式機能の劣化版だった。**

## ★慢性化した警告 ── Google SRE の答え（F調査）

```
Google SRE Workbook  multiwindow, multi-burn-rate alerting
                     短期・長期の2ウィンドウで消費速度を見て、
                     ★「ページ（即時対応）」と「チケット（翌営業日）」を機械的に分ける
                     https://sre.google/workbook/alerting-on-slos/  （一次資料で確認）

alert fatigue の根本原因（実務解説）  ①重要度が階層化されていない（全部同列）
                                      ②棚卸しの不在
```

**★社内の「慢性化した赤が3日で背景に溶ける」は、重要度階層の不在型。**
即対応と週次棚卸しを**別チャネルへ機械的に分離**し、後者は人を呼ばない代わりに
定期棚卸しへ強制的に載せる。

## ★パスを2箇所に書いた問題 ── docs as code の答え

「動いている検問を『動いていない』と言い続けた」のは典型的な **documentation drift**。
**解はドキュメント側を直す努力ではなく、正本を1箇所に強制し、CIで乖離を機械的に検出する構造。**

関連: [[reference_norms_outnumber_their_enforcement]] [[reference_heartbeat_proves_life_not_results]]
[[feedback_never_write_an_unmeasured_number]] [[feedback_use_the_team_not_alone]]
