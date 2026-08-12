---
name: ai-asset-catalog
description: Claude製AI資産(Skill/GAS/MCP/主要MD)の台帳化と「AI資産_正本」による正本・バージョン管理
metadata: 
  node_type: memory
  type: project
  originSessionId: a52ff0f8-45e3-42e0-a28d-416c6e13fef0
---

田村さんのグループのClaude製AI資産(Skill・GASスクリプト・MCP・主要MDドキュメント)を台帳化して一元管理する仕組み。散在・バージョン乱立(例:`standup_calendar.gs`が4版同居、`議事録自動整理_GAS.js`v4が2箇所)が課題だった。関連:[[downloads-archive-system]]。

**正本の置き場所(2026-07-07決定・実装済)**：Drive `マイドライブ/AI資産_正本/`（`skills/`＝汎用Skill正本, `gas/`＝GAS書き出しBK, `_旧版/`, `_tools/inventory.py`）。**Driveが正本・`~/.claude/skills`は稼働コピー**。汎用Skill5件(downloads-weekly-sweep/riyousha-futan-pdf-splitter/sitemap-architect/standup-event-notion-importer/prompt-architect)を正本化済み。プロジェクト付属Skill(hojokin-agentのsubsidy系5件)は各プロジェクトの`.claude/`が正本。運用ルールは `AI資産_正本/README.md`。

**バージョン方針**：現行1本をトップ・旧版は`_旧版/`(削除しない)・命名`_v1.0`(禁止語=最新/コピー/修正版)・**Notion台帳の"現行バージョン"列が単一の真実**。

**台帳**：`inventory.py`が全資産をスキャンしCSV生成(`Downloads書類アーカイブ/_整理ログ/AI資産台帳_YYYY-MM-DD.csv`, 128行=汎用Skill5/プロジェクト付属Skill5/GAS1/主要MD117)。**Notion「AI資産台帳」DB**=https://app.notion.com/p/50f4165ff69345e79a5b9a040764fa1b (data_source `042afc91-02d9-4477-8153-eeb5faad2dbd`, AIナレッジハブ配下)に128件投入済、**AI活用ログDB**(レコード https://app.notion.com/p/3967b1568b578178be6bf14c56957f81 )と双方向リンク。再scanで更新。

**バージョン整理(2026-07-07 実施)**：同一フォルダ内でv付き版が同居していた18グループを検出、非曖昧な**19ファイルを各フォルダの`_旧版/`へ退避**(現行1本を残す・移動のみ可逆・ログ`_整理ログ/バージョン整理_2026-07-07.csv`)。例:standup_calendar 4版→現行v3_2_1のみ残す。**最新更新が旧版側の5グループは「曖昧」で保留**(要ユーザー確認:AI返信アシスタント引継書, brand_guideline v2/v2_1 ×2, トップページ v2/無印 ×2)。判定は厳格に`v`付き版番号のみ(スクショ/連番写真の誤検出は除外済)。

**重複DB統合方針(2026-07-07 決定)**：完全統合(削除/一本化)はしない。**3層で棲み分け**——AI資産台帳=Skill/GAS/MCPの"実体インデックス"(版・正本・パス・依存)のSoT／④プロンプト・スキルDB=プロンプト/指示/テンプレ/運用手順(マルチAI)のSoT・実体管理列なしの薄い器／②ナレッジ資産DB=文書の"要約+原本リンク"カード。Skillの版・所在は台帳のみで二重管理しない。④のSkill行は台帳リンク化。MD117は②と台帳を併存し無理にrelation化しない(運用ルール明文化のみ)。方針はREADME「Notion DBの役割分担」に記録。**未実測**：④の実Skillレコード件数(レート制限で未取得)→回復後に確認。

**統合方針=確定(2026-07-07)**：「3層棲み分け＋Skillは台帳SoT」で確定、かつ**(A)採用**＝Notion側の配線(④Skill行への台帳リンク等)は④の実Skill件数を実測してから着手(今は方針確定のみ・Notion変更なし)。

**要判断(未決)**：バージョン整理の曖昧5グループの現行確定(下記)。④のSkill件数実測(レート回復後)→多ければ台帳へリンク配線。hojokin-agent系の関連事業区分(暫定=共通)の確認。MD117件の関連事業タグは未設定(所在パスからILIFE案件多め)。バージョン整理(standup_calendar 4版→現行1本+旧版退避、議事録GAS v4重複解消)は未着手。

**How to apply**：新しくSkill/GAS/MD資産を作ったら①正本を上記ルールの場所に置く②`inventory.py`再実行③Notion台帳へ反映。裸置きSKILL.md(旧`01_AI・開発/SKILL.md`=prompt-architect)は整理対象。