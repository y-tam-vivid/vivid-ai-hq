---
name: project_slack_command_center
description: Slack から有璽氏が指示 → mini の窓口ビビが受けて各担当へ回す形（2026-10-14 有璽氏の理想）。仕組みは 9/4 から在り、10/5〜10/14 は claude 認証切れで止まっていた
metadata:
  type: project
---

**有璽氏の理想（2026-10-14）**：「Slackから私が指示を出す形。Mac mini なりで AI エージェント、主に窓口は秘書ビビが受け取り、他のAIに指示を出していく設計」

**★もう在る（新しく作らない）── mini `~/.vivid-relay/slack_inbox.py`（cron 5分毎）**

```
Slack DM ─→ slack_inbox
   ├ 不可逆の語（送信・公開・削除…）→ 実行せず「承認します」を待つ
   ├ 短い「状況」の問い           → claude を起動せず status_report で即答（9/4 有璽氏）
   ├ 作る/直す/設計/検査/決め…    → bin/team_run.py（一人でやらせない・8/20 有璽氏）
   └ それ以外                    → vivi_prompt.build で ビビとして claude 実行 → DMへ返す
判断ボタンの回答は ask_hub（別の台帳）。📮AI指示箱は inbox_runner（同じく5分毎）
```

- **🔴10/5〜10/14 は全部止まっていた**：claude を cron から呼ぶと認証切れ（→ [[reference_mac_mini_execution_env]]）。
  ログは「新しい発言 0件」が並ぶだけで、落ちるのは発言が来たときだけ＝★見た目は健康だった
- ✅10/14 20:3x 直した：入口 `~/.vivid-relay/claude_cron.sh`（config.env の長期トークンを渡す）へ6か所を向けた。env -i で4本とも OK
- ▶未確認：★有璽氏の実際の DM で端から端まで通ったこと（AI からは有璽氏として送れない）
- ▶理想との差（未着手・相談して決める）：振り分けは語の正規表現で決まる（ビビの判断ではない）／担当の結果を束ねて返すのは team_run 側

**How to apply:** Slack 指示まわりを触る前にここを読む。新しい受付を作らず slack_inbox を直す。[[project_ask_hub_push_decisions]]
