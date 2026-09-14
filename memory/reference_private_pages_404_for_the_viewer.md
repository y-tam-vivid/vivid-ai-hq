---
name: reference_private_pages_404_for_the_viewer
description: 非公開・下書きのWPページは「ログイン中のそのブラウザ」でしか開けない。こちらで見えた＝有璽氏に見える、ではない
metadata:
  type: reference
---

**2026-09-14 オレンジワークス（orange-works.co）で実際に起きた。**
こちらの Chrome（ログイン済み）でスクショを撮り「このリンクで見られます」と4本渡した
→ 有璽氏「どのページも今見れない。NotFound404になる」。

実測（未ログインの curl）：
```
/works/ ・ /works/service/ ・ ?post_type=work&p=…&preview=true   → 404（private は未ログインに404を返す）
/wp-admin/edit.php                                           → 403（nginx の IP 制限＋AIOS でログインURL変更）
```

**★「私の画面で見えた」は「相手に見える」の証拠にならない。** 経路が1本（自分のログイン済みブラウザ）しか無い。
リンクを渡す前に、**相手がどの状態で開くか**（ログイン有無・端末・社外ネット）を実測する。
未ログインで開けないものは、リンクでなく**画像（Artifact）で渡す**か、見るための手順（ログインURL・許可IP）まで添える。

→ [[feedback_one_route_is_not_verification]] ／ [[project_orangeworks_portfolio_site]]

**✅裏付け（9/15 00:0x）**：有璽氏がログイン側で見られた＝真因は未ログインで確定（有璽氏の実見＋未ログインcurl の2経路）。
