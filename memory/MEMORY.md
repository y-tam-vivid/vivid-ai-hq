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

- [Mac miniリモート作業機](project_macmini_remote_workhorse.md) — `ssh mini`で操作する主作業機。~/.claude資産は移植済／残=mini側ログイン認証
- [Language: Japanese](feedback_language_japanese.md) — 応答は常に日本語
- [呼称は「有璽」「有璽氏」](feedback_naming_yuji.md) — 「本人/田村さん」不可／**★制作物も既存物も自動で正としない(3回目)**
- [モデル使い分け](feedback_model_usage_rule.md) — Sonnet標準/Opus難所/Fable封印。適するモデルは能動的に推奨する
- [測っていない数字を書かない](feedback_never_write_an_unmeasured_number.md) — ★速さのために確かさを落とさない。件数は数え方を添える／担当へ渡す数字も測ってから／出典URLは検索結果をそのまま貼る
- [判断はSlackのボタンで返す](project_ask_hub_push_decisions.md) — **全担当の恒久ルール＝判断はask_hubのボタン一本。★出した側が台帳を閉じる。詳細は本文**
- [1経路で断定するな](feedback_one_route_is_not_verification.md) — **🔴9/12★2回。足りない→待つで止めるな。器を縮める／依頼文を作る**
- [Obsidian Core_Brainを動的正本へ](project_obsidian_core_brain.md) — 00_Systemを毎ターン@import／10_Skills_RepositoryはSync除外・リンク4本(両機済)／★MacBookは9/27まで@importが空振り→Core_Brainリンクで解消
- [Current_Focus⇄Notion同期](project_notion_focus_sync.md) — launchd 15分ごと稼働中(9/29〜)。★9/30 同じ目印の2行で完了⇄未完了が往復→行を複製する時は目印を消す。同期側の重複ガードは未実装
- [ツールの使い分けと導入状況](project_tool_roles_and_adoption.md) — Obsidian=机・Notion=本棚・git=完成品。★施設側はClaude未導入・Notionは有璽氏個人＋一部／日々のメモは3か所に分散(Macメモ帳・Chatwork・iPhoneメモ)→Obsidian 01_Inbox のデイリーノートへ集約開始(9/27・振り分けは未)
- [Web公開前の計測は標準](reference_salesbreaker_campaign_setup.md) — 9/29〜全Web必須。Skill web-tracking-setup・公開直前に検問が止める
- [家計台帳⇄統合型営業管理の連携](project_kakei_daicho.md) — **いま：設計担当と全面合意（10/3）・M11は作らない。人軸・顧客を作れるのは統合側だけ・実績は家計→統合の一方向2本。残＝見込み客69件の切り分けと送り方（miniのPython）の返答**
- [素材は広報の設計図でない](feedback_source_material_is_not_the_pr_plan.md) — ★チラシに無い＝書かぬは誤り／配布物を画像欄に載せない
- [こどもまつりのリリース](project_npo_press_kodomomatsuri_202610.md) — 10/18第37回v8済／✅写真の同意OK・後援は確認中／★告知画はAPI直で作る
- [次の一手はタスク行で出す](feedback_emit_next_actions_as_tasks.md) — 区切りごとに Current_Focus「## 今週」へ1行（型はCore_Brain秘書コア§4）→Notionへ自動同期
