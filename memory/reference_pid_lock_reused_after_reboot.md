---
name: reference_pid_lock_reused_after_reboot
description: 再起動後、ロックファイルのPIDが別プロセスに再利用され、常駐が「先の実行が生きている」と誤認して黙って止まる型（2026-09-28 slack_socket で実害）
metadata:
  type: reference
---

**2026-09-28 つる自己監査で発見。** mini が再起動（08:23）した後、`~/.vivid-relay/slack_socket.lock` に
残っていた PID 920 が **天気アプリ（WeatherIntents）に再利用**されていた。
`lock_or_exit()`（slack_socket.py:794）は「そのPIDが生きているか」しか見ないので、
**30秒ごとに「先の実行（PID 920）が生きているので今回は何もしない」を出して止まり続けた**
＝Slackのボタン受信が死んでいた。レジスタは🔴停止の疑い（最終心拍23.2h前）。

- 応急処置：ロックを `_backups/slack_socket.lock.stale_pid920_20260928` へ退避 → launchd が30秒で再起動、
  08:41:26 hello受信・新PID 4613 が python の slack_socket.py であることを ps で確認（2経路一致）
- **★恒久対策は未実施（コード＝ピタゴラス領域）**：PIDの生死だけでなく、`ps -p <pid> -o command=` に
  自分のスクリプト名が含まれるかまで見る。起動時刻がロック作成より新しければ別物と判定するのも可
- 同じ朝、crontab 直書きの 07:20〜07:50 のジョブは**再起動中で全部抜けた**。cron は追いかけて実行しない。
  daily_jobs.sh 経由のものは追いつくが、crontab 直書きは追いつかない → [[project_automation_register]]

**How to apply:** 再起動・停電の直後に常駐が🔴なら、まずロックファイルのPIDの **中身（コマンド名）** を見る。
「PIDが生きている」は「自分が生きている」の証拠にならない。
