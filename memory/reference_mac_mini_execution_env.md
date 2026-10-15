---
name: reference_mac_mini_execution_env
description: Mac miniは裏側の常時稼働・実行機（メイン）。定期実行はここに置く。Python3.9系・claude CLIはPATH外・GitHub鍵は専用。スクリプトを書く前に読む
metadata:
  node_type: memory
  type: reference
---

**Mac mini が裏側のメイン実行機**（2026-08-13 本人確定）。定期実行・バッチは原則ここへ置く。
MacBook は閉じている時間がある前提で設計する。規範の本文は [[project_notion_operating_rules]] ではなく
正本 `vivid-ai-hq/.claude/skills/fukuchi-core/SKILL.md` の「マシンと実行の置き場」節。

**mini 向けにスクリプトを書く前に必ず踏むこと**

- **Python は 3.9.6**（MacBook と揃っていない）。`match` 文・f-string の `=` 記法など
  **3.10以降の構文を使うと本番でだけ落ちる**。`~/.vivid-relay/` に足すものは3.9互換で書く。
  確認は `ssh mini 'python3 -m py_compile <file>'`。
- **`claude` CLI は入っているが PATH に出ない。** 実体は `~/.npm-global/bin/claude`（v2.1.228）。
  `.zshrc` で PATH に足されているが、**SSHの非ログインシェルでは読まれない**ため
  `which claude` が空振りする。「入っていない」と誤判定しやすい。**フルパスで呼ぶ。**
- **GitHub 用の鍵は mini 専用**（`~/.ssh/id_ed25519_github`／`~/.ssh/config` で github.com に紐付け）。
  MacBook の鍵とは別物。mini からの `git` 操作はこの鍵で通る。
- Google Drive は mini にもマウント済み（`~/Library/CloudStorage/GoogleDrive-y_tam@vivid-global.com`）。
  ただし **Downloads整理は MacBook に残す**。対象が MacBook の `~/Downloads` だから。
- **`lsof` も同じ穴を持つ（2026-09-07 実測）。** 実体は `/usr/sbin/lsof`。
  cron の最小PATH（`/usr/bin:/bin`）には `/usr/sbin` が入っておらず、`subprocess.run(['lsof',...])`
  のように裸の名前で呼ぶと**手元では動くのにcronでだけ黙って失敗する**（`[Errno 2] No such
  file or directory`）。実測：`env -i PATH=/usr/bin:/bin which lsof` は失敗・`which find` は
  `/usr/bin/find` で成功（findは無事）。**`/usr/sbin/` 配下のコマンド（lsof・その他）を
  cronから叩くスクリプトは、必ず絶対パスで呼ぶか、先に `which` で解決してから使う。**
  実例：`~/.vivid-relay/stall_watch.py` がこれで9ヶ月間気づかれず、cronへ初めて
  登録した日に5分おきのエラーログとして発覚した（`LSOF_BIN = _find_bin(...)` で対処）。

**現在の cron（mini）**

```
*/15  vivid-ai-hq を git pull --ff-only（設定の受信。送信は本人が push）
7:45  Chatworkリレー（MacBookから移設）
```

**エージェントに規範が届いているかの確認方法**

「参照できていない場合はそう答えて」と条件を付けると、**実際は読めていても保守的に
「参照できていない」と答える**（MacBook・mini 双方で発生し、一度誤判定した）。
**肯定形で聞く** ―「その内容は含まれていますか。含まれていれば1行そのまま引用して」。

## ✅2026-10-07 実測 ── ★cron も launchd も環境変数を持たせていない（スクリプトが自分で読む）

```
cron            40行。★export も source も無い。/usr/bin/python3 を直接呼ぶだけ
launchd         3本（com.vivid.{slack-socket, notion-focus-sync, ai-usage-report}）
                ★どれも EnvironmentVariables を持っていない（PlistBuddy で実測）
→ ★では環境変数はどこから来るのか ＝ ★スクリプトが自分で ~/.vivid-relay/config.env を読んでいる
   ★35本の .py がこの形。共通関数 load_config_env() が3本にある
   （ask_hub_to_notion.py / import_chatwork_done.py / notion_focus_sync.py）
```

- **★「config.env に書けば読める」は不正確。** 正しくは**「読む側のコードが読むから読める」**。
  新しいスクリプトを書くときは★自分で読む処理を入れる（入れ忘れると鍵が無いまま動く）
- **🔴すでに常駐しているプロセスには届かない。** `com.vivid.slack-socket` は
  ★PID 4613・★2026-09-26 から動き続けている＝**起動時に読んだ値しか持っていない**。
  鍵を足した後に使わせるなら★再起動が要る：
  `launchctl kickstart -k gui/$(id -u)/com.vivid.slack-socket`
- ★`~/.vivid-relay` の権限は `drwxr-xr-x`（755）＝**ファイル名は他者に見える**。
  ★中身を守っているのは★ファイル側の 600（`-rw-------`）。新しく作るときは `umask 077` か `chmod 600`
- ★`~/.vivid-relay` は**git リポジトリではない**（実測）。`vivid-ai-hq` の外にあるので追跡対象にもならない


## MEMORY.md の索引から戻した記述（2026-10-08 棚卸し・索引には現在地だけを残した）

- **★10/7実測 cron40行・launchd3本とも★環境変数を持たせていない＝スクリプトが自分で config.env を読む（35本・共通関数 load_config_env）。「書けば読める」は不正確。★新しいスクリプトは自分で読む処理を入れる／🔴常駐プロセス(slack-socket PID4613・9/26から)は起動時の値しか持たない＝再起動が要る／~/.vivid-relay は git外・ディレクトリは755でファイル側600が中身を守っている**

## 🔴2026-10-08 ★キーチェーンに触るなら LaunchAgent。`launchctl asuser` も効かない

```
経路A  SSH から直接 security find-generic-password     🔴 終了コード36（User interaction is not allowed）
経路B  ssh → launchctl asuser 501 security …           🔴 Could not switch to audit session: Operation not permitted
経路C  ★一度きりの LaunchAgent を bootstrap gui/501     ✅ 読める・書ける（実測 64文字を読み出し）
```

**★Cの形（そのまま使える）**
```bash
# /tmp に plist を置き、RunAtLoad で1回だけ走らせ、終わったら bootout して消す
launchctl bootout   gui/501/com.vivid.<名前> 2>/dev/null
launchctl bootstrap gui/501 /tmp/com.vivid.<名前>.plist
sleep 5          # ★結果はファイルに書かせて読む（標準出力は返ってこない）
launchctl bootout gui/501/com.vivid.<名前>; rm -f /tmp/com.vivid.<名前>.plist
```
★plist の ProgramArguments は**絶対パス**で書く（`~` は展開されない）。

## 🔴2026-10-08 ★`notify.py` は配布先（`~/.vivid-relay/`）の版を import する

```
✗ sys.path.insert(0, "~/vivid-ai-hq/bin/hooks")   → 🔴 config.env が無い（FileNotFoundError）
✅ sys.path.insert(0, "~/.vivid-relay")            → ✅ 送れる
```
★`notify.py` は `config.env` を**自分と同じディレクトリ**から読む（コード中のコメントに明記）。
git 側の版には `config.env` が無い（★秘密を git に置かないため正しい）。
**★「同じ名前のファイルがある」＝「同じものが動く」ではない。配布先を使う。**

🔴**ヒアドキュメントと標準入力はぶつかる。** `printf … | python3 - <<"PY"` は
**★ヒアドキュメントが stdin を奪う**ので、パイプの値は届かない（2026-10-08 実測・1個しか読めなかった）。
→ ★値を渡すなら**スクリプトをファイルに置いてから**パイプする。

🔴**claude の認証は ssh では通り、cron では落ちる（2026-10-14 実測）。** 長期トークン `CLAUDE_CODE_OAUTH_TOKEN` は
`~/.zshenv` にある＝★ssh のシェルだけが読む。cron は読まない → `.credentials.json` に落ち、その更新鍵は **10/5 08:56 で期限切れ**。
```
ssh mini 'claude -p …'                       → OK（★ここで「直っている」と思わない）
env -i HOME=… PATH=/usr/bin:/bin claude -p … → Failed to authenticate: OAuth session expired
影響   claude を呼ぶ self_audit / memory_sweep（10/5〜🔴）・inbox_runner / slack_inbox / team_run も同じ型（呼ばれた時に落ちる）
```
→ ★claude を呼ぶスクリプトは config.env から `CLAUDE_CODE_OAUTH_TOKEN` を subprocess の env へ渡す。確かめるのは `env -i` で。
✅**10/14 直した（#c31c98 有璽氏承認）**：入口 `~/.vivid-relay/claude_cron.sh`（git `bin/claude_cron.sh`）が config.env から読んで本体を exec。
self_audit / memory_sweep / slack_inbox / inbox_runner / team_run / run_agent.sh の6か所をこの入口へ。★新しく claude を呼ぶものもこの入口を使う。
✅**10/14 `--model` も明示（#fa2a60 有璽氏「仕分け系はHaiku／指示を実行する系はSonnet」）**：memory_sweep=haiku、ほか5本=sonnet。★新しく足すものも必ず --model を書く（Core_Brain 17_モデルの使い分け）。

## 🔴 MacBook の `claude -p` が返らなくなる（2026-10-15 実測）

```
10:02  drive_unkibi.py を起動（40件を haiku で判定）
10:09  終了。★40件のうち28件が「返りを読めない」＝判定できていなかった
       （前の回の drive_sort は 08:47 に87件を正常に判定している＝途中から壊れた）
10:11  同じ呼び出しを単体で試す → ★120秒でも240秒でも返らない
```

- **★`claude -p` が返らないとき、スクリプトは落ちない。** `drive_sort.py` も
  `drive_unkibi.py` も except で既定値（部門=不明／区分=3）へ倒す作りなので、
  **全件が「不明」や「安全側」に落ちたまま、見かけは正常に完走する。**
  ＝★これは [[reference_ran_is_not_succeeded]] の一種。終了コード0が判定の成功を示さない。
- **★対策は「落ちた件数を数えて、閾値を超えたら止める」。**
  いまは落ちた件数が出力に混ざるだけで、合計の行には出ない。
  ★`claude -p` を使う仕分けは、**冒頭で1件だけ試し、返らなければ着手しない**。
- **追記（同日・後の実測）:** 同じ MacBook で `claude -p --model haiku --settings …` を1件だけ試したら **5.8秒で返り、rc 0・出力は正しいJSON**。★返らない状態は一時的だった可能性がある。
  ただし1回の成功は「直った」の証拠にならない。仕分けを再開する前は、冒頭の1件試しを毎回やる。
- ★同じ処理を mini で回す選択肢がある（[[project_macmini_remote_workhorse]]）が、
  **Drive のマウントは機械ごと**。MacBook の `/Users/yujimac/Library/CloudStorage/...` は
  mini から見えない。**ファイルを扱う仕分けは、そのファイルが在る機械でしか動かせない。**
- ★判定が少数（数十件）なら、**セッション自身が中身を読んで決めるほうが速くて正確**だった
  （10/15 の40件はこれで片づけた）。Haikuに投げるのは件数が多いときの手段であって、目的ではない。

### ✅ 原因が確定した ── 一時的な不調ではなく、フックの引き継ぎだった（2026-10-15 バックオフィス担当が mini で再現）

**上の「返らない状態は一時的だった可能性がある」は撤回する。** mini で再現した。

```
実測（mini・env -i で claude_cron.sh を叩く）
  ★hook_ask_answers が★子プロセスの入口で発火していた
    → ask_answers_seen/ に新しいファイルが増える
  ★07:05／08:30／08:40 の cron 分にも同じ跡があった
    ＝ 毎朝の自動処理が、ずっとこの影響を受けていた
  outputStyle も Fable Style（user と project の両方）
  ★その回は偶然JSONが返ったが、Stop の催促が鳴る日は壊れる
```

**✕採らなかった直し**：`--setting-sources` で user を外す
→ **許可設定（permissions）まで落ちる。** 隔離の代償が大きすぎる。

```
◎mini 側の直し（commit e996a7e・バックオフィス担当）
  1 claude_cron.sh が VIVID_CRON_CLAUDE=1 を立て、--settings '{"outputStyle":"default"}' を付ける
  2 UserPromptSubmit／Stop のフック3本（hook_ask_answers／hook_catch_correction／
    hook_session_writeback）は★その印があれば何もしない
    ★PreToolUse の検問は残す（地雷の注入は子でも効かせたい）
  確認：env -i で `{"区分": 1}` だけが返り、seen ファイルは増えない（10→10）
  控え：mini `_backups/*.bak_20261015_cronhooks`

◎MacBook 側（drive_sort.py・commit 6b164c0）
  ~/.vivid-relay/_claude_iso/settings.json（{"hooks": {}, "outputStyle": "default"}）を
  --settings で渡し、★cwd もそこにする（リポジトリの CLAUDE.md を引き継がせない）
  ★claude_cron.sh を通すなら印が立つので、この隔離は要らない
```

- **★「対話のために入れたフック」が、無人で動くAIの入口にも入る。**
  フックを足すときは「対話セッションだけに効かせるのか」を必ず決める。
  ★印（環境変数）で分けるのが、いまのところ唯一きれいな分け方。
- **★1回成功しても「直った」にしない。** こちらは1件試して5.8秒で返ったので
  「一時的だった」と書きかけた。**再現させた側の実測が正しかった。**
  → [[feedback_one_route_is_not_verification]]
