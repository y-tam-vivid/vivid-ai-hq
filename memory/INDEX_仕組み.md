# 仕組み ── 分野索引

**cron・同期・監視・GAS・シェル・議事録の自動処理**

> この分野の作業に着手したら読む。正本は各ファイルの本文。ここは索引。
> **上限は無い。** 毎ターン届く `MEMORY.md` と違い、必要なときだけ読まれる。
> 呼び出しの対応は [[INDEX_担当別]] にある。

- [SIGTERMでは後始末が走らない](project_lifestandup_website_wordpress.md) — ★try/finally・atexitはSIGTERMで飛ぶ。signal.signalで捕まえる／Chromeの--dump-domは返らないことがある。--screenshotへ寄せる
- [Downloads→Drive本棚](project_downloads_archive_system.md) — 受け皿17分類。sort_downloads.pyが週次(要フルディスクアクセス)
- [カレンダー テンプレ挿入](project_calendar_template_autofill.md) — GASで自動挿入。タイトル【種別】で振り分け＝命名ルールが前提
- [git add -A は飲み込む](reference_git_add_all_swallows_others.md) — 他体の書きかけが混入する。触ったファイルを明示・commitは束ねる側が打つ
- [同期は作業中だけ黙って止まる](reference_silent_sync_failure.md) — cronから`git pull --ff-only`を直呼びしない／★枝分かれはff-onlyでは永久に解けない（自動merge＋衝突ならabort）
- [直した所は配られるか](reference_fix_where_git_reaches.md) — ★自動配布にした結果、逆に`~/.vivid-relay/`を直すと15分後に黙って巻き戻る。触る前に`bin/hooks/`に同名が無いか見る
- [crontabは書けない](reference_cron_write_blocked_in_session.md) — ★日次ジョブの正本はbin/daily_jobs.conf。8/23も未解消／ssh越しなら書ける
- [launchdでファイル権限が消える](reference_launchd_loses_file_access.md) — TCCは起動元で判定。移す前にlaunchd経由でdry-runを1回
- [ブラウザ衛生の週次チェック](project_browser_hygiene_check.md) — 拡張は型で見る。毎週月曜09:30(MacBook)。慢性的な黄色を出さない
- [止めてあるものを混ぜない](reference_monitor_must_exclude_parked.md) — 警告≠異常。止めてある/保留/★直った は除く／**★検査役2体が違う数字を出したら分類の基準が違う。真因はレジスタの「有効」フラグが実態と合っていないこと(2026-08-23)**／**★心拍の宛先は行名の文字列一致。相乗り・beat無しで、動いているのに永久に🟡になる(8/27に2件)**／**★8/28 heartbeat_names_check の5件中4件が誤検知だった（PROC_NAME固定・行末コメント・自前beatラッパ）。修正済。同じ穴を4回踏んでいる＝次は正規表現を足さずastか自己申告へ**／**★「有効」フラグのズレは2回目。今回は常駐(Slack Socket Mode)で、人が手で起動した後もレジスタが2日間 有効=False＝永久に🔴が立たない状態だった。起動と登録は1セット**／**★9/1 毎朝の材料「ログの失敗N件」の中身を初実測＝10件中6件がSlackの正常なdisconnect。「異常でない」と別memoryで判定済みなのに self_audit.py がそれを読まないため12日間鳴り続けている。件数は tail -25 の窓で動くので増減も指標にならない。直すのはピタゴラス**
- [判断待ちは配布を止めない](reference_pending_decision_does_not_pause_the_pipeline.md) — ★9/1 intake_notifyが「人の目視を挟むか判断待ち」の最中にSlackへ本番投稿5件。文書の保留を機械は読まない／★レジスタの有効=Falseは実行を止めない(監視の対象外にするだけ)。止めるならdaily_jobs.confの行を止める
- [無言の失敗](reference_silent_failure_kills_adoption.md) — 失敗時こそ返す＋逃げ道。★押下は受け側にログ無し(launchd未load)＝届いたか不明
- [「動いた」と「成功した」は別](reference_ran_is_not_succeeded.md) — 常駐は一定間隔で心拍／心拍はmain()の外で包む。末尾は例外が素通り
- [記録は出口を数える](reference_log_needs_an_exit.md) — 器を作ったら出口を書き出す／★入口を直す依頼が来たら先にその列の出口を数える。受付シート「連絡が取れる手段」は台帳へ移送されない孤立列だった(2026-08-24)／**★手順書に「まだ無い機能」を書いた。決着済みの設計を在るものとして扱った。人が読む文書の前に動線を1回自分で通す(2026-08-24)**
- [稼働ダッシュボード](project_ops_dashboard.md) — AI稼働を1枚に。★古さを頁が名乗る／定期生成は未登録
- [自動処理レジスタ(心拍)](project_automation_register.md) — ★心拍名は1文字違うと黙って失敗／★miniのlaunchdは0本＝plistが在るのは常駐の証拠でない／★法人番号月次更新を新設(0827)。9/1初回目視待ち
- [議事録→顧客relation付与](project_meeting_customer_relation_linker.md) — mini cron 07:35で稼働。自社5社は除外。残115件は多くが顧客でない
- [フォルダ分類は誤答を強制する](reference_folder_classification_forces_wrong_answers.md) — 1つしか選べない置き場に判断を置かない。3割超の偏りは既定値と疑う
- [入力と出力先を先に見る](reference_ai_output_blamed_before_inputs.md) — ★フォールバックは工程ごとに散る(議事録で7個)。1本直しても潰れない
- [印を消すだけでは戻らない](reference_processed_flag_is_not_enough.md) — 元データが取得元にあるかを見る／隔離配下は対象外にする
- [却下は永続的な取りこぼし](reference_silent_rejection_backlog.md) — 却下=処理済み扱いで二度と拾われない。連続0件の日で探す
- [議事録自動整理GAS](project_giji_automation_gas.md) — 復旧済・空白解消済。オーナー区分ルーティングは設計中でバックログ停止
- [議事録の社員展開](project_minutes_employee_rollout.md) — パイロット5名で入口を開いた。全社への自動昇格は意図的に未実装
- [議事録の隔離運用](project_minutes_quarantine.md) — 空・機微・重複はDrive`_要確認`へ移す。移動のみ・削除は有璽氏
- [議事録の整理ルール](project_giji_organizing_rules.md) — 区分は台帳が持つ／表記は台帳と同じ／指標は社外会議の紐付率
- [Apps ScriptのAPI突合](reference_apps_script_api_verification.md) — node --checkは存在しないメソッドを見逃す。所属クラスの突合が必須
- [検査が偽陰性を出す](reference_reference_audit_false_negative.md) — 定数経由の参照を落とし13本を1本と誤判定／**★「0件」は「見た範囲に異常が無い」。自動処理の突合はcron/daily_jobsしか見ずlaunchd・手動実行を落とし、翌日2件出た(2026-08-24)。実行の経路は4つ**
- [見つけた≠失敗した](reference_finding_is_not_failing.md) — ★memory_audit.pyがズレ検出でrc=1→daily_jobs.shが恒久エラー誤判定・5枠即諦め＋誤通知(8/25)。8/26に常時0へ修正済。所見は心拍で伝える
- [同名定義は後勝ち](reference_apps_script_name_collision.md) — 新版を貼っても旧版が動き混在する。`関数名.toString()`で実体を読む
- [Drive上の.gsは開けない](reference_drive_gs_file_not_previewable.md) — octet-stream固定。Googleドキュメントとして作り直す
- [本数で切ると希少な版が消える](reference_retention_by_count_deletes_the_wrong_ones.md) — 残す単位は日ごと最新1本
- [リレーは積み上がる](reference_relay_piles_up_and_blames_the_user.md) — 周期より長い処理はロック必須。「読んだ」の確定は実行の前
- [bash3.2は全角直後で落ちる](reference_bash32_multibyte_unbound_var.md) — `${var}`で必ず区切る。新規シェルスクリプトは毎回grepで検査
- [Slack通知の作法](reference_slack_notification_rules.md) — 宛先/手段/条件/書式を1枚に集約(9/3新設・従来3箇所に散在)。**★経路は2つ＝報告tell()／判断ask()。ask()は1回1件・tell()は「返信不要」を自動付与**／DM`D0AT4NQ6X7D`固定・チャンネル禁止／検査は`VIVID_NOTIFY_OFF=1`必須(過去に本物へ8件誤送信)／有璽氏はコピー不可なのでlink=で渡す／**🔴金額はSlackに書かずNotionリンクへ＝当方の導出で承認未取得。確認はビビが実施・結果待ち**
- [Slackから動かす経路](reference_slack_tokens_and_socket_mode.md) — ★8/25からSocket Mode常駐(launchd)。人の承認3件が台帳へ通った／**形式外value(UUID)は9日目・累計31回(8/25=1 8/26=13 8/27=3 8/28=7 8/29=0 8/30=0 8/31=1 9/1=6)。押した人にエラーが返り続けている＝別アプリのボタン。★0が2日続いたのは直ったからでなく誰も押さなかっただけ。★8/29に書いた「次に読んだ人がapi_app_idをログへ出す」は grep実測0件＝入っていない。担当を名指しした＝ピタゴラス／検査ステラ**／貼った鍵のlog平文は未revoke／**★scopeは「足してSave」では効かない。再インストールまでが1セット。実測は auth.test の x-oauth-scopes ヘッダ(本文には出ない)**
- [バックオフのリセットが早すぎる](reference_retry_backoff_resets_too_early.md) — ★9/2 Socket Modeが19秒で9回再接続(8回 too_many_websockets)。原因はSlackでなくこちら＝1秒で張り直すので古いソケットが生きたまま数えられる。`backoff=1`が「ソケットが開いた時点」でリセットされ指数バックオフが一度も効かない。**見るのは切断の件数でなく「秒数が増えているか」。同じ数字が3つ並べば黒**。★9/2 08:43 修正済(hello受信時にリセットへ移動・ステラ検査済)。**★9/3 07:50 自然発生で検証完了＝1→2→…→300と正しく伸びた。だが断絶は9秒→23分41秒へ悪化し24分間ボタンが死んだ（心拍は緑のまま）。「速すぎる再接続が原因」の仮説は支持されず。上限300秒は復旧の遅さの下限でもある。残＝上限見直し/jitter/連続失敗の警報の3点、まだ誰にも投げていない**
- [md→Word変換](reference_md_to_docx.md) — bin/md2docx.py。★pandoc/LibreOfficeは無い。python-docxを両機へ導入済／変換後は読み返して数える
- [銀行明細CSVの形3種](reference_bank_csv_formats.md) — 楽天個人4列/りそな21列(★日付2種混在)/楽天法人=全銀協20列。裏取りはトレーラー件数／平成は自動判別できない
- [日本語ファイル名はNFD](reference_japanese_filename_normalization.md) — macOSのファイル名はNFD。NFC文字列でgrep/in判定すると静かに0件になる。★担当の申告と検算が食い違ったら、まず検算側を疑う（両機のフォント在庫も実測記載）
- [fresh eyes 2パス方式](reference_fresh_eyes_two_pass.md) — 検問インフラ限定。★8/29初実演＝A疑義10件→Bで消えたのは2件(実測で消した)・Bで新規1件。Aが0件でもBを省かない／依頼文で型を指定しないと使われない
