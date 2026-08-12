---
name: project-cfo-agent
description: CFOエージェント「ナミ」(ふくち。グループ)一式の構成 — 呼び出し型サブエージェント + Notion財務ハブ + 月次/週次の定期実行
metadata: 
  node_type: memory
  type: project
  originSessionId: 91717c3b-21ec-44e9-a0c9-fabfd6b8a69e
---

CFOエージェントは **「ナミ(CFO)」**。ふくち。グループの最高財務責任者(担当 y_tam@vivid-global.com)。名前は ONE PIECE の航海士ナミに由来(命名体系 [[project-agent-naming]])。お金にシビアで数字に強い口調、一人称「ナミ」。担当業務(優先度順): 予実管理 > KPIトラッキング > 資金繰り/キャッシュフロー > 財務レポート > 請求/入金/支払い管理。2026-07-02 構築。

**構成部品**
1. **呼び出し型サブエージェント**: `~/.claude/agents/cfo.md`(name: `cfo`)。「ナミに〜して」で呼び出し。数値は捏造しない・支払実行等の外部影響操作は事前承認、が原則。
2. **Notion財務ハブ**「💰 ナミ(CFO)財務室」(親ページ id `3917b156-8b57-8100-8c0f-ddadd0fee20b`)。配下に3DB:
   - 予実管理DB: `collection://0af67e7d-6604-4dbc-9368-0abf35c369dc`(科目/区分/年月/予算/実績/差異)
   - KPI DB: `collection://538f966f-0998-4e76-8de1-a1cd422ba78b`(指標名/区分/年月/実績値/目標値/達成率/単位)
   - 資金繰りDB: `collection://b4a402d9-42e8-426e-bf44-959e3bfbff4c`(期間/種別/現預金残高/入金予定/出金予定/純増減)
   - レポート置き場ページ: 月次サマリー `3917b156-8b57-819b-b9cc-d3f2c9d290c7` / 週次チェック `3917b156-8b57-811c-899a-c70cdc2ff8eb`
3. **定期実行(cloud routine, env `env_019JEywc7vB9TF9FA8cpuZAo`, sonnet-5, 接続 Notion+Gmail)**:
   - 月次財務サマリー: `trig_01TKZyjJVXkLHR4eQzP8fVx6`、毎月1日 9:00 JST(cron `0 0 1 * *`)、月次サマリーページに追記。
   - 週次 資金繰り・KPIチェック: `trig_0199EjbEmzJZQcWFBggt8eD2`、毎週月曜 9:00 JST(cron `0 0 * * 1`)、週次チェックページに追記。

**未了 / 次のステップ**: 3DBはまだ空。数値の投入が必要(会計ソフト未決)。会計ソフトへの入力自動化(freee/MFのAPI・OCR・銀行連携・iPaaS等)は使用ソフト確定後に着手予定。使う会計ソフトと中間ハブ(Notion採用済)は要確定。
