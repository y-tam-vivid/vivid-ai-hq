---
name: reference_group_blogs_and_cms
description: ふくち。グループ5法人のブログのURLとCMS。入稿形式が3種類あるので原稿はCMSに合わせる
metadata:
  type: reference
---

**2026-08-25 実測（curlでHTMLのフィンガープリントとHTTPステータスを確認）。**

```
法人                        CMS         ブログの入口                            実測
株式会社ILIFE                WordPress   https://i-life-fukushi.com/blog        200（メニュー名「活動風景」）
株式会社ふくち。               STUDIO      https://fuku-chi.com/news              200（/blog も200）
株式会社ビビッド               WordPress   https://www.vivid-global.com/          ★www付き。記事は
                                        月別アーカイブ /2025/10/ が200            /YYYY/MM/post-N.html
                                        sitemap: /post-sitemap.xml               ★カテゴリ一覧は無い
オレンジワークス藤井寺          WordPress   https://orange-works.co/news           200（/blog は404）
                             + Elementor                                         ★Elementorで組まれている
NPO南河内こどもステーション      Jimdo       https://minamikawachi-kodomostation.jimdosite.com/
                                        ★/blog は403＝入口のパスが別。要確認
```

**★入稿形式はCMSごとに違う。原稿を渡すときは形を合わせる。**

```
WordPress   見出し(h2/h3)＋段落の構造で渡す。ILIFE・ビビッド・オレンジワークスの3つ
            ★オレンジワークスはElementorなので、ブロック単位で貼れるよう見出しと段落を分けて渡す
STUDIO      リッチテキスト。プレーンテキスト＋画像の順序で渡すのが確実（ふくち。）
Jimdo       同上。文章ブロックと画像ブロックを交互に置く形（NPO）
```

- **ビビッドのドメインは www 付きが正。** `vivid-global.com`（www無し）と
  `www.vivid-global.com` の両方が生きているが、記事は www 側にある。
- Instagram は別台帳に載っている → Notion「📱 発信アカウント台帳」
  （collection://3f0202d1-2352-4695-a399-626705eb9014）。**ブログもこの台帳に統合した**
  （DBを分けると発信先が2か所に散るため）。
- 関連 → [[feedback_press_release_is_not_done_at_distribution]] ／ [[reference_tane_brand]]
