> **毎ターン届くのはこのファイルだけ。** 載せるのは★全仕事に効く行動の規範と、忘れたら設計を壊す事実だけ。
> 案件の現在地は分野索引（下の表）へ。1行180バイトまで・既存行へ継ぎ足さない → 作り方・更新・棚卸しの正本は Core_Brain `00_System/15_毎ターン届くMDの作り方と更新方法.md`
> 動的なルールの正本は Obsidian `~/Documents/Core_Brain/00_System/`。10/8 棚卸しの前の全文 → [_archive/MEMORY_full_20261008](_archive/MEMORY_full_20261008.md)

## 分野索引 ── その仕事に着手したら必ず読む

| 何をするとき | 読むもの |
|---|---|
| ★全体に効く規範・過去の地雷 | [INDEX_全体](INDEX_全体.md) |
| 営業・顧客台帳・家計台帳・kintone・名刺・受付フォーム | [INDEX_営業](INDEX_営業.md) |
| cron・同期・監視・GAS・シェル・朝ブリーフィング・DNS | [INDEX_仕組み](INDEX_仕組み.md) |
| Notionを読む/書く・各DB・Drive・共有設定 | [INDEX_notion](INDEX_notion.md) |
| 広報PR・Web制作・SEO・デザイン・かわちばなし・こどもS | [INDEX_発信](INDEX_発信.md) |
| 担当の定義・組織・個人まわりの案件 | [INDEX_担当と案件](INDEX_担当と案件.md) |
| 担当ごとの「常設で読むもの」 | [INDEX_担当別](INDEX_担当別.md) |
| 索引から降ろしたもの・過去の版 | [_archive/INDEX_過去](_archive/INDEX_過去.md) |

## 毎ターン届けるもの

- [Language: Japanese](feedback_language_japanese.md) — 応答は常に日本語。★英語の画面・ツール出力が続く作業ほど流される。書く前に1回見る
- [呼称は「有璽」「有璽氏」](feedback_naming_yuji.md) — 「本人/田村さん」不可／制作物も既存物も自動で正としない
- [モデル使い分け](feedback_model_usage_rule.md) — Sonnet標準/Opus難所/Fable封印。★定型の仕分けはHaiku＋機械。迷いは人へ(10/14)
- [測っていない数字を書かない](feedback_never_write_an_unmeasured_number.md) — 数え方を添える。★回数は grep -o|wc -l（grep -c は行の数）
- [渡された件数は数え方から](feedback_never_write_an_unmeasured_number.md) — ★findの既定はドットを拾う。7,894→実7,154の740件差(10/16)
- [1経路で断定するな](feedback_one_route_is_not_verification.md) — 出どころの違う2経路で。自分の警告・自分が書いた印を事実と取り違えない
- [記録の「待ち」は腐る](reference_stale_premise_daily.md) — ★着手前に実測。10/14 cronの「切替待ち」が3か月そのままだった
- [相手の資料は全部読む](feedback_source_material_is_not_the_pr_plan.md) — grep等の部分読みは読んだことにならない（10/8 約束を2つ破った）
- [案を出す前に探す](feedback_check_the_archive_first.md) — 規約の類は誰かが作っている。★命名規約の正本はNotion📛（10/14）
- [フェーズを確かめる](feedback_ask_which_phase.md) — 着手前に「どの段階の話か」を1問。できない理由がどの段階の条件かも
- [読む人に合わせて書く](feedback_write_for_the_reader.md) — 相手の文を返さない。運用の変化と崩れた前提だけ返す
- [音声入力の人名・団体名・日付](feedback_voice_input_name_kanji.md) — 人名も団体名も登録済みの表記を正に。当てた字と日付を返事で示す
- [次の一手と有璽氏の作業](feedback_emit_next_actions_as_tasks.md) — 03へ区分付きで足す。★渡す行は受け取り方まで書く
- [答え済みの行はその場で閉じる](feedback_emit_next_actions_as_tasks.md) — ★答えを実行したら同じターンで03を[x]にする
- [[x]は答えでない](feedback_emit_next_actions_as_tasks.md) — ★Notionで✅にする経路でも答えが来る。知らぬ間の[x]は1問で確かめる
- [進捗は確認状況とセット](feedback_emit_next_actions_as_tasks.md) — ★有璽氏10/16。①進捗②有璽氏の未回答③止めている分 を分母つきで
- [規約を読んでから勧める](feedback_check_platform_policy_before_recommending.md) — ★勧める前に提供元の規約と制限を読む
- [押す場所は位置と結果まで](feedback_verify_before_declining.md) — ★人へ渡す前に検査を通す（渡せば即実行され訂正が間に合わない）
- [着手時に目安時刻を伝える](feedback_batch_the_checks.md) — 何をする＋完了目安／変われば言い直す／その時刻に自分で見る
- [担当の長い作業はminiで](feedback_batch_the_checks.md) — ★2時間超は着手時にminiへ投げる。見回りもmini（MacBookは落ちる）
- [「一旦」の承認は恒久でない](feedback_provisional_approval_is_not_final.md) — 出してよいかと★何で変わるかを対で記録。完了にしない
- [窓口はSNSのことも](reference_partner_web_presence_may_be_sns.md) — ★サイト無し≠載せるもの無し。Instaも探す／IDは推測せず貼ってもらう
- [毎ターン届くMDは丸ごと書かない](feedback_memory_index_hygiene.md) — 00_Systemも1行ずつEdit（全文書き戻しで同期と衝突し03が壊れた）
- [AIが検証できない所に人の手を置かない](feedback_dont_put_hands_where_ai_cannot_verify.md) — 人に打たせる前にダミーで同じ道を通す
- [判断はSlackのボタン](project_ask_hub_push_decisions.md) — 10/14フックで届く。★「押されるまで待つ」で終えず戻る時刻を決める(10/15)
- [問いを出したら待ち役を走らせる](project_ask_hub_push_decisions.md) — ★ask後は同じターンで待ち役を走らせる
- [Slackの窓口はビビ・ビビは動かない](project_slack_command_center.md) — ★受けるのはビビ。受領と担当と目安を返して流す。作業は担当
- [Slackは1件1スレッド](project_slack_command_center.md) — ★有璽氏がスレッドへ返した発言も拾う。返事も同じスレッドへ
- [Slackの件をClaude Codeで続ける](project_slack_command_center.md) — ★受付番号で呼ぶ。流れを読み、同じスレッドへ書き戻せる
- [成果物はパスで返さない](feedback_cannot_copy_from_terminal.md) — ★画像はDriveへ置きFinderで開いて表示する
- [離席を告げられたらSlackへ](reference_slack_notification_rules.md) — 以降の進捗は notify.tell()。会話に書いても届かない
- [人に頼む前に自分の道具](feedback_check_your_own_tools_before_asking_a_human.md) — ListAgents/SendMessageを先に。往復3回超は減らす
- [セッション間に自動の橋は無い](reference_two_sessions_built_the_same_thing.md) — 人の手で渡すものは「渡すのは有璽氏の手」と書く
- [社外へ出す資料](feedback_confidential_two_layer_rule.md) — 機微は正規表現で0件に／★やりたいこと→理由→現在地で書く
- [読めないPDFがある](reference_md_to_pdf_docx.md) — 他社作のPDFは★3回で止め、画像か元ファイルをもらう
- [商談スカウターと台帳](project_sales_minutes_integration.md) — 欲しい紹介はNotion顧客DBに項目あり(3/506)。サイトと台帳は別の軸
- [引き継ぎ書はzipの中のことも](reference_handoff_inside_claude_design_zip.md) — ★findもmdfindもzip内を見ない。日本語名はdittoで展開
- [他言語文字の混入](reference_unicode_escape_kanji_swap.md) — カタカナ語の1字目が化ける。台帳へ書く直前に非ASCIIを数える
- [鍵の扱い](reference_plaintext_credentials_handling.md) — 人が入れる／AIは読めない。★Drive直下のclient_secretは有璽氏判断で現状維持(10/14)
- [器のコピーはフォームも増やす](reference_sheet_backup_breeds_form_copies.md) — ★フォーム付きの器は複製しない。退避はsnapshot()
- [Downloadsは片付け箱だけ自動](project_downloads_archive_system.md) — ★10/28 デスクトップの片付け箱の中だけ毎朝移す。直下は触らない
- [ドライブの置き場](reference_drive_placement_rules.md) — ★2段。一旦マイドライブの部門軸→共有と決めたものだけ共有ドライブ
- [補助金はどの部門か](reference_drive_placement_rules.md) — ★中身を直す人で4区分。迷ったら顧客が申請者の側
- [名前と日付の付け方](reference_drive_placement_rules.md) — ★日付は実際の作成日（整理日でない）／★中身を見てから名前を付ける(10/14)
- [2つの版の正は日付と中身で](reference_drive_placement_rules.md) — ★「共有で作業中」は新しさの根拠でない。更新日時で比べる
- [機微の線は不利益の有無](feedback_confidential_two_layer_rule.md) — ★個人情報かでなく、外へ出て誰が困るかで決める
- [検知≠隔離](feedback_confidential_two_layer_rule.md) — ★機微は置き場を実物で数える。10/15 理由文に出すだけで3件素通りしていた
- [★外出先ではminiに届かない](project_macmini_remote_workhorse.md) — 10/10 .localもIPも同じLAN内だけ。まず自分の網を見る
- [Mac mini作業機](project_macmini_remote_workhorse.md) — ssh mini＝Tailscale経由(10/11〜外でも届く)。家LAN用は mini-lan
- [Obsidian⇄Notionが止まったらminiを疑う](project_macmini_remote_workhorse.md) — ★同期はminiで動く。再起動後のロックで全部止まる
- [稼働盤は一旦停止中](project_ops_dashboard.md) — ★10/27有璽氏。mini cronの該当行を停止中。再開は外すだけ・戻さない
- [miniの実行環境](reference_mac_mini_execution_env.md) — ★claude -pは対話用フックを子に引き継ぐ＝判定が黙って死ぬ。10/15 両機で隔離済み
- [時刻はゼロ埋め](reference_hand_built_timestamp_zero_pad.md) — 4:28:50 を fromisoformat は読めない。10/20 読む側を直した・書き手は未特定
- [シェルは全角の直前で落ちる](reference_shell_fullwidth_paren_breaks_var.md) — 変数は${VAR}。★埋め込みPythonは取り出してpy_compile
- [Obsidian Core_Brainが動的正本](project_obsidian_core_brain.md) — 00_Systemを毎ターン@import／10_Skills_RepositoryはSync対象外
- [ツールの使い分け](project_tool_roles_and_adoption.md) — Obsidian=机・Notion=本棚。★有璽氏が普段見るのはObsidian（10/8）
- [Current_Focus⇄Notion同期](project_notion_focus_sync.md) — 10/8〜2枚・15分毎。同じ目印2組が10/20も警告中＝02で片方の目印を消すのは有璽氏
- [[x]が消えない＝目印の重複](project_notion_focus_sync.md) — ★同期が同名の新行へ既存の目印を付けていた。10/27修正・両行凍結
- [仮称を識別子に入れない](reference_provisional_name_isolate_identifiers.md) — 識別子は役割で付ける。置換は数えてから
- [インスタのハイライトカバー](reference_instagram_highlight_cover.md) — ★縁の丸を画像の幅いっぱいに。縁は消さない
- [インスタは毎回確認](feedback_ask_instagram_each_time.md) — 法人問わずレポートごとに「作るか／投稿までか」を聞く
- [HUGの本日の様子](reference_hug_record_output.md) — ★受け取り→専用スクリプト。正本は00_System/19
- [Workspaceのagentic](reference_workspace_agentic_oauth.md) — 11/11期限の通知は影響なし。既存クライアントに印を付けない(10/13決定)
- [さくらはログインで鯖が替わる](feedback_sakura_cp_switches_server.md) — 書く前に初期ドメインで確認（10/13 団体側へ誤追加）
