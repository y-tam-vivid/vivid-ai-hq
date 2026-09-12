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
- [区分は必ず増える](project_lifestandup_website_wordpress.md) — **★9/9 有璽氏「カテゴリーは今後増えることも想定し設計して」＝005は3分割で確定。★3つを固定値で書かずtaxonomyで持ち、タブ/絞り込み/一覧はtermを回して自動生成。1件足す＝管理画面で1語**
- [ルールを足す前に既存と突合](project_lifestandup_website_wordpress.md) — **★9/10 恒久ルール追加3条を突合＝重複2・★変更1・拡大1。★「追加」と言われても実質★前の決定の上書きのことがある。★数値(px/%)が出たら過去の値を必ず引く**
- [「良い」を作り直さない](feedback_dont_remake_what_was_approved.md) — 変えるのは名指しされた要素だけ／不採用ラベルを勝手に貼らない
- [型を作る前に数える](feedback_check_the_archive_first.md) — ★「揃えろ/合わせて」は作り直しの許可になる(2回目)。触らない対象を列挙
- [特別な理由がなければ全ページ統一](feedback_uniform_unless_reason.md) — ★9/8で5回目。揃った値自体が指摘を満たすか別途確認／★素材にも。「暗い」でなく「異なる」＝基準値1つで揃える
- [作業前にcwdを読む](feedback_read_the_workspace_first.md) — START_HERE/AGENTS/README/.envを先に読む。読まずに「できない」と言わない
- [道具ごとの鍵の在り処](reference_tool_access_map.md) — ★能力は書かない(腐る)。bin/capability_check.shで毎回取りに行く
- [様子を見てから足す](feedback_let_it_settle_before_adding.md) — 入れた仕組みは使ってから次。器を同時に立てない
- [機微の二層管理](feedback_confidential_two_layer_rule.md) — 原則共有・機微だけ`_機微`で本人限定。sort_downloads.pyで自動隔離
- [Artifactは積む](feedback_artifact_accumulate_dont_replace.md) — 作り替えず同じ1ページへ積む／★縮小版は「縮小版・原寸は◯◯」と必ず言う。画質が悪いと言われたらまず自分の圧縮を疑う
- [図解ファースト](feedback_design_diagram_first_minimal_emoji.md) — 流れ・関係・階層は図で見せ言葉は補足。図を1行に潰すのは改悪。絵文字は最小限
- [生成物はNotionへ添付](feedback_generated_files_attach_notion.md) — 該当ページへ実ファイル添付(DL可)。一時領域に放置しない
- [読むもの一覧は地図でない](feedback_reading_list_is_not_a_map.md) — 自分で列挙した一覧は読書履歴。起点1枚＋索引で辿る
- [骨組みを先に見せる](feedback_show_the_skeleton_first.md) — **🔴9/10で★3回連続。★こちらが代償を計算して機能を落とす（写真の添付を外した）。★機能は載せ代償は1行で言う＝決めるのは有璽氏**
- [業務の単位まで割る](feedback_break_down_to_the_work_level.md) — 🔴9/8「中身がなくない？」＝集計で止めるな。1行＝1業務で誰が/いくら/自社可否＋価格(福祉の同業→他業種・下限/平均/上限・出典つき)／★同じ発言から2台が別々に記憶を作った＝[[feedback_deliverable_granularity_must_be_actionable]]と重複
- [実物を読む](feedback_read_the_artifact_not_the_copy.md) — **★9/12「会議室っぽく全然ない」＝実物を見せられたら分解でなく★見た目を再現する。場の比喩は絵(床/机/人)が要る**／症状と原因は別・欄名が無いは入口・列一致≠同じ器（全部本文へ）
- [入口は名前で判断しない](reference_dangerous_entrypoints.md) — 載せる前に「書く/書かない/壊す」を実測／**★9/10 findの-deleteは-pruneを黙って無効化＝除外が効かない。消す前に-printで数える**
- [体制はビビ窓口＋ハブ参照](working-via-ai-agents-and-notion-hub.md) — 作業はビビ中央窓口経由＋AIナレッジハブ参照で進める
- [AI資産カタログ](ai-asset-catalog.md) — Drive`AI資産_正本/`を正本と宣言済＝vivid-ai-hqの設計と要調整
- [Downloads整理の2段設計](downloads-archive-system.md) — Stage1は自動化OK／Stage2(事業部・個人)は人＋AI。自動振り分け禁止
- [確認は溜めて報告は溜めない](feedback_batch_the_checks.md) — **🔴9/9「途中経過も共有ください」＝2回目。★「変化なし」は機械の状態が同じという意味で、★共有することが無いではない。★終わった担当の出口ファイルはその回のうちに読んで要点を出す**
- [「できない」の前に試す](feedback_verify_before_declining.md) — **🔴9/12 ★画面の手順を記憶で書いて外した（Googleフォームは「送信」→★「公開」へ変わっていた）＝★先に画面を1枚もらう・文言でなく★アイコンの位置で言う**／9/10 5日前の記録を数えず手作業29問を渡した／自分の言語にSDKが無い＝できないではない
- [止まるな・滞留をゼロに](feedback_stop_asking_just_do_it.md) — **🔴9/10 commitして「完了」と報告し★出していなかった(公開URLは0件)。★報告文に「どこで見えるか」を必ず1行。★作った/実装したは完了でない＝動いている状態が完了**
- [読む人の言葉で書く](feedback_write_for_the_reader.md) — 🔴9/10★可視化は「問題だけが目に入る」形に。全部に枠を描くと埋もれる／★渡すとき見方を3行添える／実装名でなく日本語／「反映した」と書くな
- [触る画面は説明でなく画面自体を直す](feedback_ui_must_be_self_explanatory.md) — **🔴9/10同日2回目「使い方がよくわからん」＝説明を足しても直らない。ウィザード型(1度に1指示)へ**
- [通知は押せる形＋読める形に](feedback_write_for_the_reader.md) — **🔴9/8「長ったらしいのは見づらい」＝親は「◯時の通知です」＋要約だけ・★詳細はスレッドへ追記（chat.postMessageのtsをthread_tsに）。出す側の部品で揃える**／ ★届くだけでは不足。営業以外はDM／★9/4「通知が来ない」＝届く方も未達。送った≠届いた
- [土台にも日付がある](reference_stale_premise_daily.md) — **★9/10 器は9/9・成果物は9/10で★1日で前提が変わっていた。★都度の指摘に頼らず機械で数える＝bin/kb_schema_check.py（表示側のキー⇄器の列⇄taxonomy）。★名前で見つかるズレだけ。意味の変化は人が見る**
- [測っていない数字を書かない](feedback_never_write_an_unmeasured_number.md) — ★真因は速さのために確かさを落とすこと。数える部品を1か所へ集約し読むだけにする。件数は数え方を添える
- [直った基準を目的側に](reference_verify_outcome_not_mechanism.md) — 🔴9/10「★60px左手に配置」を「60px以上内側ならOK」と読み替え7/6箇所を無変更。★位置か下限かは動詞で決まる／件数0を合格にしない
- [判断はSlackのボタンで返す](project_ask_hub_push_decisions.md) — **全担当の恒久ルール＝判断はask_hubのボタン一本・報告に混ぜない。kindは8種／投げる前にpreview／投げたら必ずanswer_of()を見る（押されても聞いた側へ返らない）。🔴9/7 4回目＝1通ずつでなく★Slackへ出る経路を全部数えて揃える。押せないものが混ざると判断が沈む（DM7通中押せるのは2通）。出すのはボタン・受けるのは会話でもよいが★出した側が台帳を閉じる**
- [1経路で断定するな](feedback_one_route_is_not_verification.md) — **🔴9/12★2回。足りない→待つで止めるな。器を縮める／依頼文を作る**
- [同じ依頼が2つのセッションへ入る](reference_two_sessions_built_the_same_thing.md) — ★数えるもの5つ目＝★未コミットの積み残し。担当が終わった瞬間にgit statusを数える／PID指定・pkill -f不可
- [直した所は配られるか](reference_fix_where_git_reaches.md) — ★bin/hooks/に同名があれば~/.vivid-relay/を直しても15分で消える。触る前に1回ls
- [分けるのはセッションでなく担当](feedback_one_session_split_by_owner.md) — **🔴9/9 体不足でなく★割り当ての偏り（ビビが全部リリスへ投げていた）。増やす前に割り当てを直す。報告は1本に**
- [担当が落ちる真因はスリープ](feedback_use_the_team_not_alone.md) — ⛔「1体を長く使うと落ちる」は**誤診**（分割しても3体落ちた）。★真因はMacBookのスリープ。**長い作業はminiで走らせる**→[[reference_offload_long_work_to_mini]]
- [一人で抱えるな](feedback_use_the_team_not_alone.md) — **🔴9/9 承認をもらった005を★1時間半投げていなかった（★記録はした＝記録は着手ではない）。★承認をもらったら記録と同じターンで投げる。投げられないなら★時刻で言う。★毎回の報告に「承認済みで未着手」の行を置く**
- [手順書が読まれない理由](reference_why_manuals_are_not_read.md) — ★一度間違えると二度と読まれない。○×を求めると信頼が下がる
- [記録を書くが読んでいない](reference_delivered_but_unread.md) — **★9/9外部調査＝この分野に★定説は無い（複数の情報源が「初期段階」と明言）。★15体規模の公開事例は0件。★一致は3つだけ＝①独立したcontext ②★作成者と検証者の分離(cross-checkと一致) ③★ハーネス側で強制。★輸入では解けない＝自前で決めて実測で直す**／★3回目。提案/作成の前にmemoryとNotionを数える。「無いから作る」禁止
- [届いていても読まれない](reference_delivered_but_unread.md) — 長い文書は埋もれる。起動直前に関係する行だけ4行出す／**★2026-08-24 フックは正しく鳴ったのにこちらが読まず、決着済みの議論(Z列確認欄のSlack運用)を蒸し返した。出力を増やす方向で直さない**
- [止めるのはフック](reference_hooks_enforce_what_discipline_cannot.md) — ★9/5 役割検問がmini担当セッションを誤検出(agent_id無=ビビと断定)
- [検出でなく不可能にする](reference_make_it_impossible_not_detectable.md) — ★1975年に結論済＝検出型は原理的に不完全。規範配下をread-onlyへ／**★9/5「対策は複数またがって用意して」＝層1検知・層2予防・層3解除を同時に。検知だけでは止まる回数は1回も減らない**／**★9/7「記録しました を何回も言って同じことを繰り返してる」＝記録は再発を止めない。サイトの出し直しは`~/lifestandup-wp/redeploy.sh`1本へ固め、`ng_words.txt`の語が残ればデプロイを止める。担当の完了は`~/.vivid-relay/after_agent.sh`が見張りSlackへ出す**
- [規範95枚に止める機械は4つ](reference_norms_outnumber_their_enforcement.md) — **★9/9 初めて穴を名指しで数えた＝Ｃ(在るのに効かない)3件。★C-1 hook_interactive_guardは★settings.json未登録＋★毎朝の点検CASESにも無い＝二重の見えなさ(4日)。★新しい検問は同じターンでCASESにも足す。✅C-1は有璽氏の承認で修正済(両機7本とも正常)。★足した瞬間に環境依存の誤検知が出た＝★環境変数に依存するフックは点検も同じenvで叩く**／8/29に0→4へ。★規範の変更とお金は今もaskに無く無防備
- [次の回に何が届くか](reference_what_actually_reaches_the_next_turn.md) — ★公式仕様。MEMORY.mdは200行or25KB。フック25種中3種のみ使用
- [心拍は生死しか見ない](reference_heartbeat_proves_life_not_results.md) — 成果の数字と期待値／★落ちると心拍ゼロ＝遅延と同色。該当11本→**9/8 progress_report.py修正済み・残10本**／**★9/8 頻度も1日2回→毎時(07-22時)へ。crontab直書き・daily_jobs.conf側は無効化のみ**
- [誰も拾わない警告は無に等しい](reference_a_warning_nobody_owns.md) — ★9/10で2回目。慢性の🟡は内訳を数える（2件中1件は誤検知）／実体欄に説明を書くと機械が誤読する
- [探さずに人へ投げるな](reference_no_gate_on_asking_the_human.md) — ★8/29 Stopフックに検査2。未検索で「無い」と言うと差し戻す
- [判断待ちは両方向で壊れる](reference_pending_decision_does_not_pause_the_pipeline.md) — ★9/5解決。pendingはask_hubへ聞く。孤児はlink_pendingで結ぶ
- [sheets_clientはクラス](reference_sheets_no_credentials_on_mini.md) — ★9/11 sc.Sheets()を作る。meta()の戻りは name/rows(titleでない)。★道具は要約でなく実物のソースを見る
- [kintoneの列は写しの写し](reference_stale_copy_of_kintone_columns.md) — ★未接続。雛形62列もSkill61列も実物より短い。無いと断定しない
- [ターミナルからコピーできない](feedback_cannot_copy_from_terminal.md) — **🔴9/9 5例目＝「着手完了」と報告したが実物は全部mini内で★有璽氏へ0件。★報告前に「本人はどこで見られるか」を自問し、見られないなら★まだ完了でなく中間物と言う**／渡すのはSlack添付/Driveのリンク。★その場で使うファイルは`open`でFinderを開く(6例目・zipはminiに在り触れなかった)／**★9/8 4例目＝ローカルのファイルパスも届かない。実測値の羅列は成果物でない。見える形にして渡すまでが1セット**
- [渡す物は受け取り手の要件で数える](project_lifestandup_website_wordpress.md) — **★9/9 テーマzipが本番でインストール失敗（階層が1つ深い）。★「ファイルが在る」と「相手が使える形か」は別。zipは`unzip -l`の先頭3行を見る**
- [書く前にdiffを見せる](feedback_show_diff_before_edit.md) — 変更内容と同時に触る全ファイルを出して承認を待つ
- [日本語に別の文字が混入する](reference_unicode_escape_kanji_swap.md) — ★\uエスケープで漢字化け／**★9/5機械で解消(Stopフック検査4)。★9/9に本番3例目「этот」・4例目「진」(進)を機械が先に検出＝★同日2回働いた。★意味の同じ外国語に化けるので目視では素通り**
- [検査に出す版を固定する](reference_freeze_the_version_under_review.md) — ★検査中に作る側が触ると判定がどの版か不明。sha256を添えて渡す
- [穴は指摘される前に探す](feedback_find_holes_without_being_told.md) — ★9/11 報告8回中3回がStopフックですり替わり未達・🟢のまま
- [成果物の形式と本数を復唱](feedback_confirm_the_deliverable_form.md) — 形式/本数/出口を先に確定／**★9/4 有璽氏へ渡す文書は.mdで渡さない。bin/md2pdf.pyでPDF化**
- [離席前に書き戻す](feedback_write_back_before_you_go.md) — ★担保2つとも効かず。自動確定の7割は生成物のみ／差し戻しは4回とも空振り／★①離席宣言③区切りは規律依存で止まる／②無操作は原理的に不可→Stopフックと機械で担保
- [索引は1行180バイトまで](feedback_memory_index_hygiene.md) — **⛔9/9真因＝本数でなく1本の長さ(180B超が40/78本)。★降ろさず「本文へ戻す」。消す前に本文に在るか数える。bin/check_index_line_length.py**
- [権限も環境の一部](reference_permissions_are_part_of_the_environment.md) — **★9/9 有璽氏が★本番WordPressの許可を出した（恒久制約の解除）。✅9/9 21:40 ★本番で新テーマが動いた（方式B・インストール済み／★有効化していない＝サイトは不変）。★不可逆は「有効化」の1手だけ＝そこは人が押す。★順序（デモ完成→zip→本番）は許可が出ても崩さない**
- [控えは置き場も中身も](reference_backups_in_volatile_places.md) — ★消える場所もgit下も不可。**★9/8 4例目＝相手のツールの作業フォルダも不可。控えは_backups/へ**
- [gitに入れた機微は消せない](reference_secrets_in_git_history.md) — ★9/4 口座番号がpush済。作業場所をrepo外へ・履歴の書き換えは要承認
- [MCPの読取は平文で残る](reference_tool_results_cache_keeps_secrets.md) — ★tool-results/に機微が残る。掃除で消えない・親が最後に消す
- [制作は原則miniへ](reference_offload_long_work_to_mini.md) — ★9/11 sshが断続的にタイムアウト(3回)。★1回で落ちたと判定しない＝再試行3回＋別経路。★担当はPIDで生死を見る
- [上書きの器に過去は無い](reference_overwriting_containers_have_no_past.md) — 定期化する前に「遡れるか」を決める。残す単位は日ごと最新1本・数字(JSON)で残す
- [公開が詰まる真因は grep -r](project_lifestandup_website_wordpress.md) — **🔴9/9 redeploy.shが2回詰まった(21分/6分)。⛔★「真因＝grep -r」は不十分だった＝★直しても3回目も止まった。★手で打つと数秒・スクリプト内だと止まる＝★未特定。✅9/10 ★手動6手順が3回目も成功(13分)。★指示文へ毎回6手順を書くのが速い。★redeploy.shは直さない。★安全装置を外すのでなく速くする。★npx をcronから呼ぶ時は`< /dev/null`**
- [Vercel無料プランの保護](reference_vercel_free_plan_protection.md) — ★403=Mitigations(DDoS防御)・時間帯で振れる。★1回0枚で断定せず再試行／スクショはstatic-previewを配信して撮る／枠100本･日次リセット。数字と解除手順は本文へ戻した(9/12)
- [Secretは読み出せない](project_ops_dashboard.md) — **✅9/9決着＝稼働盤は正常（有璽氏「見れています」）。⛔401は当方の誤診＝`vercel env pull`は`[SENSITIVE]`(11文字)を返す。★AIが測れるのは「合言葉なしで401」まで。「ありで200」は人の領域＝★測れないと分かったら担当を起こす前に人へ1行聞く（今回は順番が逆だった）**
- [AI社員オフィス＝会議室](project_ai_office_console.md) — ★9/12 優先①本人②社内③外部(福祉施設の事務)。★指示はSlackと画面の両方＝入口2･台帳1。★スマホ必須で画面は2層
- [稼働盤Artifactが止まる](project_ops_dashboard_artifact.md) — ★解決。Vercel(fukuchi-kadoban)へ2時間おき＋Basic認証。有璽氏の操作は無し
- [記憶の層分け設計](project_memory_layer_design.md) — ★8/25実装＋つるで到達確認済(届いた)。残=索引から降ろす承認
- [本番WPは読むだけで測れる](project_lifestandup_website_wordpress.md) — **★9/9 公開APIとHTMLのcurlだけで移行の未確定8→4件。★top(14)/blog(16)確定・/trial・★Emanon BusinessはProの子テーマ（Proも要る）。★人へ聞く前に公開URLから数える**
- [IGをサイトへ出す](project_lifestandup_website_wordpress.md) — **✅9/9 IG側は完了。★ショートコード=`[instagram-feed feed=1]`（保存済）。★動くのは本番WPだけ・デモは静的で展開されない。残＝テーマへdo_shortcode+フォールバックを仕込む／余計な4プラグイン停止。★同日4件が同じ根＝実物を見ずに人の画面を指示した**
- [SNS画像は誰が作るか](feedback_who_makes_the_images.md) — デザイン物は外／写真の切出しはこちら。★Canvaで生成できる(要手直し)
- [リリースは配信で終わりでない](feedback_press_release_is_not_done_at_distribution.md) — 文面と画像まで1セット／★施設IGに業界の話は不可
- [外の知を先に見る](feedback_look_outside_before_reinventing.md) — ★9/8有璽氏「お前だけで考えんな」。同じ型の失敗が繰り返されたら自前パッチの前にクローバーへ業界調査を投げる
- [網羅は出典より件数](feedback_coverage_over_citation_when_asked_to_enumerate.md) — ★9/8「網羅的に」出典なし・推測でも項目は落とさない。数値だけ出典必須
- [SB送信前の必須3点](reference_salesbreaker_campaign_setup.md) — ★全案件必須。タグ4本+パス/UTMで経路分離+.md封鎖。送信後は取り返せない
- [恒久ルール⑥60pxちょうど配置](project_lifestandup_website_wordpress.md) — ⛔誤読訂正。★タブレット崩れはpx修正でなく構造修正へ転換(9/10)
- [Web制作ルールを資産に](project_web_build_rules_asset.md) — ✅9/10 ★Cがブラウザで使える(lsu-editor/・合言葉つき・遅延1〜6分)。config1本で別サイトへ。★find -deleteは-pruneを無効化し巻き込む
- [恒久ルール⑤40px比例](project_lifestandup_website_wordpress.md) — ★9/10 Web40px基準にsp/tablet比例(24/35px)。④判断つかない分類は廃止
- [Claude Designのものを公開する](reference_claude_design_local_edit_not_reflected.md) — ★9/10 書き出しは★3形式ある(bundler/生HTML/.dc.html+React)。★形式判別の工程が要る。C→Design は不可
