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
