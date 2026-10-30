---
name: project_meeting_sort_card
description: 議事録の仕分けカード③（mini meeting_sort.py）。議事録ごとにSlackのカードで相手・区分・共有を決める。2026-10-30 段階1を cron で稼働
metadata:
  type: project
---

設計＝名鑑の設計担当 `scratchpad/handoff/2026-10-30_仕分けカード③の設計.md`（クラウドのブランチ claude/internal-business-partner-platform-v4zjnn）。実装＝ピタゴラス（mini）／検査＝ステラ（条件付き合格→必須6点を直した）／cron 前点検＝ドーベルマン（条件付きで可）。

## 現在地（2026-10-30 11:57〜稼働）
```
cron(mini)  3,18,33,48 * * * *  meeting_sort.py --live    拾う→カード→押された答えを書く
            5 17 * * *          meeting_sort.py --digest  社内として自動で記録した分を［違う］ボタン付きで（1通3件まで）
心拍        ⚙️レジスタ「議事録の仕分けカード」（行名＝コードの HEARTBEAT_NAME と1字違わず一致させる）
            「…夕方の一覧（--digest）」行は有効OFF（digest は成功の心拍を打たない作り）
対象        段階1＝有璽氏個人の議事録で、作成が稼働開始 10/30 11:35 より後のものだけ。1日10枚まで
控え        mini _backups/{meeting_sort.py,notion_meeting_customer_link.py,crontab}.bak_20261030-*
```
- 有璽氏の答え（10/30・Slackボタン）：#7a8dcd 列を足してよい／#23e9aa 夕方は1件ずつ［違う］ボタン付き／#56b3a4（試しのカード）②確定して全社へ共有。
- 🔒個人議事録DB に列 `仕分け`（未／自動／確定／受付待ち／保留）と `仕分けの受付番号` を足した（22→24列）。
- ★既存のリンカー notion_meeting_customer_link.py（毎朝07:35）は「仕分けが空 or 受付待ち」の行だけを扱うように1条件を足した。カードと二重に相手を決めないため。
- ★全社への共有は、顧客が空のままでは立てない（promote_minutes.py は昇格した時点の顧客を写すだけで、後から直らない）。意図は state.json の share_wanted に残し、顧客が付いた回に立てる。14日で外す。
- 機微＝GASの「機微の疑い」列が空でないもの（自前の語彙はやめた・広すぎて47%が機微になった）。機微の行は Haiku を呼ばない。
- 当たり率（dry-run・直近6か月の正解付き社外45件）：機械の1位で一致 41/45。正解の一部はリンカーが付けたもので高めに出る。

## 残り
- ［直す］のモーダルは未実装。✍️その他に「2」や会社名を書けば直せる。モーダルには ask_hub.py・slack_socket.py の改修が要る＝バックオフィス担当のセッションが持っている（差分の案は mini `meeting_sort_dryrun_result.md` B節）。
- vivi_desk が議事録カードにも「担当のセッションは閉じています」と返す（文面が実態と違う）。vivi_desk はバックオフィス担当の持ち物。
- 本物で通っていない道：①確定・社内の自動・保留・［違う］の戻し・夕方の一覧の投稿・Haiku の本物の呼び出し。初回を見る：17:06 の一覧／新しい議事録が入った最初の回。
- 段階2（過去分・直近6か月から・1日10枚）と段階3（社員）はまだ。
- 報告書の一式：mini `~/.vivid-relay/meeting_sort_{dryrun_result,live_result,stella_review,fix_result,watchdog}.md`

関連 [[project_giji_automation_gas]] [[project_meeting_customer_relation_linker]] [[project_partner_meikan]] [[project_ask_hub_push_decisions]]
