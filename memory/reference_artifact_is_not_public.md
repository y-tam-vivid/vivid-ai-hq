---
name: reference_artifact_is_not_public
description: Claude の Artifact URL は社外・Claudeアカウント外の相手には見せられない。外部へ渡す成果物の出し先の選び方
metadata:
  type: reference
---

**★Artifact の URL は「社内で回すもの」であって、社外へ渡せる公開URLではない。**

2026-09-08 実測（かわちばなし・トップページ）。有璽氏が Artifact のURLを他者へ送ったが
**「見れない」**。相手は Claude の環境下にいない。

```
こちらの見立て（誤り）  「公開しただけでは非公開。共有メニューから共有すれば見られる」
実際                   ★その共有は Claude アカウントを持つ相手にしか効かない
                       Claude を使っていない社外の人には、共有しても届かない
```

## 出し先の選び方（★「見せたい相手が誰か」で決まる）

```
社内・Claudeを使う人     Artifact でよい。★枠を消費しない・更新が1手
社外・Claudeを使わない人  ★Artifact は不可。下から選ぶ
  静止画でよい           PNG／PDF にして Google Drive へ置きリンク共有 ★いちばん確実・すぐ
  Webページとして見せたい  GitHub Pages ／ Cloudflare Pages ／ Netlify
  Vercel                 ★2026-09-08 時点で枠が尽きている（有璽氏）。使わない
                         → [[reference_vercel_free_plan_protection]]
```

## この環境に在るもの（2026-09-08 実測・MacBook）

```
gh / netlify / wrangler / surge   ★4つとも入っていない
git                               あり（2.39.5）
Vercel                            MCP経由で叩けるが★枠が尽きている
Google Drive                      MCP経由で使える（PNG/PDFの置き場としては確実）
```

## 型として

- **★「共有できます」と言う前に、相手がどの環境にいるかを1回聞く。**
  こちらは Claude の中にいるので、Claude の共有が万能に見える。**外から見ると壁がある。**
- 同型 → [[feedback_cannot_copy_from_terminal]]（ローカルのファイルパスも届かない）／
  [[feedback_write_for_the_reader]]（「どこで見えるか」を1行で言う）。
  **3つとも「こちらから見えているものが、相手からは見えていない」という同じ穴。**

## ★実際の出し方（2026-09-08 確立・実測つき）

```
① 静的HTMLを作る        scratchpad/{extract_vals.js, render_dc.py}
② 長尺PNGで撮る          Chrome headless。★撮影用の版を別に作って2点を潰す：
                        ・min(68vh,600px) → 600px    高さを大きく取ると hero が巨大化する
                        ・position: fixed → static   下端に貼り付いてトリムが効かない
                        実測：この2点を潰す前は「実高さ19,991px」と出た。潰したら★5,349px
③ Drive へ上げて公開     bin/drive_upload.py <file> <mime> --public   ★mini から実行
                        （MacBookには google 認証もライブラリも無い。miniにdriveスコープ在り）
```

**★公開できたかの確かめ方（1経路で断定しない）**

```
✕ 使えない  ページのHTMLに「ログイン」が含まれるかを見る
            → Drive のビューアには常にログインボタンがある。★必ず誤検知する（実際にやった）
○ 使える    ①API の permissions.list に ('anyone','reader') があるか
            ②★認証なし・cookieなしで実体が取れるか
              curl -L "https://drive.google.com/uc?export=view&id=<ID>"
              → HTTP 200 / image/png / 2,940,029 bytes / 1440x5349 を実測できた
```

**PDF は使わない。** Chrome の --print-to-pdf は紙幅（612pt）に押し込むのでレイアウトが崩れ、
ページ区切りでカードが分断される（9ページに割れた）。**長尺PNGの方が原本に近い。**
