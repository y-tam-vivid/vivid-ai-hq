# 営業 ── 分野索引

**営業・顧客台帳・kintone・名刺**

> この分野の作業に着手したら読む。正本は各ファイルの本文。ここは索引。
> **上限は無い。** 毎ターン届く `MEMORY.md` と違い、必要なときだけ読まれる。
> 呼び出しの対応は [[INDEX_担当別]] にある。

- [IG DM営業リスト](project_ig_dm_sales_lists.md) — 119番(大阪→東京・児童/就労)とゲームブル(全国)。★多店舗・FCが効く／DMは1日数十件が上限＝件数はそこから逆算
- [大きなSheetsはgviz経由](reference_gviz_large_sheet_access.md) — ★gvizは黙って嘘をつく。数値状文字列はCSV出力で読む
- [kintoneは行番号≠レコード番号](reference_kintone_subtable_rows.md) — サブテーブル継続行を数えないと行参照が全部ズレる。エラーは出ない
- [toC顧客台帳](project_toc_customer_ledger.md) — Notion完結。個人顧客マスター＋提案商談。将来=人物マスター中心
- [法人番号は申請不要で取れる](reference_corp_number_bulk_download.md) — 全件DLは申請なしで今日から使える。Web-API IDだけが2週間〜1か月
- [台帳掃除は価値判定してから](reference_ledger_cleanup_triage.md) — ★8/31の削除で14→21組へ増えた(備考の決着が消え01に行が残る)／**★9/5 有璽氏の決定4件＝①毎朝の督促は期限なし保留(実装済) ②01からも3行消す(★AI推奨と逆・差分だけ出して未実行) ③顧客種別はAIの判断で変えてよい ④受付41行目は中身を全部見せてから(#8330f0で再提示)**／**★引き継ぎ書の「削除後14組」は誤り。実測9組（B-0008の7組しか引いていなかった。3ID同時なら12組消える）**／**★法人番号空59件の内訳＝個人(事業主)へ変える候補14／判断つかず40／機械で番号を確定できる5。★corp_number_fillの「確定16件」は別の母数(59件プールに入るのは5件だけ)**
- [あいまい照合の設計](reference_fuzzy_match_design.md) — ★1文字違いは距離であって類似ではない(直/正で別人を結合)。誤りの実例で試す／キーは複数持つ
- [法人番号の真因は社名欄](reference_ledger_name_blocks_corp_match.md) — 施設名同居/誤記/連結で突合が死ぬ。★絞り込みと適格性検査を混ぜない
- [指数表記は計算で戻さない](reference_recover_exponential_corp_number.md) — toFixedでの復元は禁止。全件データで1社に絞れたときだけ確定
- [kintoneルックアップはコピー](reference_kintone_lookup_is_a_copy.md) — マスタ更新→参照アプリで取り直しまでが1作業
- [空行が汚れる2経路](reference_sheet_scan_range_pollution.md) — 書式継承と走査範囲。件数は「会社名がある行」で数える
- [チェックボックス書式の侵食](reference_sheets_checkbox_format_creep.md) — 空行のfalseは後から行が入るとキーを壊す。CSVはキーの形を検査
- [レコード統合の手順](reference_record_merge_protocol.md) — 全列突合→移送→集計列を空に→削除。廃止選択肢は上書きで始末
- [ベタ書きの選択肢は腐る](reference_hardcoded_option_lists.md) — 書き込み系5本がマスタを巻き戻す／★手段の語彙は3箇所に散る(フォーム/90のK列/Notionチャネル)。90に連絡手段の列は無い
- [\uエスケープで漢字が化ける](reference_unicode_escape_kanji_swap.md) — 日本語はliteralで書き、書いた後に1文字ずつ突合する
- [営業×議事録の統合設計](project_sales_minutes_integration.md) — **2026-08-22 全論点に回答済。結合キー=社内顧客ID／全社昇格分だけ営業へ見せる**
- [他種別テレアポリスト](project_telapo_list_other_services.md) — ★載せてよい。3,495社/7,646事業所。9/6に🟡2件を解消（数字・I/J矛盾0行）。🔴残＝ＨＡＬＥの番号（有璽氏の判断）
- [架電前に台帳と突き合わせる](reference_call_list_must_be_matched_against_ledger.md) — ★外部リストは架ける前に00と突合。掃除の価値は用途で変わる（突合に使うなら空欄は見逃しに直結）
- [行番号の参照は組み直しで腐る](reference_row_reference_rots_on_rebuild.md) — 一覧は法人番号で指す／★9/6 2回目=照合を正規化すると人がCtrl+Fで当てられない。合否は厳密一致で数える
- [見本の複製に前案件の実績が残る](reference_sample_copy_keeps_past_results.md) — 数式が値に焼き付く。複製した器はread_formulas()で1回開く
- [新リスト前に墓場を探す](reference_new_list_splits_judgment.md) — 「反映」を挟むと判断が2箇所に増える。06_テレアポリストがその死体／**★9/5 続報＝器を1つにしたのに移行先が空だった（09⑤=0件・40活動ログのTEL=0件）。現場は元の見本ファイルへ書いていた。決定は行数で確かめる**
- [営業案件管理](project_sales_workbook_read_first.md) — ★SWELL統合は8/3にB-0380側で決着済(逆転指示は保留)／機械が新規判定して書かない
- [台帳作業の認証](reference_sheets_no_credentials_on_mini.md) — ★認証は有璽氏本人のOAuth(サービスアカウントでない)＝作った物は共有不要／共有ドライブはsupportsAllDrives必須
- [営業ワークブックは戻せる状態に](feedback_sales_workbook_hands_off.md) — AIが書くときだけ①BU→②diff→③承認→④実行
- [営業ワークブック](project_sales_pipeline_workbook.md) — ★営業は一度も触っていない＝開かせる1回が要る／投稿側intake_notify.pyは未実行
- [SalesBreaker API](reference_salesbreaker_engagement_api.md) — ★2026-08-28 contract=turn82。list/get系は403。中身を読めるのは templates/preview と saved-lists/preview だけ
- [営業ワークブックは列移動可](reference_sales_workbook_column_moves.md) — 全GASが見出し名で引く。受付シートは例外／apply_schema_v3は実行禁止
- [kintone CSV取り込みの地雷](reference_kintone_csv_import_landmines.md) — 更新キーは「3.」／ユーザーはログイン名／書き出しはUTF-8／必ず突合
- [施設と運営法人はずれる](reference_facility_vs_corporation.md) — 営業先は施設・番号は運営法人。複数施設で番号が重複しうる(kintone側は未確認)
- [kintone顧客マスター](reference_kintone_customer_master.md) — 顧客の正本。Notion顧客DBは中間ミラー(鍵=法人番号)。機微はkintone留置
- [名刺→kintone](project_meishi_to_kintone_pipeline.md) — ★取得元フォルダは既に在る(受付フォーム自動生成・0件)。残はバッチ本体
- [コミュニケーションログ基盤](project_communication_log_hub.md) — 📨ログDBへ格納し相互リンク。★逆向き(会社→過去の会話)は辿れない
- [顧客ファイルのDrive格納先](feedback_customer_files_drive_location.md) — 財務(03)でなく取引先・人物別(11)へ
- [kintone CSV→Notionミラー](project_kintone_csv_to_notion_mirror.md) — 地雷=指数表記/継続行/cp932化け→作成後にSELECT突合で検証
- [Sheets書き込みの暗黙挙動11点](reference_sheets_number_format_order.md) — 器を増やしても保護・入力規則は付いてこない
- [GameBull×SalesBreaker](project_gamebull_form_sales.md) — 第1波13,709件済→★訴求Aで確定。第2波3,121件(フォーム有)は送信待ち／LPに1行タグ設置済
- [受付確認をSlack返信で受ける](project_intake_slack_reply.md) — 氏名/IDで解決。★返信経路は8/26 16:20実測OK。**書き先はZ列直書き（Y列分離は廃止）／修正後のボタン押下は0件＝未検証**／**🔴9/3発見＝「ボタンの中身が読めませんでした」が33回。valueが裸UUIDで我々のコードは出していない（送信元未特定・押した人には毎回失敗が返っている）**
- [LPの計測タグ](reference_lp_tracking_tags.md) — gamemarke に SB/GTM/GA4/Clarity の4本。★ログイン不要で発火を確定させる3手
- [SB送信前の必須3点](reference_salesbreaker_campaign_setup.md) — ★全案件必須。タグ4本+パス/UTMで経路分離+.md封鎖。送信後は取り返せない
