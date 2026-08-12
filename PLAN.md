# vivid-ai-hq — AI規範の一元化と全面展開

> **このファイルが作業の正本。** 会話が圧縮されても、これを読めば続きから再開できる。
> 種別: 作業層（完了後は Notion ⑥ディスカッションログへ要約を残して降格）
> 最終更新: 2026-08-12 ／ 責任AI: Fable Style（主セッション）

---

## 1. 何を解決するのか

### 症状（2026-08-12 実測）

10体のエージェント定義と Output Style の間で、同じ規範が食い違っていた。

| | agents/*.md (10体) | output-styles/fable-mode.md |
|---|:--:|:--:|
| 図解ファースト／絵文字抑制 | ○ | **×** |
| 「境界」の量産モード例外 | ○ | **×** |
| 思考OS Skill の発動条件 | ○ | **×** |
| ビビ中央窓口→名鑑振り分け | ○ | **×** |
| 着手前のナレッジハブ検索 | ○ | **×** |
| 情報ファイアウォール | ○ | **×** |
| 生成ファイルのNotion添付 | ○ | **×** |
| 版ズレの検知 | ○ | **×** |
| 作業ログの強度 | 「都度・積極的に」 | 「一段落したら」（旧版） |
| 学習ログDBの参照形式 | `collection://16936917…` | `data_source 16936917…` |

### 真因（推測ではなく実物で確定）

全10体の CORE:BEGIN マーカーにこう書かれている:

```
正本は ~/.claude/core/ を編集し sync-agents.sh を実行
```

```
~/.claude/core/   → 存在しない
sync-agents.sh    → 存在しない（~/bin にも find でも 0件）
```

**正本ディレクトリも生成器も作られていない。** だから全員が配布先を直接手編集するしかなく、
CORE区間の外にあった「Notion運用ルール」節と Output Style が取り残された。

### 増幅器

```
crontab: */15 * * * * ~/bin/sync-claude-mini.sh
         rsync -au 双方向（新しい方が勝つ・整合性判定なし）
```
MacBook と Mac mini のどちらで手編集しても15分後に相手へ伝播する。正本判定が無い。

### 拡大要因（別スレッドの要件）

Web / スマホでも10体を使いたい。しかしクラウドセッションは `~/.claude` を読まない。

> The cloud VM **clones your current directory's GitHub remote**
> **Subagents defined in your repo's `.claude/agents/` are picked up automatically.**
> To change settings for a cloud session, **commit settings files to the repository**.
> — code.claude.com/docs/en/claude-code-on-the-web

→ 配布先が 2面（MacBook/mini）から 4面（＋Web/スマホ）に増える。
→ 正本をローカルディレクトリに置く案は破綻する。**正本は git リポジトリでなければならない。**

---

## 2. 設計 ─ コピーを配らない

生成器でテキストを10箇所へ複製する案は捨てた。**参照だけを配る。**

```
              .claude/skills/fukuchi-core/SKILL.md   ★唯一の正本（本文はここだけ）
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
  agents/*.md ×10     CLAUDE.md        （Web/スマホ）
  frontmatter:        @import           リポジトリを clone するだけ
  skills: [fukuchi-core]                で同じ実体が載る
        │                 │
   本文コピー無し      本文コピー無し
```

根拠（v2.1.228 で利用可）:
> `skills` — Skills to preload into the subagent's context at startup.
> **The full skill content is injected**, not only the description.

Output Style は「口調」だけに縮小し、組織ルールを一切持たせない → ズレる面が物理的に消える。

### 配布経路

```
        ┌──────────────────────────────┐
        │ GitHub: vivid-ai-hq (private)│ ★正本
        │   .claude/agents/  ×10 +1    │
        │   .claude/skills/            │
        │   .claude/output-styles/     │
        │   .claude/settings.json      │
        │   CLAUDE.md / .mcp.json      │
        └──────────────────────────────┘
     git pull │            │ 自動 clone
    ┌─────────┴──┐         ▼
    ▼            ▼    claude.ai/code ＋ スマホ(Claudeアプリ)
 MacBook      Mac mini
 ~/.claude/agents ─symlink→ repo
 ~/.claude/skills ─symlink→ repo
 ~/.claude/CLAUDE.md ─symlink→ repo
```

15分双方向 rsync は廃止し `git pull` に置き換える（ズレの増幅器を除去）。

---

## 3. 手順

### Phase A ─ ローカル組み立て（GitHub不要・AI側で完結）

- [x] **A1** リポジトリ骨格＋PLAN.md ─ `~/vivid-ai-hq/` git init 済（main / user=y_tam）
- [x] **A2** 共通規範を単一正本へ集約 ─ `.claude/skills/fukuchi-core/SKILL.md`（277行）
      CORE区間＋CORE外だったNotion運用ルール節を統合。廃止済みの sync-agents.sh 注記は除去
- [x] **A3** 10体を移設し、CORE区間を削除して `skills: [fukuchi-core]` 参照へ置換 ─ 3,275行→635行（本文の複製を全廃）
- [x] **A4** `CLAUDE.md` 作成（@import ＋ memory索引ポインタ）
- [x] **A5** `output-styles/fable-mode.md` を口調のみへ縮小し移設
- [x] **A6** `.claude/settings.json`／`.gitignore` 整備（`.mcp.json` は不要と判明：user-scope MCPサーバー0件、claude.aiコネクタはアカウント紐づけ）
- [x] **A7** `check.sh` 作成 ─ 規範の複製・skills参照漏れ・memory索引の孤児・symlink状態を検査。全項目パス
- [ ] **A8** ローカル2台を symlink 化、`*/15` 双方向 rsync を停止し `git pull` へ

### Phase B ─ GitHub（★ユーザー手番・10〜15分）

- [ ] **B1** github.com で **private** リポジトリ `vivid-ai-hq` を作成（README等は入れない）
- [ ] **B2** SSH公開鍵を登録（下記コマンドで表示）
- [ ] **B3** `git remote add` → `git push -u origin main`
- [ ] **B4** claude.ai/code で当該リポジトリを選択しセッション作成

### Phase C ─ クラウド実測（10分）

- [ ] **C1** クラウドセッションで `/mcp` → Notion/Gmail/Drive コネクタの可否を確認
      ★ここが×だと ビビ/ナミ/センゴク はWebで機能しない（全員Notion依存）
- [ ] **C2** 10体の呼び出しテスト（`@secretary` 等）
- [ ] **C3** スマホのClaudeアプリからセッション操作を確認

---

## 4. 確定事実（再調査不要）

| 項目 | 実測値 |
|---|---|
| Claude Code | v2.1.228（`skills:` frontmatter 利用可） |
| git | 2.39.5 あり／`user.email=y_tam@vivid-global.com`、`user.name` はglobal未設定 |
| gh / brew | **無し**。ブラウザ作成＋SSH push で代替可（導入不要） |
| SSH鍵 | `~/.ssh/id_ed25519.pub` あり（Mac mini接続用に作成済） |
| 既存リポジトリ | fukuchi-core / kids-apps / task は git初期化済だが **remote 0本** |
| memory | `~/.claude/projects/-Users-yujimac/memory/` に66本＋MEMORY.md（索引63行） |
| memoryのスコープ | **cwd依存**。`~/fukuchi-*` から起動すると0本になる |
| 孤児memory | `reference_org_master_notion.md` が MEMORY.md 未登録 |
| エージェント | 10体＋`pr-playbook.md`。CORE区間は10体とも同一ハッシュ `19d812a6…` |
| agents優先順位 | `.claude/agents/`(3) > `~/.claude/agents/`(4) > plugin(5) |
| 別スレッドの手順書 | 3〜5項（ブランチ取り込み／既存5エージェント／フォーク配布）は別案件の文脈。1・2・6〜8のみ有効 |

## 5. 未確定（Phase Cで解消）

- クラウドセッションで claude.ai コネクタ（Notion/Gmail/Drive/Calendar）が使えるか。
  コネクタはマシンでなくアカウントに紐づくため通る見込みだが、公式明言なし。
- スマホの**通常チャット**ではサブエージェントは使えない。使えるのは Claude Code クラウドセッションの操作・監視。

## 6. 再開方法（圧縮された場合）

1. このファイルを読む
2. `cd ~/vivid-ai-hq && git status && git log --oneline | head` で現在地を確認
3. 上のチェックリストの未完項目から続行
