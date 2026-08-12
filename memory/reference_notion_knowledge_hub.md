---
name: reference_notion_knowledge_hub
description: ビビッド業務管理Notionハブと組織マスター(Company×Division×Department)。全ナレッジ整理の整合性の基準
metadata: 
  node_type: memory
  type: reference
  originSessionId: a5c258b1-21a4-4d70-8a4d-916760150ede
---

ふくち。グループ／株式会社ビビッドのナレッジ整理は、Notion「**ビビッド業務管理**」ハブを正本の入口とする。ここに定義された**組織マスターが全整理の整合性の軸**（メモ・ファイル・タスク・エージェントを串刺しにするコード体系）。

- ハブ: **ビビッド業務管理** https://app.notion.com/p/35e7b1568b5781c391dbcc87f0ee6b1f
- 設計ドキュメント: **🗂️【設計】社内ナレッジ整理・一元化／ナレッジホーム設計**（2026-07-04, 叩き台v1）https://app.notion.com/p/3927b1568b5781e19b57d7da9bd0617c

**組織マスター（分類の背骨）**
- Company（所属法人）: `10ビビッド`（本体）/ `20ILIFE`（LIFE STAND UP運営）/ `30SWELL`（オレンジワークス藤井寺運営）/ `グループ横断`
  - ※`30` の法人現行名は **リアンライフ株式会社**（旧SWELLSOCIETY）。ただし **Notion select の実値は現状 `30SWELL` のまま**。実値とラベルを混同しないこと（[[reference_org_master_notion]]）。
- Division（部門）: 10経営企画 / 11事業開発 / 12マーケ / 13営業 / 14管理 / 15施設運営 / LSU / OW
- Department（5桁コード）: 例 13-100法人コンサル部, 13-200FPコンサル部, 14-200経理 等

**Notion正本アーキテクチャ（叩き台）**: 01会社情報 / 02部門・プロジェクト / 03議事録DB【統一】 / 04顧客管理DB【正マスター】 / 05月報DB / 06財務室(ナミCFO) / 07AI活用ログ / 09Archive。議事録は「🔒個人議事録DB → ✅全社へ共有 → 🌐全社議事録DB → ③タスクDB → ④担当者マスター」の昇格フロー。

**議事録DB群 新設完了（2026-07-12・ゼロベース再設計で構築）**: 前提が変わり「稼働中の自動化(notta→タスク)は詰まっており無視してゼロベースで」の方針で、手で回る背骨を新設。物理分離を採用（Notionは行権限が無いため機微保護はDB分離で引く）。作ったDB4本＝①**🔒個人議事録DB**(中間・一次受け/ワークスペース直下**非公開**, ds `816f0dd0-3633-4b1b-b173-6d220e25ef12`)＝全議事録の一次着地、「全社へ共有」✅で昇格 ②**🌐全社議事録DB**(ハブ配下・共有, `49e12c3d81ec495babbac5dc160dbfd6` / ds `a6599740-aafc-4907-b1fb-0f21a3be2586`)＝業務会議の正本、relation: タスク⇄元議事録・担当者⇄関連議事録・昇格元(個人)⇄全社版 ③**👤担当者マスターDB**(`7aaab919d05d4ad8bbfca4a6faa9dc9a` / ds `49f65ba4-9d4d-449f-8a6a-bb4efd038bd2`, 6名投入済) ④タスクは[[reference_notion_knowledge_hub]]記載の新✅ビビッドタスク管理DBを使用。往復リンク検証済。**旧notta v4.0**(GAS)は参考: Drive部門別振り分け＋旧DB_Vivid_Task/DB_Task二重登録は詰まり気味で今は非依存。旧叩き台スキーマ=https://app.notion.com/p/3987b1568b5781a09bffefce45435b60。顧客DBは [[reference_kintone_customer_master]]（正本kintone・Notionは索引・次タスク）。**次**: 顧客DB(kintoneミラー)設計／カレンダー命名ルール確定／個人議事録DBを確実に非公開設定確認。

**全社タスクDB刷新（2026-07-12）**: 旧DB_Vivid_Taskは組織コード軸が強いがタスク名が不明瞭で本格稼働前。柴田個人DB「📋タスク管理DB(SNS・自動化・営業)」(`6447870409814df99b788bbc1aa98a63`)の良さ=①命名ルール`【文脈(PJ/媒体)】具体的成果物・動作＋頻度` ②**次アクション欄**(物理的な次の一歩を1文) ③領域(機能軸5分類) ④きれいなStatus/Priority を高評価。→ **柴田DBは温存(個人用)し、その良さ＋ビビッド側の組織ロールアップ(Company/Dept/Project/関連定例)を結合した新DB「✅ビビッドタスク管理DB(全社)」を新設**＝https://app.notion.com/p/325c3683418247a8b78837c369c3a1c5 (ds `collection://62c7fadf-3fb1-409d-bc90-238fdce29b0f`)。ハブ配下・タスクID接頭辞VT。旧DB_Vivid_Taskは今後アーカイブ退避＋ハブ埋込差替え予定(未実施)。議事録DB新設後に「元議事録」relationを接続する。

**アクセス前提**: Claude CodeはNotion/Drive/Slack/Gmail(MCP)を読めるが、Claude.aiの「プロジェクト」機能のナレッジと**別タブのClaude Code会話は読めない**。整合はNotion等の共有ファイル経由で取る。

命名論点(未確定): ナレッジ統括CKO=ロビン、戦略CSO=ジンベエへ入替提案。関連 [[project_agent_naming]] [[project_local_memo_cleanup]]
