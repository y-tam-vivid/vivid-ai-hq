> **2026-09-24 軽量化。** 毎ターン届くのはこのファイルだけ。**ここには最小限しか置かない。**
> 動的なルール・ナレッジの正本は Obsidian **`~/Documents/Core_Brain/00_System/`**（MOC から辿る）。
> ここ（vivid-ai-hq）は完成したコード・スキルの置き場。旧「全体に効くもの」110行は [INDEX_全体](INDEX_全体.md) へ退避（消していない）。

## 分野索引 ── その仕事に着手したら必ず読む

| 何をするとき | 読むもの |
|---|---|
| ★全体に効く規範・過去の地雷（旧MEMORY.mdの本体） | [INDEX_全体](INDEX_全体.md) |
| 営業・顧客台帳・kintone・名刺・受付フォーム | [INDEX_営業](INDEX_営業.md) |
| cron・同期・監視・GAS・シェル・議事録の自動処理 | [INDEX_仕組み](INDEX_仕組み.md) |
| Notionを読む/書く・各DB・Drive・共有設定 | [INDEX_notion](INDEX_notion.md) |
| 広報PR・SNS・Manus・デザイン・成果物の見せ方 | [INDEX_発信](INDEX_発信.md) |
| 担当(10体)の定義・組織・個人まわりの案件 | [INDEX_担当と案件](INDEX_担当と案件.md) |
| 担当ごとの「常設で読むもの」を知りたい | [INDEX_担当別](INDEX_担当別.md) |
| 索引から降ろしたもの・過去の版 | [_archive/INDEX_過去](_archive/INDEX_過去.md) |

## 毎ターン届けるもの（最小限）

- [Mac miniリモート作業機](project_macmini_remote_workhorse.md) — `ssh mini`で操作する主作業機。10/5 通信は復旧（★Wi-Fi経由）。有線LANはまだ壊れたまま（IP 192.168.2.200・/32・ルーター空欄）＝Wi-Fiが切れると止まる
- [Mac miniリモート作業機](project_macmini_remote_workhorse.md) — `ssh mini`で操作する主作業機。✅10/5夕 有線LAN復旧（手入力 192.168.1.200/24・ルーター .1・既定経路=有線を実測）。★設定はminiのAIが networksetup で直せる＝画面操作を人に渡さない
- [Language: Japanese](feedback_language_japanese.md) — 応答は常に日本語
- [呼称は「有璽」「有璽氏」](feedback_naming_yuji.md) — 「本人/田村さん」不可／**★制作物も既存物も自動で正としない(3回目)**
- [モデル使い分け](feedback_model_usage_rule.md) — Sonnet標準/Opus難所/Fable封印。適するモデルは能動的に推奨する
- [測っていない数字を書かない](feedback_never_write_an_unmeasured_number.md) — ★速さのために確かさを落とさない。件数は数え方を添える／担当へ渡す数字も測ってから／出典URLは検索結果をそのまま貼る
- [離席を告げられたらSlackへ](reference_slack_notification_rules.md) — 10/5 有璽氏。★以降の進捗はnotify.tell()。会話に書いても届かない
- [判断はSlackのボタン](project_ask_hub_push_decisions.md) — ★ターン終了前にopenを数える。1週間超は前提を測り直す(10/5 前提が消えていた)
- [1経路で断定するな](feedback_one_route_is_not_verification.md) — 🔴★応答を返したのが誰かを見る(10/5 whoisがIANAで止まり9件誤判定寸前)
- [Obsidian Core_Brainを動的正本へ](project_obsidian_core_brain.md) — 00_Systemを毎ターン@import／10_Skills_RepositoryはSync除外・リンク4本(両機済)／★MacBookは9/27まで@importが空振り→Core_Brainリンクで解消
- [Current_Focus⇄Notion同期](project_notion_focus_sync.md) — launchd 15分ごと稼働中(9/29〜)。★9/30 同じ目印の2行で完了⇄未完了が往復→行を複製する時は目印を消す。同期側の重複ガードは未実装
- [ツールの使い分けと導入状況](project_tool_roles_and_adoption.md) — Obsidian=机・Notion=本棚・git=完成品。★施設側はClaude未導入・Notionは有璽氏個人＋一部／日々のメモは3か所に分散(Macメモ帳・Chatwork・iPhoneメモ)→Obsidian 01_Inbox のデイリーノートへ集約開始(9/27・振り分けは未)
- [Web公開前の計測は標準](reference_salesbreaker_campaign_setup.md) — 9/29〜全Web必須。Skill web-tracking-setup・公開直前に検問が止める
- [★実データが入ったら早く公開](feedback_seo_standard_kit.md) — 10/5有璽氏。検索に載るまで時間がかかる。計測は★sites.jsonに載せて予約
- [公開中サイトのSEO標準装備](feedback_seo_standard_kit.md) — 10/5〜 Clarity＋Search Console＋サイトマップ＋月次レビュー。★Clarity設置済＝ILIFE・ふくち。・オレンジ・119番・こどもS／ビビッドのみ保留(WPログインURL不明)。台帳 bin/web_tracking/sites.json。★月次レビューの本体はクラウドのルーティン「SEO巡回エージェント」(trig_01Y9…)
- [家計台帳⇄統合型営業管理の連携](project_kakei_daicho.md) — **いま：設計担当と全面合意（10/3）・M11は作らない。人軸・顧客を作れるのは統合側だけ・実績は家計→統合の一方向2本。残＝見込み客69件の切り分けと送り方（miniのPython）の返答**
- [渡し物はDrive案件フォルダ・番号を振る](reference_backups_in_volatile_places.md) — 10/5。★入れる前にDrive側を数える(16世代が既に在った)
- [素材は広報の設計図でない](feedback_source_material_is_not_the_pr_plan.md) — ★チラシに無い＝書かぬは誤り／配布物を画像欄に載せない
- [こどもステーション団体サイト](project_minamikawachi_kodomo_station_site.md) — ko-station.org 本番(v45)。直しの正本は ~/kodomo-photo-work/*_fixes.py＋api_src。★Ad Grants 審査待ち(10/5申請・10/7に確認)。立ち上げ手順とCSVは05/02_Google広告に用意済み
- [こどもまつりのリリース](project_npo_press_kodomomatsuri_202610.md) — v22。★配信10/6(火)10:00／★入稿素材は一式そろった(Drive 06_…/04_入稿素材・本文は全体2,501字)／★PR TIMESの下書きは未作成
- [PR TIMES入稿の罠と切り分け](reference_prtimes_editor_behaviors.md) — ★入稿前に必ず読む。**★報道素材に入れても記事本文に写真は載らない(別物・10/5に指摘を受けた)／必ずプレビューで見る**／行頭の「1.」で全体がリスト化(解除不可)／画面が読めない時は拡張のサインインを見る
- [かわちばなし地域ポータル](project_kawachibanashi_portal.md) — **シート→サイトは9/13から kb_live.sh で稼働中（10/5 3経路一致で実測）＝新しく作らない**。★10/5夜 器に下書き47件（kb-0004〜0050・公開は人が付ける。収集は ~/.vivid-relay/kb_collect.py）。★~/kawachibanashi_site は9/10の残骸（同じVercelに紐づく・ここから出さない）
- [こどもまつりのリリース](project_npo_press_kodomomatsuri_202610.md) — ★PR TIMES下書き作成中(release_id=6)・配信10/6(火)10:00は動かさない(有璽氏10/5)。写真は2枚並べで足せるだけ。★配信10/6(火)10:00／★入稿素材は一式そろった(Drive 06_…/04_入稿素材・本文は全体2,501字)／★PR TIMESの下書きは未作成
- [PR TIMES入稿の罠と切り分け](reference_prtimes_editor_behaviors.md) — ★入稿前に必ず読む。**★報道素材に入れても記事本文に写真は載らない(別物)／**★写真は多めが既定(上限30枚)・勝手に絞らない(10/5に2回指摘)／作る前によそのリリースを1本見て形を決める**／必ずプレビューで見る**／行頭の「1.」で全体がリスト化(解除不可)／画面が読めない時は拡張のサインインを見る
- [かわちばなし地域ポータル](project_kawachibanashi_portal.md) — **シート→サイトは9/13から kb_live.sh で稼働中（10/5 3経路一致で実測）＝新しく作らない**。★穴＝トップの見本6件。★~/kawachibanashi_site は9/10の残骸（同じVercelに紐づく・ここから出さない）
- [次の一手はタスク行で出す](feedback_emit_next_actions_as_tasks.md) — 区切りごとに Current_Focus「## 今週」へ1行（型はCore_Brain秘書コア§4）→Notionへ自動同期
