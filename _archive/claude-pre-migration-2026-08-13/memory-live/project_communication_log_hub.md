---
name: project_communication_log_hub
description: LINE/Messenger/メール等のやり取りを📨コミュニケーションログDBへ格納し顧客DB/kintone/議事録と相互リンクする基盤
metadata: 
  node_type: memory
  type: project
  originSessionId: 41edb8f6-2705-4dac-93d0-901e01d25136
---

顧客との**LINE/Messenger/メール等のやり取りログ**を後追いできる基盤。Notionに**📨コミュニケーションログDB**（1スレッド=1レコード）を新設し、相手を🏢顧客DBへRelation、kintone顧客レコードには本ページURLを貼って相互リンク。商談/面談の議事録も同思想で🌐全社議事録DBへ（ログDBと議事録DBは分離、両者を🏢顧客DBにRelation）。2026-07-17にくりはら工業でパイロット→松本共有フォルダA/B(LINE4本+Messenger3本=計7スレッド)を反映。

**DB**：`collection://1d129663-73c1-4979-9e18-1624a6f0d459`（page 064bca88cff64955bfe282ee4fc2a8e4、親=ビビッド業務管理）。DUAL relationで🏢顧客DB(f506787d…)・👤担当者マスター(49f65ba4…)・🌐議事録DB(a6599740…)に「コミュニケーションログ」逆プロパティが付き各DBから逆引き可。スキーマ・手順は**スキル`customer-db-sync`に④入口＋専用節として統合済**（[[project_kintone_csv_to_notion_mirror]]／targets.md）。どのタブのClaudeでもスキル起動で同じ処理ができる。

**運用の要点**：
- ログ本文＝📌最新サマリ(日付・最上部)→🧭経緯タイムライン→💬主要往復。**原ログ全文はDrive原本**(`…/11_取引先・人物別/コミュニケーションログ原本/`・md5照合)で保管、Notionへ逐語転記しない(長文＋化け源)。Messengerのhtmlはpythonでタグ除去し抽出。
- **kintone相互リンク**：kintoneに「NotionログURL」列を1つ追加(松本の初回設定)し、`法人番号,会社名,チャネル,NotionログURL`のCSVを法人番号キーで更新取込＝手貼りゼロ。法人番号なし(個人事務所/NPO/個人)は会社名で手動照合。逆方向はkintoneの法人番号＋レコードURLをもらいNotionの空`kintoneレコードURL`列を一括反映。対応表CSV(7スレッド)は `11_取引先・人物別/顧客情報kintone反映csv/kintone_NotionログURL対応表_20260717.csv`。
- **人材/除外**：複業・紹介人材は`種別=人材`で顧客DBへ(所属先企業は顧客化しない)。**自社の業務委託者は顧客DBに含めない**(例:野本修平)。
- 設計・作業ログの継続ハブ＝⑥ディスカッションログDB『📨コミュニケーションログ基盤の設計・構築』(page 3a07b156-8b57-8182-96ec-e8586ead4207)。

**営業セルフ運用化(2026-07-20)**：この反映オペを営業(松本筆頭)が楽に依頼できるよう、Notion『🧭 営業オペレーション・ハブ』(page 3a37b1568b5781ab88e3de9f73ab4a37／ビビッド業務管理配下)を作成。Part1=反映依頼マニュアル(営業は「Driveにフォルダ命名規約で置く→『顧客DB反映して』の2ステップ」だけ)、Part2=営業定例(確定:対象=ビビッド営業チーム/KPI=活動量中心/週次＋月次定例/記録・準備・集計は最大限Claude・ビビへ)。⑥に設計スレッド『🧭 営業オペレーション設計』(page 3a37b1568b5781139a36eda2cd71dd8a)。
