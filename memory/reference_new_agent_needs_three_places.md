# 担当が増えたら、同じターンで3か所を揃える

**★2026-09-13 有璽氏「直近で担当が増えたと思うので、それの確認もお願いしたい」**

チョッパー（`responsive-engineer`・レスポンシブ／オートレイアウト担当）が増えていた。
実測すると、**増えているのに画面に1つも出ていなかった。**

```
名鑑 .claude/agents/responsive-engineer.md   ★MacBookに在り・miniに無かった
会議室の席（office_data.build_members）      ★14人のまま＝席が無い
羅針盤のアイコン行（dashboard_projects）      ★14人のまま
走行判定（agent_running.AGENT_KEY_PREFIX）   ★chopper を引けず「名鑑に無い」と表示
立ち絵 assets/agents_portrait/320/*.png      ★無い（画像が割れる）
```

## 真因は2つ

**① 二重管理。** 名鑑は `.claude/agents/*.md` にあるのに、会議室は
`AGENT_ROUTINES` という**手書きの辞書**を名簿にしていた。
＝担当が増えるたび、人が2か所を直さないと席ができない。
→ **★名鑑を正本にした**（`_roster_keys()`）。ルーティンが無い担当も席だけ出て
「今日は出番なし」と座る。**名鑑に1本足せば席ができる。**

**② 片機だけを見て「無い」と言った。**
mini の `.claude/agents/` を見て「名鑑に無い名前」と画面へ出した。
**MacBook 側には在った**（別セッションが commit 済み・miniへ未着）。
→ 規範「1経路で断定するな」。**両機で数えるまで「無い」と書かない。**

## ★担当が増えたときに揃える3か所（＋2）

```
① .claude/agents/<key>.md          名鑑の実体 ★両機に届いたか確認する
② agent_running.AGENT_KEY_PREFIX   起動名（chopper_xxx）→ key
③ dashboard_projects.AGENT_NAME_MAP / AGENT_DISPLAY   日本語名 ⇄ key ⇄ 表示名
＋ 立ち絵 assets/agents_portrait/{,320/}<key>.png     ★無ければ頭文字が出る（割れない）
＋ 会議室の席は①から自動で作られる（2026-09-13 以降）
```

**★起動名は自由記述。** `run_agent.sh <名前>` の名前には接尾辞が付く
（`lilith_005` `pita_wp_run` `chopper_ledger`）。だから②は**前方一致**で引く。
引けなければ **推測で当てない**。当てると別の担当が動いて見える方が有害。
引けなかったことは `unmapped_running()` で数え、画面の error 欄へ出す。
