---
name: reference_mac_mini_execution_env
description: Mac miniは裏側の常時稼働・実行機（メイン）。定期実行はここに置く。Python3.9系・claude CLIはPATH外・GitHub鍵は専用。スクリプトを書く前に読む
metadata:
  node_type: memory
  type: reference
---

**Mac mini が裏側のメイン実行機**（2026-08-13 本人確定）。定期実行・バッチは原則ここへ置く。
MacBook は閉じている時間がある前提で設計する。規範の本文は [[project_notion_operating_rules]] ではなく
正本 `vivid-ai-hq/.claude/skills/fukuchi-core/SKILL.md` の「マシンと実行の置き場」節。

**mini 向けにスクリプトを書く前に必ず踏むこと**

- **Python は 3.9.6**（MacBook と揃っていない）。`match` 文・f-string の `=` 記法など
  **3.10以降の構文を使うと本番でだけ落ちる**。`~/.vivid-relay/` に足すものは3.9互換で書く。
  確認は `ssh mini 'python3 -m py_compile <file>'`。
- **`claude` CLI は入っているが PATH に出ない。** 実体は `~/.npm-global/bin/claude`（v2.1.228）。
  `.zshrc` で PATH に足されているが、**SSHの非ログインシェルでは読まれない**ため
  `which claude` が空振りする。「入っていない」と誤判定しやすい。**フルパスで呼ぶ。**
- **GitHub 用の鍵は mini 専用**（`~/.ssh/id_ed25519_github`／`~/.ssh/config` で github.com に紐付け）。
  MacBook の鍵とは別物。mini からの `git` 操作はこの鍵で通る。
- Google Drive は mini にもマウント済み（`~/Library/CloudStorage/GoogleDrive-y_tam@vivid-global.com`）。
  ただし **Downloads整理は MacBook に残す**。対象が MacBook の `~/Downloads` だから。

**現在の cron（mini）**

```
*/15  vivid-ai-hq を git pull --ff-only（設定の受信。送信は本人が push）
7:45  Chatworkリレー（MacBookから移設）
```

**エージェントに規範が届いているかの確認方法**

「参照できていない場合はそう答えて」と条件を付けると、**実際は読めていても保守的に
「参照できていない」と答える**（MacBook・mini 双方で発生し、一度誤判定した）。
**肯定形で聞く** ―「その内容は含まれていますか。含まれていれば1行そのまま引用して」。
