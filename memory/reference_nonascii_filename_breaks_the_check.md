---
name: reference_nonascii_filename_breaks_the_check
description: 日本語ファイル名は git が "\347\231\272" とクォート＋8進エスケープで返すため、パスを正規表現で判定する検問が黙って外れる。同期の自動解決が24.5時間止まった実例。
metadata:
  type: reference
---

# 日本語ファイル名は、機械の判定を黙って外す

**★機械が「解けるはずのものを解かない」とき、まずファイル名の文字種を疑う。**
`git` は既定（`core.quotepath=true`）で、ASCII 以外を含むパスを**クォート＋8進エスケープ**して返す。

```
実物                          git が返す文字列
memory/MEMORY.md              memory/MEMORY.md                             ← そのまま
memory/INDEX_発信.md          "memory/INDEX_\347\231\272\344\277\241.md"   ← ★別物になる
```

`^(memory/.*\.md|WORKING\.md)$` のような正規表現は、後者に**当たらない**（先頭と末尾が `"`）。
`[ -f "$_f" ]` のようなファイル存在チェックも同じ理由で外れる。**例外は出ない。静かに条件が偽になる。**

## 実例 ── 同期が24.5時間止まった（2026-09-16 つる）

```
現象   mini が behind 48 / ahead 6。分岐点 9/15 08:11 から約24.5時間
       SYNC_STATUS.md は「🔴自動マージが★衝突して中止された。人が解くまで古いまま」
実測   merge-tree で衝突予測 → 衝突は memory/*.md の★3本だけ。コードの衝突は★0本
       ＝ 2026-09-14 新設の「追記型なら機械が両方残して解く」ロジックの対象そのもの
真因   bin/vivid-sync.sh:129 `git diff --name-only --diff-filter=U`
       衝突3本のうち memory/INDEX_発信.md が日本語名 → クォートされて正規表現に当たらない
       → 「追記型ではない」と判定 → 自動解決へ入らず abort → 🔴のまま固定
直し   `git -c core.quotepath=false diff --name-only --diff-filter=U`
```

**★2026-09-14 に1度だけ発火した実績（commit `773686b`）があるのが、この型を見えなくした。**
そのとき衝突したのは ASCII 名のファイルだけだった。
＝ **①作った ②繋いだ ③1度は発火した、が揃っていても「日本語名のときだけ落ちる」**
→ [[reference_make_it_impossible_not_detectable]] の①②③を実測しても、この穴は通り抜ける。

## ★同じ日、同じ症状を別セッションが「人の問題」と書いていた

向こうは「9/14 に直したのは🔴の**文面**であって**解く人が来ること**ではない。
文面は正しい。それでも1日止まった」と結論していた（`reference_silent_sync_failure.md` の書きかけ）。
**★解く人は要らなかった。機械が解けるのに、判定が外れていただけ。**
**「人が拾わないから溜まる」と読むと、対策が精神論（もっと拾え）に向かう。**
機械が落ちている可能性を、先に1回だけ実測で潰す。

## どこを疑うか（同期に限らない）

```
git diff / status / ls-files の出力を正規表現やgrepに通している
find / ls の結果をシェル変数へ入れて [ -f ] している
Python の subprocess で git の出力を split して突き合わせている
```

**★確かめ方**：判定に使っている実際の文字列を1度 `echo` して目で見る。
`grep -c` の件数だけ見ると「0件＝該当なし」と読んでしまう（沈黙は確認成立の証拠にならない）。
→ [[feedback_one_route_is_not_verification]]

**★日本語ファイル名そのものは悪くない。**`memory/INDEX_発信.md` は読む人のための正しい名前。
直すのは名前ではなく、**名前を読む側**（`core.quotepath=false` を明示する）。

関連 → [[reference_silent_sync_failure]] ／ [[reference_make_it_impossible_not_detectable]] ／
[[reference_a_warning_nobody_owns]]
