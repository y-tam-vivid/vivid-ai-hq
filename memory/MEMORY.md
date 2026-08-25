> **ここは「全AI・全担当に効くこと」だけを置く。** 分野ごとの知識は下の分野索引にある。
> 毎ターン届くのはこのファイル。**上限（約24.4KB）があるので、ここは増やさない。**
> 分野索引には上限が無い。新しい記憶は原則そちらへ足す → [[project_memory_layer_design]]

## 分野索引 ── その仕事に着手したら必ず読む

| 何をするとき | 読むもの |
|---|---|
| 営業・顧客台帳・kintone・名刺・受付フォーム | [INDEX_営業](INDEX_営業.md) |
| cron・同期・監視・GAS・シェル・議事録の自動処理 | [INDEX_仕組み](INDEX_仕組み.md) |
| Notionを読む/書く・各DB・Drive・共有設定 | [INDEX_notion](INDEX_notion.md) |
| 広報PR・SNS・Manus・デザイン・成果物の見せ方 | [INDEX_発信](INDEX_発信.md) |
| 担当(10体)の定義・組織・個人まわりの案件 | [INDEX_担当と案件](INDEX_担当と案件.md) |
| 担当ごとの「常設で読むもの」を知りたい | [INDEX_担当別](INDEX_担当別.md) |
| 索引から降ろしたもの・過去の版 | [_archive/INDEX_過去](_archive/INDEX_過去.md) |

## 全体に効くもの（毎ターン届く）

- [Mac miniリモート作業機](project_macmini_remote_workhorse.md) — `ssh mini`で操作する主作業機。~/.claude資産は移植済／残=mini側ログイン認証
- [両機は同じ環境にする](fukuchi-core「マシンと実行の置き場」) — 道具は両機へ。★定期実行は片方だけ・他方は.disabledで残す
- [Mac miniの実行環境](reference_mac_mini_execution_env.md) — 裏側の実行機。Python3.9系／claudeは`~/.npm-global/bin/claude`／到達確認は肯定形で聞く
- [Language: Japanese](feedback_language_japanese.md) — 応答は常に日本語
- [名乗る](feedback_say_who_you_are.md) — ★有璽氏は誰と話しているか分からなくなる。区切りで名乗り直す／自分がビビなら外へ回さない
- [呼称は「有璽」「有璽氏」](feedback_naming_yuji.md) — 「本人」「田村さん」は使わない。全出力に適用
- [モデル使い分け](feedback_model_usage_rule.md) — Sonnet標準/Opus難所/Fable封印。適するモデルは能動的に推奨する
- [思考OS Skill](project_thinking_os_skill.md) — 10レンズ＋6要素骨格をローカルSkill化。/thinking-osで全モデル共通
- [「誤記」と決めつけない](feedback_dont_call_it_a_typo.md) — 実測データは過去の写し。「システムは△△・こちらは◯◯、どちらが正か」と並べて聞く
- [「良い」を作り直さない](feedback_dont_remake_what_was_approved.md) — 変えるのは名指しされた要素だけ／不採用ラベルを勝手に貼らない
- [型を作る前に数える](feedback_check_the_archive_first.md) — ★「揃えろ/合わせて」は作り直しの許可になる(2回目)。触らない対象を列挙
- [作業前にcwdを読む](feedback_read_the_workspace_first.md) — START_HERE/AGENTS/README/.envを先に読む。読まずに「できない」と言わない
- [道具ごとの鍵の在り処](reference_tool_access_map.md) — ★能力は書かない(腐る)。bin/capability_check.shで毎回取りに行く
- [様子を見てから足す](feedback_let_it_settle_before_adding.md) — 入れた仕組みは使ってから次。器を同時に立てない
- [機微の二層管理](feedback_confidential_two_layer_rule.md) — 原則共有・機微だけ`_機微`で本人限定。sort_downloads.pyで自動隔離
- [Artifactは積む](feedback_artifact_accumulate_dont_replace.md) — 作り替えず同じ1ページへ積む／★縮小版は「縮小版・原寸は◯◯」と必ず言う。画質が悪いと言われたらまず自分の圧縮を疑う
- [図解ファースト](feedback_design_diagram_first_minimal_emoji.md) — 流れ・関係・階層は図で見せ言葉は補足。図を1行に潰すのは改悪。絵文字は最小限
- [生成物はNotionへ添付](feedback_generated_files_attach_notion.md) — 該当ページへ実ファイル添付(DL可)。一時領域に放置しない
- [読むもの一覧は地図でない](feedback_reading_list_is_not_a_map.md) — 自分で列挙した一覧は読書履歴。起点1枚＋索引で辿る
- [骨組みを先に見せる](feedback_show_the_skeleton_first.md) — 作る前に3〜5行で形を出す。抽象語(図/整理)が出たら合図
- [実物を読む](feedback_read_the_artifact_not_the_copy.md) — ★欄名が無いは入口(隣列を見る)／★渡すのは行でなくセル(94の21行目→B21)
- [入口は名前で判断しない](reference_dangerous_entrypoints.md) — 載せる前に「書く/書かない/壊す」を実測で1回確かめる／★止めたあとにドライランを通すと実害の中身が分かる(54v3は既存21件を二重に書くところだった)／**日付・IDの突合は正規化してから数える。同じ列で書式が混在し偽陰性が出る**
- [体制はビビ窓口＋ハブ参照](working-via-ai-agents-and-notion-hub.md) — 作業はビビ中央窓口経由＋AIナレッジハブ参照で進める
- [AI資産カタログ](ai-asset-catalog.md) — Drive`AI資産_正本/`を正本と宣言済＝vivid-ai-hqの設計と要調整
- [Downloads整理の2段設計](downloads-archive-system.md) — Stage1は自動化OK／Stage2(事業部・個人)は人＋AI。自動振り分け禁止
- [確認は溜めて1回](feedback_batch_the_checks.md) — 承認が要るのは6項目だけ。入れたものはその場でminiにも入れる
- [「できない」の前に試す](feedback_verify_before_declining.md) — 憶測で断らない。理由＋やりますかまで／★人へ渡す手順は「挿入位置」でなく置き換え後の全文で。実物が1行に収まっており「次の行に」が構文エラーを生んだ(2026-08-23)
- [承認を求めすぎるな](feedback_stop_asking_just_do_it.md) — 既定は自分で進める／★進める分を判断待ちに積むと停滞が人のせいに見える
- [読む人の言葉で書く](feedback_write_for_the_reader.md) — 配る文書に実装名を出さない／公開ページに人名も書かない=権限構造が漏れる
- [毎朝の出力が古い前提を配る](reference_stale_premise_daily.md) — 判断を覆したらレポート文のベタ書きをgrep。3日間流通した
- [測っていない数字を書かない](feedback_never_write_an_unmeasured_number.md) — **真因は速さのために確かさを落としていること(記憶から数字を埋める)**。数える/揃えるを部品に固め呼ぶだけにする／日付はnorm_date()を通した値だけ／件数は「443社(会社名がある行)」と数え方を添える／**★有璽氏の設計＝毎回数えず1か所(dashboard_data.json・読み口facts.py)へ集約し読むだけにする。別々に数えると人ごとに違う答えが出る**／★変種＝APIの`ok:false`を見ず空配列を「0件」と読み、権限があるのに「無い」と報告した(条件を欲張ると権限のある方まで落ちる)／**★部品を置いただけでは既存経路は変わらない。書き込む側から先に置換する（読む側だけ直すと揃って見えて汚れは増える）**
- [1経路で断定するな](feedback_one_route_is_not_verification.md) — 数・存在・状態は2経路／道具を外す判断も2経路。権限が無い≠届かない
- [別マシンとは直接やり取り不可](reference_two_sessions_built_the_same_thing.md) — SendMessageは同じマシン内だけ。連携はWORKING.md/相手のローカル/Notion
- [分けるのはセッションでなく担当](feedback_one_session_split_by_owner.md) — 有璽氏へは1本にまとめて出す
- [一人で抱えるな](feedback_use_the_team_not_alone.md) — ビビは集約係で手を動かさない。★窓口はビビ一人／投げる前に道具の有無を数える
- [届いていても読まれない](reference_delivered_but_unread.md) — 長い文書は埋もれる。起動直前に関係する行だけ4行出す／**★2026-08-24 フックは正しく鳴ったのにこちらが読まず、決着済みの議論(Z列確認欄のSlack運用)を蒸し返した。出力を増やす方向で直さない**
- [止めるのはフック](reference_hooks_enforce_what_discipline_cannot.md) — ★Stopフック導入(MacBookのみ・miniは未登録)。差し戻しは1ターン1回
- [ターミナルからコピーできない](feedback_cannot_copy_from_terminal.md) — mini。渡し方はSlack/リンク/人の手を無くす。★返事は出した経路へ
- [書く前にdiffを見せる](feedback_show_diff_before_edit.md) — 変更内容と同時に触る全ファイルを出して承認を待つ
- [穴は指摘される前に探す](feedback_find_holes_without_being_told.md) — 毎朝08:40 self_audit.pyがつるを起動。自分たちの仕組みは可逆なら直す
- [成果物の形式と本数を復唱](feedback_confirm_the_deliverable_form.md) — 「PR動画」1語で動画を作り込んだ。形式/本数/出口を先に確定する
- [離席前に書き戻す](feedback_write_back_before_you_go.md) — ★①離席宣言③区切りは規律依存で止まる／②無操作は原理的に不可→Stopフックと機械で担保
- [索引は1行180バイトまで](feedback_memory_index_hygiene.md) — 超えるとMEMORY.mdは一部しか届かない(2026-08-21に61,671バイト＝上限2.5倍を実測)。詳細は各ファイル本文へ
- [権限も環境の一部](reference_permissions_are_part_of_the_environment.md) — 両機allow58で解消済。機械を足したら鍵と一緒にpermissionsも揃える
- [上書きの器に過去は無い](reference_overwriting_containers_have_no_past.md) — 定期化する前に「遡れるか」を決める。残す単位は日ごと最新1本・数字(JSON)で残す
- [稼働盤Artifactが止まる](project_ops_dashboard_artifact.md) — ★Vercel公開済(fukuchi-kadoban)＋2時間おき。中身は保護ONまで載せない＝有璽氏が1クリック
- [記憶の層分け設計](project_memory_layer_design.md) — ★8/25実装＋つるで到達確認済(届いた)。残=索引から降ろす承認
- [リリースは配信で終わりでない](feedback_press_release_is_not_done_at_distribution.md) — **関係法人のブログ・SNS投稿文と画像の作成までが1セット**（2026-08-25）。対象は📱発信アカウント台帳を読んで毎回リスト化・投稿の実行者は当面 有璽氏
