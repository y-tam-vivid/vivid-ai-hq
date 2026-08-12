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

### 真因（2026-08-12 訂正済み）

当初「生成器が作られていない」と判定したが**誤り**。Mac mini セッションの実測で確定した真の構造:

```
生成器は Mac mini に実在し、今日3回稼働している
  ~/.claude/core/{00-共通,10-法人,11-営業部門,20-個人}.md ＋ sync-agents.sh

しかし MacBook⇄mini の同期対象は agents/ skills/ output-styles/ memory/ の4つだけ
  → core/ と CLAUDE.md は同期対象外 ＝ MacBook からは存在しないように見えていた
```

**真因は「生成器が無い」ではなく、生成器の配布先リストに1面しか登録されていないこと。**

```
sync-agents.sh の配布先
  agents/*.md ×10 の CORE区間          ← 登録済み・完全一致 (f6b60f52ae60)
  output-styles/fable-mode.md          ← ★未登録 → 8項目が置いていかれた
  ~/.claude/CLAUDE.md                  ← ★未登録 → core/ と8行以上が逐語重複
  agents/*.md の CORE区間の外           ← ★対象外 → Notion運用ルールが手貼りで10体に重複
  Notion「🗺️ AI設定ファイルの地図」の写し  ← ★手動 → 4つ目の複製
```

配布先を足せばこの症例は直るが、**面が増えるたびに登録を思い出す必要がある**という同じ失敗の型は残る。
だから採る手は「配布先を足す」ではなく「配布そのものをやめる（参照だけ配る）」。

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

---

## 7. Mac mini セッションとの合流（2026-08-12 23:50）

mini 側監査（Google Doc: 1KJ_5cM_uq279TRnAUW-ysM-envj2YKr5RTlAleyo3KQ）を受けて実施。

### 突合の結果

| 論点 | 結果 |
|---|---|
| MacBook の agents は mini の今日の版か | **一致**。10体すべて `f6b60f52ae60`（mini指定の shasum 方式で実測） |
| 私の正本 vs mini の core（00-共通＋10-法人） | 見出し差ゼロ／本文差12行。内訳＝sync-agents.sh の運用注記3行（意図的に除去）＋写し更新の手順4行（旧方式固有）＋遵守義務の一文2行（旧手貼り節から引き継ぎ） |
| mini が指摘した「A2は不要」 | **半分正しい**。分解し直しはしていない（生成済みの出力をそのまま使ったので内容は同一）。ただし取り込みは必要だった |
| mini が指摘した「A6は不要」 | **不採用**。`sync-agents.sh --check` は複製の一致だけを見る。`check.sh` は複製の**存在**・skills参照漏れ・memory索引の孤児・symlink状態も見る |

### mini 側が数えていなかった複製が2つあった

- `~/.claude/CLAUDE.md`（5,659B）が core/ と **8行以上を逐語で重複**。sync-agents.sh の管理外
- Notion「🗺️ AI設定ファイルの地図」の全文写し（00/10/11）が4つ目の複製

→ どちらもリポジトリ方式では不要になる。CLAUDE.md は @import のみ、Notion写しは
   リポジトリへのポインタ＋要約（参照層ブリーフィング型）へ縮小する。

### 採った構造（mini の「混ぜない」原則は保持）

```
.claude/skills/
  fukuchi-core/     00-共通＋10-法人   → 全10体が frontmatter skills: で参照（配布はしない）
  fukuchi-sales/    11-営業部門        → 営業の作業時のみ。全体へ注入しない
  fukuchi-personal/ 20-個人           → 法人エージェントには載せない
_archive/           旧方式の実物（11/20原本・sync-agents.sh・mini CLAUDE.md）を保存
```

### 実施済み

- [x] **15分双方向 rsync を停止**（crontab をコメントアウト。バックアップ: scratchpad/crontab.backup-2026-08-12）
      ← mini 監査の「止めるまで両機の編集が競合し続ける」に対応。**最優先で実施**
- [x] mini の `core/` 4ファイル＋`sync-agents.sh`＋`CLAUDE.md` を回収
- [x] 11-営業部門 / 20-個人 を Skill 化。00/10 は fukuchi-core と突合の上で削除

### mini 側に残る作業（Phase B の後）

- mini の `~/.claude/core/` は**今後編集しない**。編集先はリポジトリの `.claude/skills/`
- mini でも repo を clone し、`~/.claude/{agents,skills,output-styles}` を symlink 化
- mini の `~/.claude/CLAUDE.md` は repo の CLAUDE.md へ置換（本文を持たせない）
- Notion「🗺️ AI設定ファイルの地図」を全文写し → リポジトリへのポインタ＋要約に縮小

---

## 8. 未決の判断 ─ Skill の正本は Drive か Git か（2026-08-13）

検査6（リポジトリ外の .md 検出）で、他cwdスコープに閉じ込められて不可視だった
`ai-asset-catalog` を回収した際に判明した衝突。

```
2026-07-07 決定   Drive「マイドライブ/AI資産_正本/」が Skill の正本
                  ~/.claude/skills は "稼働コピー"
                  旧版は _旧版/ へ・命名は _v1.0（禁止語=最新/コピー/修正版）
                  Notion台帳の「現行バージョン」列が単一の真実

今回の設計        .claude/skills/ が正本（git で版管理・check.sh で機械検査）
```

用途が違うだけで競合ではない可能性がある（Drive＝人が開く・DL可・Notion台帳と紐づく／
リポジトリ＝AIが実行時に読む・4面へ自動配布）。取りうる形:

| 案 | 内容 | 効果 |
|---|---|---|
| **案1** | リポジトリを正本、Drive を配布用ミラー（人が読む窓口）へ降格。Drive側は編集禁止と明記 | git履歴・check.sh が効く。Notion台帳は「現行=リポジトリのcommit」を指す |
| 案2 | Drive を正本のまま、リポジトリを実行用ミラーへ降格 | **編集先がDriveになり git と check.sh が効かなくなる**。今回の一元化の趣旨と衝突 |
| **案3** | 対象で分ける（実行されるSkill/agents＝リポジトリ／人が読む資料・成果物＝Drive） | 二重管理が増えない範囲で両立。境界の明文化が必要 |

推奨は案1。理由＝今回の一連の問題はすべて「機械が検査できない場所に正本を置いた」ことから出ている。
※ 2026-07-07 の宣言をどういう意図で出したかは本人しか知らないため、決定は本人。**ユーザー回答待ち。**

## 9. 承認待ちの破壊的操作（2026-08-13 提示済み・未実行）

いずれも削除はせず `_archive/` への移動のみ。git 管理下で巻き戻し可。

- ① 版の並存の解消: `~/bin/sort_downloads.py` と `_v4_backup.py`（md5一致・cron未使用）を退避し、
  `_v5.py` を `sort_downloads.py` へ改名＋crontab書き換え／`~/.claude.json.backup`・`.tmp.19316…` を退避
- ② A8 symlink化: `~/.claude/{agents,skills,output-styles,projects/…/memory}` を
  `_archive/claude-pre-migration-2026-08-13/` へ退避してから repo への symlink を張る
- ③ 他cwdの memory 原本は**動かさない**（動かすとそのcwdで起動時にメモリが消えるため、重複を許容）

## 10. 参照方式の実証（2026-08-13・ローカル）

コピー配布を廃止する前提＝「`skills:` frontmatter による注入が実際に効くこと」を実測で確認した。
これが×なら10体が規範なしで動くため、A8（symlink化）の前提条件として先に潰した。

```
実行  cd ~/vivid-ai-hq && claude -p --agent cfo --permission-mode plan "<規範の中身を問う質問>"

問い  情報ファイアウォールの「公開レベル」3区分を原文どおりに
      「迷ったときの既定」表で『ファイルを動かすか』の定め
      （推測で答えず、参照できていなければ「参照できていない」と答えるよう指示）

回答  内部限定 ／ メンバー共有可 ／ 外部公開可
      動かさない（保留にする）
      「システムプロンプトに読み込まれている fukuchi-core SKILL.md に基づく」と明言
```

`.claude/agents/cfo.md` は55行の固有定義のみで、上記の文言は1文字も含まれていない。
**参照方式は成立。** ただしこれはローカル（cwd=リポジトリ）での実証であり、
クラウドの clone 経路でも同じに効くかは C2 で別途確認する（合格条件はエージェント名の
一覧化ではなく「規範の中身を答えられること」）。
