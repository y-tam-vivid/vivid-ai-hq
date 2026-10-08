---
name: project_macmini_remote_workhorse
description: "Mac miniをリモートのClaude Code作業機に。MacBookから`ssh mini`で操作。資産移植済み、残りはmini側のログイン認証"
metadata: 
  node_type: memory
  type: project
  originSessionId: 641c1ccc-baa6-431e-ab77-d8158697ed01
---

Mac mini を「Claude Code の主作業機」にし、MacBook から遠隔操作する構成（2026-07-10 構築）。

## 接続情報
- Mac mini OSアカウント短縮名: **`yuji_macmini`**（MacBookの`yujimac`とは別。@Macはホスト名）。ホーム=/Users/yuji_macmini
- Tailscale: mac-mini = 100.126.116.44 / MagicDNS `mac-mini.taild56082.ts.net`（tailnet taild56082）。MacBook=macbook-pro 100.103.130.58
- SSH鍵認証済み: MacBook `~/.ssh/id_ed25519`（無パスフレーズ）→ mini `~/.ssh/authorized_keys`
- MacBook `~/.ssh/config` に **エイリアス `mini`** 追加済 → `ssh mini` でパスワード無しログイン
- 注意: miniはmacOSのリモートログインが**パスワード認証を拒否**する設定。鍵認証のみ。GUIは`vnc://100.126.116.44`

## 移植済み資産（MacBook ~/.claude → mini）
- agents/ 10体（ビビ/ナミ/センゴク/ロビン/モルガンズ/ステラ+開発4体+pr-playbook）
- 記憶27件+MEMORY.md → mini `~/.claude/projects/-Users-yuji-macmini/memory/`（ホームから`claude`起動で読まれる）
  - **重要な落とし穴**: Claude Codeのprojectスラッグはパスの`_`を`-`に変換する。`/Users/yuji_macmini`→スラッグは`-Users-yuji-macmini`（ダッシュ）であって`-Users-yuji_macmini`ではない。最初アンダースコア側に置いて記憶が読まれず、ダッシュ側へ移して解決
- skills / output-styles(Fable Style) / settings.json(Fable Style既定)
- CLAUDE.md(共通ルール)はmini側に既存

## 環境（mini）
- macOS 26.4 / arm64 / node,npm(/usr/local/bin),git,brew(/opt/homebrew)有り
- Claude Code CLI: `@anthropic-ai/claude-code` v2.1.206。実体は`~/.npm-global/bin/claude`、`.zshrc`でPATH追加済
- 導入時メモ: npmのallow-scriptsでpostinstallがブロックされる→パッケージ内`node install.cjs`を手動実行で解決

## ログイン完了（2026-07-11）
- mini側Claude Codeログイン済み（Claude Maxサブスク認証）。表示が"API Usage Billing"→"Claude Max"に変化で確認
- ログイン手順メモ: `ssh mini`→`claude`→`/login`。SSH越しはTerminal.appのクリップボード(`c to copy`/OSC52)が効かず、認証URLをコピペできない→**支援者がスクショのURLを書き出してMacBookローカルで選択コピー→ブラウザ**が確実。URLのstate/challengeはセッション固有なので画面を開いたまま操作（Escで無効化）

## 認証の永続化（確認済み 2026-07-11）
- 認証は`~/.claude/.credentials.json`(ファイル)にも保存され、SSH越し(headless)でも有効。macOSキーチェーンはSSHセッションでロック(`User interaction is not allowed`)されるが、Claudeはファイル認証にフォールバックして動く
- 検証: `ssh mini '~/.npm-global/bin/claude -p "..."'` で応答が返る＝ヘッドレス認証OK。※非対話SSHは`.zshrc`のPATHが読まれないので`claude`はフルパス`~/.npm-global/bin/claude`で叩く
- 初回ログイン直後の再起動で一度だけ再`/login`を要求されたが、ファイル認証保存後は解消

## 同期の仕組み（2026-07-11 構築）
- **`~/bin/sync-claude-mini.sh`**（MacBook）= **双方向自動同期**（新しい方が勝つ/削除は伝播しない）。MacBook起点でmini→MacBook(pull)→MacBook→mini(push)を`rsync -au`。対象=agents/skills/output-styles/memory。memoryは`-Users-yujimac`↔miniの`-Users-yuji-macmini`をマッピング。ログ=`~/.claude/sync-mini.log`。多重起動はmkdirロックで防止、mini不達なら静かに終了
- **crontabで15分ごとに自動実行**（`*/15 * * * *`）。※LaunchAgentは`~/Library/LaunchAgents`がroot所有755で書けず不可→cron採用。既存cron(sort_downloads/chatwork_relay)と併存
- 旧`~/bin/sync-claude-to-mini.sh`=一方向ミラー(--delete)。手動で強制上書きしたい時用に残置
- 割り切り: ①削除は自動伝播しない ②同一ファイル同時編集は新しい方で上書き。完全履歴が要るならgit方式へ
- 前提: MacBookが起動中の時だけ同期(cron起点)。MacBook休止中のtickはスキップ、起床後の次tickで同期

## 残タスク（任意）
- MCPコネクタ(Notion/Drive等)はアカウント連携型(claudeAiMcpEverConnected)。mini側で`/mcp`で状態確認、要認証ならVNCでmini側ブラウザから許可(SSH越しはURLコピー不可のため)
- 未実施: 記憶/エージェント更新の**両機同期の仕組み化**(git private repo等)。今はrsyncで手動push可
- settings.local.json(権限allowlist)は機体固有のため未移植。miniでは権限プロンプトが初期は多め

関連: [[reference_ai_org_chart]] [[project_secretary_agent]]

## 🔴 2026-10-05 通信不通の真因（実測）
- **有線LAN（Ethernet・優先順1位）の設定が壊れている**：「DHCP（ルーターは手入力）」で IP 192.168.1.200／★サブネットマスク 255.255.255.255／★ルーター空欄（DHCP INFORM の返答は旧ルーター 192.168.0.254）
- macOS は優先1位の有線を主経路にするため、★既定経路が無くなり外へ出られない（ping 8.8.8.8 NG・clarity/github/slack 000）。★Wi-Fi（192.168.1.9・ルーター 192.168.1.1）を明示すれば 200＝回線は生きている
- 有璽氏「ネットはつながっているはず」＝回線とWi-Fiは正しい。壊れているのは有線LANの設定だけ
- 直し方（★システム設定なので有璽氏の手で）：システム設定→ネットワーク→Ethernet→詳細→TCP/IP→「手入力」IP 192.168.1.200／サブネット 255.255.255.0／ルーター 192.168.1.1（または「DHCPサーバを使用」）
- 確かめ方：`ssh mini 'route -n get 8.8.8.8; curl -s -o /dev/null -w "%{http_code}" https://github.com/'`
- ✅10/5 15:2x 有璽氏が修正 → ★外へ出られるようになった（github/clarity 200・ping OK）。ただし★経路は Wi-Fi(en1)。有線は IP 192.168.2.200（1→2の打ち間違い疑い）・マスク /32・ルーター空欄・方式「DHCP（ルーター手入力）」のまま＝★Wi-Fiが切れると再び止まる。有線の直しは未
- ✅10/5 mini の git 枝分かれ（ahead 8／behind 201・10/1〜通信断の間）を解消：止めていたのは claude.ai同期スキル google-workspace の未追跡9本（origin と同一を確認して _backups/untracked_google-workspace_20261005 へ退避）＋状態ファイル2本の衝突（origin を採用）。控え枝 backup/mini-before-merge-20261005。両機 🟢
- ★10/1〜10/5 の通信断の間、mini 発の自動処理（Slack通知・ask_hub・daily_jobs 等）は外へ出られていない＝ドーベルマンで取りこぼしを点検する

## ✅ 2026-10-05 夕 解消（mini 上のAIが直した）
- 有璽氏が手で直そうとしたが「DHCP（ルーター手入力）」のまま・IP 192.168.**2**.200・マスク/32・ルーター空欄で残っていた
- ★**画面で直してもらうより、AIが mini 上で `networksetup -setmanual "Ethernet" 192.168.1.200 255.255.255.0 192.168.1.1` を叩く方が速く確実**（管理者パスワード不要・rc=0で通った）。★次からは有璽氏に画面操作を渡す前にこれを試す
- 実測：経路1 = 既定経路 interface en0・gateway 192.168.1.1 ／ 経路2 = `curl --interface en0 https://github.com` 200 → 一致。ルーターへの ping 0%損失
- 戻し方：`networksetup -setdhcp "Ethernet"`

## 🔴2026-10-06 17:37 ★ssh が切れたら、miniの障害と決めつけず★自分のIPを見る

**症状**：それまで通っていた `ssh mini` が `Could not resolve hostname tamurayuujinoMac-mini.local` で落ちた。

**真因＝miniではなく★こちら（MacBook）が別のネットワークへ移っていた。**

```
実測  MacBookのIP     10.3.14.246   ゲートウェイ 10.2.0.126   SSID 00_MCD-FREE-WIFI（外出先）
      miniのIP        192.168.1.200（自宅/事務所の網）
      ping            192.168.1.200 ／ 192.168.2.200 とも★100%ロス
      外への通信       github へ 200 ＝★回線自体は生きている
→ ★別セグメントにいる。mDNS（.local）も網をまたげないので名前解決から落ちる
```

**★切り分けの順（この順で2経路見る）**
```
① 自分のIPとゲートウェイ    route -n get default ／ ipconfig getifaddr en0
② miniのIPへ直接 ping       192.168.1.200
③ 外への通信                curl -o /dev/null -w "%{http_code}" https://github.com
①が 192.168.1.x でなければ★miniは無関係。網へ戻るまで待つ（miniを疑わない）
```

- **★mini へ投げた仕事は、ssh が切れても走り続ける。** `run_agent.sh` は内部でバックグラウンドへ
  切り離すため、こちらの回線が落ちても止まらない。**結果は mini の出口ファイルに残る。**
- **How to apply:** 外出先（フリーWi-Fi・テザリング）では mini へ届かない。
  長い処理を投げたら、**同じ網へ戻ってから出口を読む**。届かないことを「失敗」と報告しない。

### ★同日 追記 ── ①生存は git で分かる ②出口を `~/.vivid-relay` だけに置くと読めない

```
✅miniが生きている証拠（★ssh不通でも分かる）
   git fetch → behind が増える。17:00:04 に mini の自動確定（60分放置ぶん）が来ていた
   ＝★インターネット経由の経路（git）は網をまたぐ。ssh（LAN・mDNS）だけが届かない

🔴出口が読めない
   指示文で出口を ~/.vivid-relay/<name>.md と決めた。★これは git 管理外＝★同じ網でしか読めない
   → ssh が切れた瞬間に、仕事の結果を取り出す経路が★0本になった
```

**★mini へ仕事を投げるときは、出口を2本持たせる。**
```
① ~/.vivid-relay/<name>.md          ★詳細（同じ網で読む）
② ★終わったら notify.tell() で Slack へ1本   ★網をまたぐ。「終わった・出口はここ」だけ
   （長い結果を貼らない。冒頭に「返信は要りません」を付ける → reference_slack_notification_rules）
```
★今回（10/6 チョッパー）は②を指示文に入れていなかった。**終わったことに気づく経路が無い。**
**How to apply:** `run_agent.sh` へ渡す指示文に「完了したら notify.tell で知らせる」を必ず1行入れる。


## MEMORY.md の索引から戻した記述（2026-10-08 棚卸し・索引には現在地だけを残した）

- `ssh mini`で操作する主作業機。10/5 通信は復旧（★Wi-Fi経由）。有線LANはまだ壊れたまま（IP 192.168.2.200・/32・ルーター空欄）＝Wi-Fiが切れると止まる
- ★10/6 17:37 sshが切れた真因は★こちらが別網(外出先Wi-Fi 10.3.x)＝miniは無関係。先に自分のIPを見る。投げた仕事は切り離し済みで走り続けるが★出口(~/.vivid-relay)は同じ網でしか読めない→指示文に「終わったらnotify.tell」を必ず入れる。生存はgitのbehindで分かる。✅10/5夕 有線LAN復旧（手入力 192.168.1.200/24・ルーター .1・既定経路=有線を実測）。★設定はminiのAIが networksetup で直せる＝画面操作を人に渡さない
