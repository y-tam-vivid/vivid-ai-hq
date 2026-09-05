---
name: reference_detect_noninteractive_session
description: フックの中で「対話セッションか claude -p か」を見分ける唯一の手段は CLAUDE_CODE_ENTRYPOINT。agent_id・isatty・CHILD_SESSION は全部使えない（実測）
metadata:
  type: reference
---

**`claude -p` は人に問い返せない。** そこで `AskUserQuestion` を出すと、
**誰も押せない画面で無言のまま止まり続ける。**
止めるには、フックの中で「いま対話セッションか非対話か」を判定できないといけない。

## ★答え ── 環境変数 `CLAUDE_CODE_ENTRYPOINT` の1本だけ（2026-09-05 実測）

```
CLAUDE_CODE_ENTRYPOINT == 'cli'      → 対話（端末のTUI）。★人が居る。止めてはいけない
CLAUDE_CODE_ENTRYPOINT == 'sdk-cli'  → 非対話（claude -p）。★人が居ない
                          'sdk-ts' / 'sdk-py' → 同じく非対話（SDK経由）
無い / 上記以外                       → ★判定不能。通す（fail-open）
```

**★フックの子プロセスへ環境変数は継承される。**だからフックから読める（実測）。

### 3経路で確かめた

```
経路1  claude 実体(199MB)の該当関数
       ENTRYPOINT = 非対話 ? "sdk-cli" : "cli"
       呼び出し元 O = interactivity.kind === "non-interactive" || wir(argv)
       ＝★Claude Code 自身の「非対話か」の判定そのものが、この文字列に出ている
経路2  実機A/B  claude -p のフックが見た値 = 'sdk-cli'
                pty上で起こした対話TUIのフックが見た値 = 'cli'
経路3  母集団   mini の transcript 25,261 assistant行の entrypoint 欄
                cli 18,538 ／ sdk-cli 6,723。★欠測・第3の値は0件
```

## ★使えなかったもの（全部 実測して落とした。ここが本題）

```
✕ agent_id        ★メイン/サブは分かるが、対話/非対話は分からない。
                  非対話メインの PreToolUse payload に agent_id は無い＝対話メインと同じ。
                  ★hook_role_guard.py の型はここには流用できない
✕ os.isatty()     ★対話・非対話とも 0/1/2 すべて False。
                  フックの標準入出力は claude が繋ぎ替えるので、モードを反映しない
✕ CLAUDE_CODE_CHILD_SESSION   ★対話・非対話とも '1'。子へ継承されるので汚染される
✕ CLAUDECODE      ★両方 '1'
```

**★「使えるはず」で書かないこと。** 上の4つはどれも一見それらしいが、実測すると全部 潰れる。

## ★継承による汚染 ── 唯一の既知の穴

```js
if (ENTRYPOINT が既にある) {
  if (=== "cli" && 非対話) → "sdk-cli" へ直す   // ◎ これは正しく直る
  return                                        // ★それ以外は継承値をそのまま使う
}
```

- `claude -p` の中から**対話**TUIを起こすと、継承した `sdk-cli` が**残る**＝対話なのに非対話と誤判定する。
- ただしこれは「人が居ない場所で人向けのTUIを起こす」という組み合わせなので、実務では起きない。
- **★測るときは要注意。**親の値を消さずに子を起こすと、必ず親の値が出て測り損なう
  （実測時に1回踏んだ。`env` から `CLAUDE_CODE_*` を落としてから起こすこと）。

## ★監査に使える ── transcript にも同じ値が残っている

`~/.claude/projects/**/*.jsonl` の `user` / `assistant` 行に **`entrypoint` 欄がある。**
過去に遡って「どのセッションが非対話だったか」を数えられる＝
**検問を入れる前に、誤検知率を実データで測れる。**

```
実測（mini・2026-09-05）  AskUserQuestion の呼び出しは 6回、★全部 'cli'（対話）
                          非対話 6,723 assistant行での呼び出しは ★0件
```

## ★測るときに踏んだもの

- **対話TUIは pty が要る。**`subprocess` にそのまま渡すと起動しない。`pty.openpty()` を使う。
- **信頼ダイアログが出て止まる。**`~/.claude.json` の `projects[cwd].hasTrustDialogAccepted`
  が false だと、対話起動のたびに聞かれる。★使い捨てディレクトリで受けて、
  **測り終わったらその項目だけ外して原状復帰する**（`/tmp` は `/private/tmp` として記録される）。
- **macOS に `timeout` コマンドは無い。**

## 🔴★そもそも `claude -p` に AskUserQuestion は存在しない（2026-09-05 実測）

**検問を作る前に、止めたい相手が居るかを数えるべきだった。**

```
実測1  claude -p に「AskUserQuestion を使え」と指示 → ★ツールが無く使えなかった
       そのセッション自身が2経路で確認：
         ToolSearch "select:AskUserQuestion" → No matching deferred tools found
         キーワード検索 → 別ツール5本のみ
実測2  mini の transcript 25,261行  非対話 6,723行での呼び出し ★0件
                                   対話  18,538行での呼び出し   6件（7〜8月）
実測3  ★対話TUIでは実在する。pty で起こして実際に呼ばせ、PreToolUse が発火した
```

- **★だから「非対話で AskUserQuestion が出て止まる」は、この構成では起こらない。**
  22分の停止の原因を AskUserQuestion と書いた前提は、mini の記録では裏が取れない。
  実際に止める型は**承認ダイアログ**の方（`hook_permission_slack.py` の領域）。
- **★代わりに起きる型がある（実測）。** ツールが無いと、AIは**本文に番号つきの選択肢を書いて
  「番号だけ返してください」で終わる。** ＝ [[project_ask_hub_push_decisions]] で
  有璽氏が3回止めている記述式そのもの。**止まりはしないが、誰も答えられない。**
  ★これは PreToolUse では捕まえられない（ただの本文）。Stop 側の話。
- **★検問自体は残す価値がある。** ツールの提供有無は版・構成で変わるうえ、対話側では現に実在する。
  ただし**「これで22分の停止が消える」とは言えない。**

## ★対話でも AskUserQuestion は使えない ── この2機は `dontAsk`（2026-09-05 実測）

判定はできるようになったが、**「対話なら AskUserQuestion は正しい道具」は、この2機では成り立たない。**

```
実測  ~/.claude/settings.json の permissions.defaultMode = 'dontAsk'
      （bin/setup_hooks.sh が既定で入れている）
      → ★対話セッションでも AskUserQuestion は拒否されうる
有璽氏（同日・★3回目の指摘）
      ✕ AskUserQuestion（端末のダイアログ）  ★don't ask mode で拒否される・端末依存も同じ
      ◎ ask_hub.ask()
```

**だから検問は2段にする。**

```
非対話  ★ブロック   人が居ないので、警告を出しても結局止まる＝警告は無意味
対話    ★警告のみ   人が居るので警告が効く。止めると有璽氏の作業を殺す（層2で最も怖い誤爆）
判定不能 ★通す
```

→ [[project_ask_hub_push_decisions]]「選択式」の要件3つ（①プッシュで届く ②押せる ③その他は書いて返せる）。
**①が抜けているものは、選択肢が並んでいても不可。**

関連 [[reference_offload_long_work_to_mini]]（非対話で走らせる運用そのもの）
／[[project_ask_hub_push_decisions]]（人に判断を返す正しい経路＝ボタン）
／[[reference_make_it_impossible_not_detectable]]（検出でなく不可能にする）
／[[reference_hooks_enforce_what_discipline_cannot]]（規律で守れないものは機械で止める）
