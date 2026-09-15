# 無料プランは「枠」より先に「規約」で詰まる

**★2026-09-15 有璽氏**
> 「他社とかこういった部分、AI会議室とかがどうやって運営してるかを調べて、
>   バーシャル（Vercel）課金して皆さんやられてるのかどうかを調べて。
>   割ともうずっと動いてるようなものを見かけたりするんだけど、
>   そういったことっていうのができないものなの？」

★この問いを外へ投げた（クローバー）ことで、**こちらが1人で見ていたら出てこなかった事実**が出た。

## ★見落としていた事実 ── Vercel Hobby は非商用・個人利用のみ

一次情報（vercel.com/docs/plans/hobby・2026-08-31更新）:

> As stated in the fair use guidelines,
> **the Hobby plan restricts users to non-commercial, personal use only.**

**★費用の話だと思って調べていたら、規約の話だった。**
ふくち。グループのVercelアカウントには19プロジェクトある（2026-09-15 実測）。

```
jfbi.vivid-global.com   調査研究サイト・独自ドメイン・対外公開
lifestandup-preview     顧客案件のデモ
gamemarke_lp            営業で実際に使ったLP
kawachibanashi / sns-insight-pro / static-preview ほか計19
```

**★「会議室が止まった」は1プロジェクトの症状で、本体はアカウント全体の前提だった。**

## ★型として覚えること

```
無料で使えるかを確かめるときは★2つ別々に見る
  ① 枠（容量・回数・転送量）        ← つい先に見る
  ② ★規約（商用利用が許されているか） ← ★枠に余裕があっても、ここで不可のことがある
★①だけ見て「無料で足りる」と結論しない。★法人で使うなら②を先に読む。
```

- **★Cloudflare は「商用利用可・カード登録不要」と公式に明記**（Workers/KV）。
  同じ「無料」でも、規約の前提がまったく違う。
- **★症状から入ると①しか見えない。**「そもそもどう作るのが普通か」から投げたので②が出た。
  → [[feedback_look_outside_before_reinventing]]（★調査は症状でなく構築の仕方から投げる）

## ★あわせて分かったこと（クローバーの調査より）

- **定石は2層に分ける** ── 画面の骨格は変更時だけ配る／数字だけ軽い置き場を頻繁に更新。
  ★うちは30分ごとに骨格まで丸ごと作り直しており、そこは遠回りだった。
- **「常時動くサーバーが要る」は誤った前提。** 常時動いているのは Mac mini の方で、
  Vercel/Cloudflare 側は「置き場」＋「呼ばれたら返す係」でしかない。
- **GitHub Actions + Pages（Upptime方式）は今回使えない。**
  非公開リポジトリでの定期実行は GitHub Pro（$4/月）が必須。公開リポジトリには社内の中身を置けない。
- **Supabase は7日間アクティビティが無いと自動停止**（定期pushがあれば止まらない見込み・未実測）。
- ★Blob の「Billing State: Inactive」停止の条件は**公式に記載が無い**。
  コミュニティに「枠内に戻っても解除されない」報告が複数ある（★1経路でしか確かめていない）。

関連 [[reference_free_tier_dies_by_count_not_size]] [[project_ai_office_console]]
[[feedback_look_outside_before_reinventing]] [[reference_vercel_free_plan_protection]]
