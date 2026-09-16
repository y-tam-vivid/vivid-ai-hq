# ふくち。会議室 ── ホスティングの外部調査（2026-09-15・クローバー博士）

★読むだけで書いた。本番サーバー・Vercel・台帳・Notion・kintone・Slack・コードへは1文字も触っていない。
★出典が付く数値は付けた。付かないものは「出典なし・推定」と明記した。★1つの結論に絞らず、選択肢と代償を並べる。

---

## ① 有璽氏の4つの問いへの直接の答え（結論を先に）

**問い① そもそも、どう作るのが普通か**
「画面(骨格)は滅多に作り直さず1回だけ配る」「数字(データ)だけを頻繁に更新する」の2層に分けるのが定石。
うちの「30分ごとに全体を作り直してデプロイ」は、この定石から見ると遠回り（詳細は③）。
数字だけを頻繁に更新する置き場として KV/Blob/DB を使うのは定石どおり。

**問い② うちの作りを疑ってほしい件**
疑ってよい。★「常時動くサーバーが要る」という前提自体が誤り。Mac miniが24時間稼働の実機なので、
Vercel側は"サーバー"ではなく"置き場"でしかない。全体再デプロイを30分ごとに繰り返す部分だけが過剰。

**問い③ 無料でずっと動いているものは実在するか**
実在する。GitHub(public repo)+GitHub Actions+GitHub Pagesの組み合わせ(Upptime方式)、
および Cloudflare Workers+KV は、★カード登録不要・商用利用も許可された無料枠が公式に明記されている。
ただし「社内限定(非公開)」×「定期実行」の組み合わせは、GitHub無料プランでは成立しない（後述）。

**問い④ Vercelの課金条件（2026年時点）**
Hobby(無料)でBlobは使えるが、1GB保存＋Advanced Operations月2,000回等の枠内に限る。
★超過すると即課金ではなく「使えなくなり30日待つ」。★今回の停止(Billing State: Inactive)は
容量超過ではなく、公式未記載の"謎の停止"としてVercelコミュニティに複数報告がある（原因未確定）。

---

## ② 構成の比較表

| 構成 | 費用（無料枠） | 常時動くか | 認証(社内限定) | 上限・注意点 | 出典 |
|---|---|---|---|---|---|
| **現状: Vercel静的サイト+Vercel Blob** | 静的配信: Fast Data Transfer 100GB/月・関数呼出1M/月・Edge Request 1M/月。Blob: 保存1GB/月・Simple Operations 1万/月・Advanced Operations 2,000/月・転送10GB/月 | ○（ただし後述の規約リスクあり） | Basic認証を自前実装 | Blobは容量でなく「操作回数」でも詰まる。超過すると**30日間アクセス不可**。原因不明の停止報告あり(下記) | [Vercel Blob Pricing](https://vercel.com/docs/vercel-blob/usage-and-pricing) |
| **Cloudflare Pages + Workers + KV** | Workers: 10万req/日。KV: 読10万/日・書込等1,000/日・保存1GB。Cron Trigger: 3/Worker(account計5)・最短1分間隔。Pages: 500ビルド/月 | ○ | Cloudflare Access(50人まで無料)、またはWorkerでBasic認証を自前実装 | 日次リセット式の上限。★**カード登録不要・商用利用可**と公式に明記 | [Workers Pricing](https://developers.cloudflare.com/workers/platform/pricing/), [Workers KV free tier](https://blog.cloudflare.com/workers-kv-free-tier/), [Cron Triggers limits](https://runhooks.app/blog/cloudflare-workers-cron-triggers-limits/) |
| **GitHub Actions + GitHub Pages（Upptime方式）** | Actions: publicリポジトリは無制限・privateは無料2,000分/月。Pages: 帯域100GB/月(ソフト上限・超過は警告のみ) | △ | Pagesは公開前提。★非公開×定期実行(schedule)は**GitHub Pro($4/月)が必須**（無料アカウント+privateリポジトリでは定期実行が機能しない） | 社内限定データをpublicリポジトリには置けない。この用途には無料枠だけでは成立しない | [Upptime how it works](https://upptime.js.org/docs/), [GitHub Actions billing](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions), [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) |
| **Netlify Functions + Netlify Blobs** | 月300クレジット共有プール（帯域20cr/GB・本番デプロイ15cr/回・関数実行10cr/GB時、関数タイムアウト10秒） | ○（クレジット内） | Password Protection機能あり（★無料プランで使えるか未確認） | クレジット枯渇で**配信停止**（自動課金はしない）。Blobsの容量上限は出典未確認 | [Netlify Functions usage](https://docs.netlify.com/build/functions/usage-and-billing/) |
| **Firebase Spark（無料）** | Firestore: 読5万/書2万/削除2万・日次、保存1GiB。Realtime DB: 保存1GB・★読み書き無制限(無料)。Hosting: 10GB。Cloud Functions: 200万回/月 | ○ | Firebase Auth内蔵。ただしHostingは公開前提で別途対策要 | ★**Cloud Storage(ファイル保存)は2026年2月3日から有料Blazeプラン必須へ変更済み**。Firestore/Realtime DBは無料のまま | Firebase料金解説記事複数（一次情報の料金ページは今回未fetch。出典弱め） |
| **Supabase（既にアカウントあり）** | DB 500MB・共有RAM500MB・MAU5万。Realtime: 同時接続200・月200万メッセージ・1メッセージ256KB上限。Edge Functions 50万回/月。ファイル1GB | △ | Supabase Auth内蔵 | ★**7日間アクティビティが無いと自動停止**（手動再開が必要・初回アクセスに10〜30秒のコールドスタート）。ただし定期pushがあれば「活動あり」とみなされ止まらない可能性が高い（未実測） | [Supabase Project Pausing](https://supabase.com/docs/guides/platform/free-project-pausing) |
| **Deno Deploy** | リクエスト100万/月・帯域100GB/月・CPU 50ms/req・KV保存1GB・cron API内蔵 | ○ | 自前実装 | カード不要・商用利用可と明記 | Deno公式ドキュメント（検索結果の要約のみ・一次情報は今回未fetch） |
| **Vercel Cron（参考。今のうちの仕組みとは別物）** | Hobbyは最大2ジョブ・1日1回まで・UTC限定・分単位の精度保証なし | - | - | ★今回の会議室はmini自身のcronが30分ごとにデプロイを蹴っているだけで、Vercel Cronは使っていない可能性が高い（未確認） | [Vercel Cron Hobby limits](https://runhooks.app/blog/vercel-hobby-cron-job-limits-explained/) |
| **参考: OSSの「AI社員/エージェント監視ダッシュボード」製品** | 例: Mission Control（OSS・無料）、agent-dashboard等 | ○（ただし★自前サーバーが前提） | 自前実装 | ★これらは「サーバーレスで無料ホスティング」ではなく「自分のマシンで動かす」前提の設計。mini自身で動かすなら候補になり得るが、Vercel等の代替にはならない | [Mission Control](https://mc.builderz.dev/) |

---

## ③ うちの作りへの所見（遠回りかどうか）

**★前提の整理から。**「常時動くサーバーが要る」という発想自体が、今回はズレている可能性が高い。
サーバーレス関数(Vercel Functions・Cloudflare Workers等)は「呼ばれた瞬間だけ動く」設計で、
待機中は課金も稼働もしない。★"常時動いている"のはMac mini(24時間稼働の実機)の方で、
Vercel/Cloudflare側は単なる「数字の置き場」＋「呼ばれたら数字を返す係」でしかない。

**①静的サイトの全体再デプロイを30分ごとに繰り返す部分＝遠回り。**
一般的な定石は「画面の骨格(レイアウト・HTML・CSS・JS)は変更があった時だけデプロイ」
「頻繁に変わる数字はKV/Blob/DBのような軽い置き場へ書き、画面側はそこを読みに行くだけ」の分離。
うちは骨格までまとめて毎回作り直しており、変わっていない部分まで毎回配り直している。
★Vercel Hobbyの上限(1日100デプロイ)には収まっているので"壊れてはいない"が、
本来デプロイ不要な作業を1日48回発生させている点は無駄が大きい。

**②Blobで数字だけ頻繁更新する設計自体は定石通り。**
「骨格は別・数字は軽い置き場」という発想そのものは間違っていない。
問題は「軽い置き場」として選んだVercel Blobの無料枠が、★容量(1GB)だけでなく
「操作回数」（Simple Operations月1万・Advanced Operations月2,000）でも制限されている点。
今回容量は206KB・202ファイルで全く問題にならない水準だが、
★list()等の操作は「Advanced Operations」としてカウントされ、月2,000回という枠は
30秒ごとの更新チェックを積み重ねるとすぐ届きうる規模。実際にVercelコミュニティでは
「容量は枠内なのに操作回数超過で止まった」「操作回数も枠内に戻ったのに停止が解除されない」
という報告が複数あり、当方はうちの実装がどのAPI(list/get/put)をどの頻度で呼んでいるかまでは
読んでいない（依頼で禁止されているため）。★今回の停止の直接原因がこれかどうかは
実測(コードを読む)しないと確定できない。

**③Vercel Hobbyの利用規約そのものが、法人利用と噛み合っていない可能性がある。**
Vercel Hobbyプランは公式に「非商用利用限定」と明記されている。ふくち。グループは法人であり、
社内業務の可視化であっても「事業のために使っている」以上、規約上はグレーゾーンに当たりうる
（この点はクローバーの判断ではなく、事実として提示するのみ）。原因不明の停止が繰り返されるなら、
規約適合と技術上の安定性の両方の観点から、Cloudflare(商用利用可・カード不要と明記)への
乗り換えを検討する価値がある。

**④GitHub Actions方式(Upptime型)は、今回は使えない。**
「社内限定のデータ」×「定期実行」の組み合わせが、GitHub無料プランでは技術的に成立しない
（非公開リポジトリでの定期実行(schedule)にはGitHub Pro月4ドルが必須）。
public repoにすれば無料だが、会議室の中身（誰が何をしているか）を公開するわけにはいかない。

---

## ④ 調べきれなかったこと・分からなかったこと

- **Vercel Blobの「Billing State: Inactive」停止の発生条件**は、Vercel公式ドキュメントに記載が無く、
  コミュニティ(ユーザー報告)からしか情報が取れなかった。★1経路(コミュニティの体験談)でしか
  確認できていない。停止後に「Vercelスタッフが手動で解除した」事例が複数あるらしいという言及はあったが、
  一次情報(Vercelサポートの公式回答)には辿り着けなかった。
- **今回止まった直接の原因**（容量か・操作回数か・別の課金判定か）は、当方はうちの実装コードを
  読んでいないため特定できていない。★依頼上の制約で読んでいないだけで、調べれば分かる可能性は高い。
- Netlify BlobsのGB単位の具体的な保存容量上限は出典が見つからなかった。
- Netlify Password Protection機能が無料プランで使えるかは確認できなかった（有料プラン限定の可能性）。
- Firebase・Deno Deployの料金は一次情報(公式料金ページ)を直接fetchしておらず、
  検索結果の要約記事からの引用に留まる（数値の一部はブログ記事の孫引き）。
- Google Cloud Scheduler等、GCP系の定期実行の無料枠・カード登録要否は未調査。
- 「無料で動いているように見えて実は課金している」がどの程度の割合で起きているか、
  定量的なデータは見つからなかった。個別の事実（Vercelはカード登録不要＝無料は真）は確認できたが、
  一般的な統計は無い。★この分野に「定説」と呼べるものは無い。

---

## ⑤ 出典一覧

- [Vercel Blob Pricing（公式）](https://vercel.com/docs/vercel-blob/usage-and-pricing)
- [Blob store suspended (billing inactive) on Hobby — Vercel Community](https://community.vercel.com/t/blob-store-suspended-billing-inactive-on-hobby-need-one-time-data-export/46834)
- [Store-level Blob suspension persists after usage dropped below Hobby limit — Vercel Community](https://community.vercel.com/t/store-level-blob-suspension-persists-after-usage-dropped-below-hobby-limit/48435)
- [Blob store suspended after hitting free-tier limit — Vercel Community](https://community.vercel.com/t/blob-store-suspended-after-hitting-free-tier-limit-please-reactivate/48680)
- [Vercel Hobby Plan（公式）](https://vercel.com/docs/plans/hobby)
- [Vercel Limits（公式）](https://vercel.com/docs/limits)
- [Vercel Hobby Cron Limits Explained](https://runhooks.app/blog/vercel-hobby-cron-job-limits-explained/)
- [Upptime — How it works](https://upptime.js.org/docs/)
- [GitHub Actions billing（公式）](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions)
- [GitHub Actions schedule limitation on free private repos — DevActivity](https://devactivity.com/insights/github-actions-cron-schedules-a-hidden-free-tier-hurdle-impacting-developer-productivity/)
- [GitHub Pages limits（公式）](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
- [Cloudflare Workers Pricing（公式）](https://developers.cloudflare.com/workers/platform/pricing/)
- [Workers KV free tier — Cloudflare Blog（公式）](https://blog.cloudflare.com/workers-kv-free-tier/)
- [Cloudflare Workers Cron Triggers Limits 2026](https://runhooks.app/blog/cloudflare-workers-cron-triggers-limits/)
- [Cloudflare Access free tier / basic auth options（コミュニティ・実装例）](https://developers.cloudflare.com/workers/examples/basic-auth/)
- [Netlify Functions usage and billing（公式）](https://docs.netlify.com/build/functions/usage-and-billing/)
- [Supabase Project Pausing（公式）](https://supabase.com/docs/guides/platform/free-project-pausing)
- [Supabase Pricing 2026 解説記事](https://uibakery.io/blog/supabase-pricing)
- [Mission Control（OSS AI Agentダッシュボード）](https://mc.builderz.dev/)
- [Firebase Free Tier 2026 解説記事](https://agentdeals.dev/vendor/firebase)
- [Deno Deploy Pricing 解説記事](https://www.srvrlss.io/provider/deno-deploy/)
