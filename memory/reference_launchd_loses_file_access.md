---
name: reference_launchd_loses_file_access
description: "cron を launchd へ移すと、同じスクリプトが同じユーザーで動くのに Downloads/Desktop/Documents を読めなくなる。TCCは「誰が起動したか」で判定するため"
metadata:
  type: reference
---

**cron から launchd へ移し替えると、ファイルアクセス権が消えることがある。** スクリプトも
ユーザーも変えていないのに `PermissionError: [Errno 1] Operation not permitted` で落ちる。

macOS の TCC（プライバシー保護）は**実行された中身ではなく、誰が起動したか**で許可を判定する。

```
cron が起動      → cron に与えたフルディスクアクセスが効く      読める
launchd が起動   → plist の Program（/usr/bin/python3）を見る   許可が無ければ読めない
```

**2026-08-18 実測**（`~/bin/sort_downloads.py`）── cron では動いていたものが、launchd 経由の
dry-run で `Operation not permitted: '/Users/yujimac/Downloads'` を出して exit 1。
**移していたら、29%飛んでいたものが100%止まっていた。**

## 移す前の判定

```
そのスクリプトが読む場所は？
  │
  ├─ ~/Library 配下だけ（ブラウザ設定・アプリのPreferences 等）
  │     → TCCの保護対象外。launchd へ移してよい
  │       例: browser_hygiene.py は launchd で問題なく動いた（同日実測）
  │
  └─ Downloads / Desktop / Documents / iCloud / 外部ボリューム
        → TCCの保護対象。**移すと止まる**
          cron のまま置くか、python3 にフルディスクアクセスを与えるか
          （後者は全pythonスクリプトが全ファイルを読めるようになる。影響が広い）
```

## 必ずやること

**移す前に、launchd 経由で1回 dry-run を通す。** plist をテスト用ラベルで作り、
`launchctl kickstart` して exit code とログを見る。手元で `python3 script.py` が
動いたことは**launchd で動く証拠にならない**。→ [[reference_dangerous_entrypoints]]

## 関連する判断

MacBook の cron は「予定時刻に寝ていた回を捨てる」（実測29%欠落）。launchd なら復帰後に
取り戻せる ―― が、**それはTCCに触れない仕事に限る**。飛ぶこと自体は
[[project_automation_register]] の心拍が🔴で検知するので、cron のまま残す判断も成り立つ。
