# イベント運用スキル群（Claude Code / claude.ai 共通）

イベントの企画から広報、実施報告までを一連で回すための6スキル。
claude.ai と Claude Code の双方で同じ挙動になるよう、Agent Skills 仕様の
frontmatter（name / description のみ）で統一している。

## 構成

| スキル | 役割 |
|---|---|
| event-comms-orchestrator | ハブ。配信カレンダー生成とフェーズ判定、各スキルへの委譲 |
| event-db-sync | Notion イベントDBへの起票・更新・照会 |
| event-plan-kit | 企画書、香盤表、役割分担、KPI設計 |
| event-press-kit | プレスリリース（MARK N式8ステップ）、メディアアプローチ |
| event-social-kit | SNS素材（カルーセル/ストーリー/リール）とキャプション |
| event-report-kit | 実施報告書、KPI実績対比、課題と改善策 |

## 連鎖

```
event-plan-kit → event-db-sync → event-comms-orchestrator
                                    ├ event-press-kit
                                    └ event-social-kit
                                          ↓
                              event-report-kit → event-db-sync
```

## 設置方法（Claude Code）

### プロジェクト単位（チームで共有する場合／推奨）

リポジトリのルートに配置し、コミットする。クローンした全員が自動で使える。

```
<repo>/.claude/skills/event-*/
```

### 個人単位（全プロジェクトで使う場合）

```bash
cp -r event-* ~/.claude/skills/
```

Claude Code はセッション中のファイル変更を検知するため、再起動は不要。
新規にディレクトリを作った場合のみ再起動する。

### claude.ai から同期する場合

claude.ai 側でスキルを有効化したうえで、一度だけ非対話モードで実行する。

```bash
CLAUDE_CODE_SYNC_SKILLS=1 claude -p "List the skills you have available"
```

`~/.claude/skills/synced/` にダウンロードされる。claude.ai 側で
スキルを更新するたび、このコマンドを再実行する必要がある。

## 注意点

- 同名スキルは「個人 > プロジェクト」の順で優先される。
  claude.ai から同期したスキルは、ローカルの同名スキルに上書きされる。
  二重管理を避けるため、設置場所はどちらか一方に統一すること。
- 各スキルは Python 3 標準ライブラリで動く。
  event-social-kit のみ Pillow / OpenCV / NumPy / ffmpeg と日本語フォントを要する。
- Notion 連携には Notion MCP が必要。書き込み前に必ずユーザー確認を挟む設計になっている。

## 依存パッケージ（event-social-kit を使う場合）

```bash
pip install pillow opencv-python numpy
# ffmpeg と Noto Sans CJK も必要
```
