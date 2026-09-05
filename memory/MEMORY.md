> **ここは「全AI・全担当に効くこと」だけを置く。** 分野ごとの知識は下の分野索引にある。
> 毎ターン届くのはこのファイル。**上限は 200行 または 25KB（先に来た方）**── 公式仕様で確認済み。
> 2026-08-29 実測 75行 / 13.0KB。★行数にも上限がある点に注意（byteだけ見ない）。
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
- [呼称は「有璽」「有璽氏」](feedback_naming_yuji.md) — 「本人/田村さん」不可／対外は「代表」・グループ名が先／**★制作物の実物を自動で正としない(2回目)**
- [モデル使い分け](feedback_model_usage_rule.md) — Sonnet標準/Opus難所/Fable封印。適するモデルは能動的に推奨する
- [思考OS Skill](project_thinking_os_skill.md) — 10レンズ＋6要素骨格をローカルSkill化。/thinking-osで全モデル共通
- [「誤記」と決めつけない](feedback_dont_call_it_a_typo.md) — 実測データは過去の写し。並べて聞く／**★既存の器を「足りない」と決めつけない。列名が同じでも意味は同じでない(会場=エリアだった)。対処は変えるでなく足す**
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
- [実物を読む](feedback_read_the_artifact_not_the_copy.md) — ★欄名が無いは入口(隣列を見る)／★渡すのは行でなくセル／**★有璽氏が言うのは症状。原因は別(「左に余白」の真因は番号バッジが画面外へ飛んでいた)。直す前に実物で1回見る**／**★9/5 縮小画像で見た目を判定しない。図形は潰れても“それらしく”見える。原寸で切り出す**
- [入口は名前で判断しない](reference_dangerous_entrypoints.md) — 載せる前に「書く/書かない/壊す」を実測で1回確かめる／★止めたあとにドライランを通すと実害の中身が分かる(54v3は既存21件を二重に書くところだった)／**日付・IDの突合は正規化してから数える。同じ列で書式が混在し偽陰性が出る**
- [体制はビビ窓口＋ハブ参照](working-via-ai-agents-and-notion-hub.md) — 作業はビビ中央窓口経由＋AIナレッジハブ参照で進める
- [AI資産カタログ](ai-asset-catalog.md) — Drive`AI資産_正本/`を正本と宣言済＝vivid-ai-hqの設計と要調整
- [Downloads整理の2段設計](downloads-archive-system.md) — Stage1は自動化OK／Stage2(事業部・個人)は人＋AI。自動振り分け禁止
- [確認は溜めて1回](feedback_batch_the_checks.md) — 承認6項目だけ／両機に入れる／**★溜めるのは確認。報告は溜めず進んだ時点で出す**
- [「できない」の前に試す](feedback_verify_before_declining.md) — 憶測で断らない。理由＋やりますかまで／★人へ渡す手順は「挿入位置」でなく置き換え後の全文で。実物が1行に収まっており「次の行に」が構文エラーを生んだ(2026-08-23)
- [承認を求めすぎるな](feedback_stop_asking_just_do_it.md) — 既定は自分で進める／★積むと停滞が人のせいに見える／**★9/4 有璽氏に「私待ちを教えて」と聞かせた。待ちの置き場は5つ以上あり横断の一覧が無い。「なし」と言う前に全部数える**
- [読む人の言葉で書く](feedback_write_for_the_reader.md) — 配る文書に実装名を出さない／公開ページに人名も=権限構造が漏れる／判断を仰ぐ行も主語を道具の名にしない／**★「反映した」と書くな。原稿に書いただけを相手は「画面に出た」と読む。どこで見えるかを1行で言う(見えないなら見えないと)**
- [通知は押せる形にする](feedback_write_for_the_reader.md) — ★届くだけでは不足。営業以外はDM／★9/4「通知が来ない」＝届く方も未達。送った≠届いた
- [毎朝の出力が古い前提を配る](reference_stale_premise_daily.md) — 判断を覆したらレポート文のベタ書きをgrep。3日間流通した
- [測っていない数字を書かない](feedback_never_write_an_unmeasured_number.md) — **真因は速さのために確かさを落としていること(記憶から数字を埋める)**。数える/揃えるを部品に固め呼ぶだけにする／日付はnorm_date()を通した値だけ／件数は「443社(会社名がある行)」と数え方を添える／**★有璽氏の設計＝毎回数えず1か所(dashboard_data.json・読み口facts.py)へ集約し読むだけにする。別々に数えると人ごとに違う答えが出る**／★変種＝APIの`ok:false`を見ず空配列を「0件」と読み、権限があるのに「無い」と報告した(条件を欲張ると権限のある方まで落ちる)／**★部品を置いただけでは既存経路は変わらない。書き込む側から先に置換する（読む側だけ直すと揃って見えて汚れは増える）**／**★「解消11件」の申告を突合したら7件だった。過剰修正は本人には成功に見えるので申告に出ない＝別主体で読むしかない**／**★9/4「残り18ページ」が実物では1ページ。「そのクラスを持つ数」を「直っていない数」として書いた。分母を2段で書く**
- [直った基準を目的側に](reference_verify_outcome_not_mechanism.md) — **★9/5再発で実測＝24分→67秒。真因(旧接続の残留)は未修正**
- [判断はSlackのボタンで返す](project_ask_hub_push_decisions.md) — 🔴9/4 2回目＝**全担当の恒久ルール**（ボタン一本・報告に混ぜない）／**★押されても聞いた側へ返らない。投げたら毎回 answer_of() を見に行く**／**★kindは8種のみ(開発/営業/福祉/広報/財務/法務/個人/その他)。予約通知が'経営'でValueError→1h40m気づかず。仕込む前にpreviewを1回通す**／**★9/5 端末の承認ダイアログはSlackでは解けない(返事は新セッションを起こすだけ)。有璽氏の決定＝運用でなく構造を直す。①通知へ機名 ②Slackで押せる形＝要承認・未着手**
- [1経路で断定するな](feedback_one_route_is_not_verification.md) — 数・存在・状態は2経路／0件は別法で数え直す／★列挙は絞らず全部出す／**★限界の申告は免罪符でない(「1本しか開いていない」と書きつつ「0件」と断定→実際は1件)**／**★有璽氏が数字に違和感を示したら数え直す。9/4は2回連続で外した(42→24→実測627)。表計算は1枚目だけ数えない／行数でなく「使える列が埋まった行」**／**★逆に「その認識で合っている」と言われたら測らない。裏取りは自分の推測にだけ当てる**
- [同じ依頼が2つのセッションへ入る](reference_two_sessions_built_the_same_thing.md) — ⛔9/5 notify巻き戻りの真因は別と判明。型自体は実在
- [直した所は配られるか](reference_fix_where_git_reaches.md) — ★bin/hooks/に同名があれば~/.vivid-relay/を直しても15分で消える。触る前に1回ls
- [分けるのはセッションでなく担当](feedback_one_session_split_by_owner.md) — 有璽氏へは1本にまとめて出す
- [担当が落ちる真因はスリープ](feedback_use_the_team_not_alone.md) — ⛔「1体を長く使うと落ちる」は**誤診**（分割しても3体落ちた）。★真因はMacBookのスリープ。**長い作業はminiで走らせる**→[[reference_offload_long_work_to_mini]]
- [一人で抱えるな](feedback_use_the_team_not_alone.md) — ビビは集約係で手を動かさない。★窓口はビビ一人／投げる前に道具の有無を数える／**★完了報告は「指示の側」から読む。落ちた指示は報告に出ない（「できません」は書けるが「忘れました」は本人にも見えない）。指示に番号を振り、番号ごとに実物で確かめる**／**★2026-08-29「ギャッやるなよ。誰かにやらせろ」＝2回目。★「存在しません」で止めるな＝スキル名でなく①スキル②bin/③pip④過去実績のgrepで数える（Word変換は既にbin/md2docx.pyが在った）**
- [手順書が読まれない理由](reference_why_manuals_are_not_read.md) — ★一度間違えると二度と読まれない。○×を求めると信頼が下がる
- [記録を書くが読んでいない](reference_delivered_but_unread.md) — ★3回目。提案/作成の前にmemoryとNotionを数える。「無いから作る」禁止
- [届いていても読まれない](reference_delivered_but_unread.md) — 長い文書は埋もれる。起動直前に関係する行だけ4行出す／**★2026-08-24 フックは正しく鳴ったのにこちらが読まず、決着済みの議論(Z列確認欄のSlack運用)を蒸し返した。出力を増やす方向で直さない**
- [止めるのはフック](reference_hooks_enforce_what_discipline_cannot.md) — ★9/5 役割検問がmini担当セッションを誤検出(agent_id無=ビビと断定)
- [検出でなく不可能にする](reference_make_it_impossible_not_detectable.md) — ★1975年に結論済＝検出型は原理的に不完全。規範配下をread-onlyへ
- [規範95枚に止める機械は4つ](reference_norms_outnumber_their_enforcement.md) — 8/29に0→4へ。★規範の変更とお金は今もaskに無く無防備
- [次の回に何が届くか](reference_what_actually_reaches_the_next_turn.md) — ★公式仕様。MEMORY.mdは200行or25KB。フック25種中3種のみ使用
- [心拍は生死しか見ない](reference_heartbeat_proves_life_not_results.md) — 成果の数字と期待値／★落ちると心拍ゼロ＝遅延と同色。該当11本
- [誰も拾わない警告は無に等しい](reference_a_warning_nobody_owns.md) — ★9/3 混入を直したら届く経路ごと消えた／表示だけで警告にしない
- [探さずに人へ投げるな](reference_no_gate_on_asking_the_human.md) — ★8/29 Stopフックに検査2。未検索で「無い」と言うと差し戻す
- [判断待ちは両方向で壊れる](reference_pending_decision_does_not_pause_the_pipeline.md) — ★9/5解決。pendingはask_hubへ聞く。孤児はlink_pendingで結ぶ
- [kintoneの列は写しの写し](reference_stale_copy_of_kintone_columns.md) — ★未接続。雛形62列もSkill61列も実物より短い。無いと断定しない
- [ターミナルからコピーできない](feedback_cannot_copy_from_terminal.md) — mini。渡し方はSlack/リンク/人の手を無くす。★返事は出した経路へ
- [書く前にdiffを見せる](feedback_show_diff_before_edit.md) — 変更内容と同時に触る全ファイルを出して承認を待つ
- [日本語に別の文字が混入する](reference_unicode_escape_kanji_swap.md) — ★\uエスケープで漢字化け／**★9/5機械で解消。Stopフック検査4(キリル/ハングル/タイ/デーヴァナーガリー検出)でexit2差し戻し。実測誤検知0/35**
- [検査に出す版を固定する](reference_freeze_the_version_under_review.md) — ★検査中に作る側が触ると判定がどの版か不明。sha256を添えて渡す
- [穴は指摘される前に探す](feedback_find_holes_without_being_told.md) — 毎朝08:40 self_audit.pyがつるを起動／★材料の発言欄は38%が偽物。本文を読む
- [成果物の形式と本数を復唱](feedback_confirm_the_deliverable_form.md) — 形式/本数/出口を先に確定／**★9/4 有璽氏へ渡す文書は.mdで渡さない。bin/md2pdf.pyでPDF化（docx/pptxもbin/にある）**
- [離席前に書き戻す](feedback_write_back_before_you_go.md) — ★①離席宣言③区切りは規律依存で止まる／②無操作は原理的に不可→Stopフックと機械で担保
- [索引は1行180バイトまで](feedback_memory_index_hygiene.md) — ★件数が構造的に上限。棚卸しは`memory_audit.py --retire`で候補を出す（判断は人）。いま降ろすものは無い
- [権限も環境の一部](reference_permissions_are_part_of_the_environment.md) — ★allowに*があってもaskが勝つ／★拒否は3層。operation not permittedはsettings.jsonで直らない／**★9/5 保護パスはAND(目的の承認＋手段が可逆)。指示だけを根拠にせず、成功報告には指示の在処まで書く**
- [控えは置き場も中身も](reference_backups_in_volatile_places.md) — ★消える場所もgit下も不可。bin/hooksの控えは_backups/へ。名指しで保存する
- [gitに入れた機微は消せない](reference_secrets_in_git_history.md) — ★9/4 口座番号がpush済。作業場所をrepo外へ・履歴の書き換えは要承認
- [MCPの読取は平文で残る](reference_tool_results_cache_keeps_secrets.md) — ★tool-results/に機微が残る。掃除で消えない・親が最後に消す
- [制作は原則miniへ](reference_offload_long_work_to_mini.md) — ★止まりはログでなくtranscriptで見る。対応づけは指示文(起動時刻は4割誤る)
- [上書きの器に過去は無い](reference_overwriting_containers_have_no_past.md) — 定期化する前に「遡れるか」を決める。残す単位は日ごと最新1本・数字(JSON)で残す
- [Vercel無料プランの保護](reference_vercel_free_plan_protection.md) — ★終わらないdeployはBLOCKED(commit author未登録)が真因。重さでない
- [稼働盤Artifactが止まる](project_ops_dashboard_artifact.md) — ★解決。Vercel(fukuchi-kadoban)へ2時間おき＋Basic認証。有璽氏の操作は無し
- [記憶の層分け設計](project_memory_layer_design.md) — ★8/25実装＋つるで到達確認済(届いた)。残=索引から降ろす承認
- [SNS画像は誰が作るか](feedback_who_makes_the_images.md) — デザイン物は外／写真の切出しはこちら。★Canvaで生成できる(要手直し)
- [リリースは配信で終わりでない](feedback_press_release_is_not_done_at_distribution.md) — **関係法人のブログ・SNS投稿文と画像の作成までが1セット**（2026-08-25）。対象は📱発信アカウント台帳を読んで毎回リスト化・投稿の実行者は当面 有璽氏
- [SB送信前の必須3点](reference_salesbreaker_campaign_setup.md) — ★全案件必須。タグ4本+パス/UTMで経路分離+.md封鎖。送信後は取り返せない
