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

- [Language: Japanese](feedback_language_japanese.md) — 応答は常に日本語
- [呼称は「有璽」「有璽氏」](feedback_naming_yuji.md) — 「本人/田村さん」不可／制作物も既存物も自動で正としない
- [モデル使い分け](feedback_model_usage_rule.md) — Sonnet標準/Opus難所/Fable封印。適するモデルは能動的に推奨
- [測っていない数字を書かない](feedback_never_write_an_unmeasured_number.md) — 件数は数え方を添える／担当へ渡す数字も測ってから
- [1経路で断定するな](feedback_one_route_is_not_verification.md) — 出どころの違う2経路で。自分の警告・自分が書いた印を事実と取り違えない
- [相手の資料は全部読む](feedback_source_material_is_not_the_pr_plan.md) — grep等の部分読みは読んだことにならない（10/8 約束を2つ破った）
- [フェーズを確かめる](feedback_ask_which_phase.md) — 着手前に「どの段階の話か」を1問。できない理由がどの段階の条件かも
- [読む人に合わせて書く](feedback_write_for_the_reader.md) — 相手の文を返さない。運用の変化と崩れた前提だけ返す
- [音声入力の人名・日付](feedback_voice_input_name_kanji.md) — 人名は別の出どころの表記を正に。登録した字と日付を返事で示す
- [次の一手と有璽氏の作業](feedback_emit_next_actions_as_tasks.md) — 返答末尾に「★有璽氏がすること」節／頼む行は03へ区分付き(10/8〜)
- [押す場所は位置と結果まで](feedback_verify_before_declining.md) — 押す場所・結果・確認ダイアログまで。人の手は1つ・コマンド1行
- [着手時に目安時刻を伝える](feedback_batch_the_checks.md) — 何をする＋完了目安／変われば言い直す／その時刻に自分で見る
- [AIが検証できない所に人の手を置かない](feedback_dont_put_hands_where_ai_cannot_verify.md) — 人に打たせる前にダミーで同じ道を通す
- [判断はSlackのボタン](project_ask_hub_push_decisions.md) — 終わる前にopen・answeredを数えfree_textまで読む／選択肢の数字を揃える
- [離席を告げられたらSlackへ](reference_slack_notification_rules.md) — 以降の進捗は notify.tell()。会話に書いても届かない
- [人に頼む前に自分の道具](feedback_check_your_own_tools_before_asking_a_human.md) — ListAgents/SendMessageを先に。往復3回超は減らす
- [セッション間に自動の橋は無い](reference_two_sessions_built_the_same_thing.md) — 人の手で渡すものは「渡すのは有璽氏の手」と書く
- [他言語文字の混入](reference_unicode_escape_kanji_swap.md) — カタカナ語の1字目が化ける。台帳へ書く直前に非ASCIIを数える
- [鍵の扱い](reference_plaintext_credentials_handling.md) — 値は人が入れる・聞かない／macOSキーチェーン＋-A／AIは鍵を読めない
- [Mac mini作業機](project_macmini_remote_workhorse.md) — ssh mini。切れたら先に自分の網を見る／投げる指示文に notify.tell
- [miniの実行環境](reference_mac_mini_execution_env.md) — cron/launchdは環境変数なし＝スクリプトがconfig.envを自分で読む
- [シェルは全角の直前で落ちる](reference_shell_fullwidth_paren_breaks_var.md) — 日本語中の変数は${VAR}。bash -nでは見つからない
- [Obsidian Core_Brainが動的正本](project_obsidian_core_brain.md) — 00_Systemを毎ターン@import／10_Skills_RepositoryはSync対象外
- [ツールの使い分け](project_tool_roles_and_adoption.md) — Obsidian=机・Notion=本棚。★有璽氏が普段見るのはObsidian（10/8）
- [Current_Focus⇄Notion同期](project_notion_focus_sync.md) — launchd15分ごと稼働。行を複製する時は目印を消す
- [仮称を識別子に入れない](reference_provisional_name_isolate_identifiers.md) — 識別子は役割で付ける。置換は数えてから
