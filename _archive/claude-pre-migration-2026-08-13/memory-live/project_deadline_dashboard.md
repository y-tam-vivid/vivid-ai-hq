---
name: project_deadline_dashboard
description: 締切ダッシュボード=タスク+法務期日を🚦信号で横断把握、ビビ朝ブリーフィングに集約
metadata: 
  node_type: memory
  type: project
  originSessionId: 1d73b6d9-e954-4b58-94e8-3640388031c9
---

期日を一覧で把握する仕組み(2026-07-17構築)。UIに埋もれる期日を🔴🟡🟢信号で可視化。

**ハブ**: 📆締切ダッシュボードpage `3a07b156-8b57-811a-9992-ca6856fd9de4`(親=ビビッド業務管理)。

**ソース2系統**:
- ①**ビビッドタスク管理DB**(全社) `collection://62c7fadf-3fb1-409d-bc90-238fdce29b0f`(Due Dateベース)。議事録の決定/宿題/次回アクションはこのDBに起票される→議事録フォローもここに含まれる。
- ②**法務・期日管理DB**(センゴク法務室) `collection://498d4f2e-b8c4-4522-bbbc-8fbbd6a85a5d`(次回アクション期日・解約通知期限)。契約の自動更新/解約通知。

**両DBに`🚦信号`Formula列を追加済**(空期日は空欄・now()基準で自動更新)。信号ルール=🔴超過or残り3日以内(今すぐ)/🟡4〜7日(今週中)/🟢8日以上(通常)。=[[project_design_agent]]フランキーのデザインガイドライン標準に準拠。

**ビビ連携**: [[project_secretary_agent]]の毎朝ブリーフィングに両DBの🔴🟡を集約する運用をsecretary.mdに追記済。まず代表本人の把握用、将来は担当フィルタで各人向け「あなたの締切」配信へ拡張(契約=センゴク/入金支払=ナミへ橋渡し)。

**残**: (a)ビビの朝ブリーフィングroutine(cron)側の実装反映は未確認 (b)各人向け共有ビュー/通知は将来。締切ダッシュボードの前提だった移行本体は完了([[project_claude_ai_logs_to_notion_migration]])。
