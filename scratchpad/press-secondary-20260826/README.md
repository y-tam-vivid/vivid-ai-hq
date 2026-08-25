# リリース二次展開の原稿と画像（2026-08-26 時点）

**セッションのscratchpadは揮発する**ので、ここへ退避した。
前回それで実物を失っている → `memory/project_npo_press_releases_202608.md` の
「scratchpad実体」の項。

```
secondary-posts.tpl.html   原稿12本の編集元。__IMG_XXXX__ が画像の差し込み口
make_social_images.py      Instagram用1080×1080を7枚つくる。元画像は読むだけ
social/                    ★生成済みの7枚。原本(~/Downloads/IMG_*.jpeg)は
                           Downloads整理で動く可能性があるので、ここにも置いた
```

## 公開先（同じURLへ再公開する）

https://claude.ai/code/artifact/125abd35-6128-40c3-9b1a-c638d5617a8b

**★別のファイルパスで publish すると別のArtifactになる。** 更新するときは
tpl を直す → 下の手順で焼く → **同じパスの `secondary-posts.html` を publish**。

```
1  python3 make_social_images.py            画像を作り直すときだけ
2  下の焼き込みを流して secondary-posts.html を作る
3  Artifact に secondary-posts.html を渡す（同じパスなら同じURLへ更新される）
```

焼き込み（差し込み口 → data URI）:

```python
import base64, io, os
pairs={"__IMG_0101__":"01_1_cover.jpg","__IMG_0102__":"01_2_booth.jpg",
       "__IMG_0103__":"01_3_kyoto.jpg","__IMG_0104__":"01_4_hall.jpg",
       "__IMG_0105__":"01_5_numbers.jpg","__IMG_0201__":"02_1_banner.jpg",
       "__IMG_0202__":"02_2_credit.jpg"}
s=io.open("secondary-posts.tpl.html",encoding="utf-8").read()
for tok,name in pairs.items():
    s=s.replace(tok,"data:image/jpeg;base64,"+
                base64.b64encode(open("social/"+name,"rb").read()).decode())
io.open("secondary-posts.html","w",encoding="utf-8").write(s)
```

## 元画像の対応（make_social_images.py が読む先）

```
01_1_cover   ~/Downloads/IMG_4463 2.jpeg   グランフロント大阪・親子
01_2_booth   ~/Downloads/IMG_4460 2.jpeg   ★左半分だけ切る（右にRoblox看板）
01_3_kyoto   ~/Downloads/IMG_8196.jpeg     ★右側だけ切る（左にRobloxポスター）
01_4_hall    ~/Downloads/IMG_4467 2.jpeg   会場全景
02_1_banner  img/webinar_banner.jpg        ★これだけ揮発済みの可能性。
                                           原本は ~/Downloads の登壇PDF
```

**★クロップ位置は規約対応。** 変えるときは
`memory/reference_roblox_event_naming_rules.md` を読んでから。
