---
name: reference_vivid_dns_sakura
description: vivid-global.com のDNSとWebはさくらインターネット。レジストラはGMO。当方に認証情報が無くDNS変更もFTPも実行できない
metadata:
  type: reference
---

**`vivid-global.com` のDNSもWebサーバも、さくらインターネットにある**（2026-08-22 実測）。

```
NS          ns1.dns.ne.jp / ns2.dns.ne.jp     ＝ さくらのDNS
A           210.224.185.82（www も同じ）      ＝ さくらのサーバでサイトが動いている
レジストラ  GMO（internet.gmo）               ★ドメイン登録とDNS運用は別会社
```

## ★当方からDNSは変更できない（実測して確認した）

```
~/.netrc                なし
~/.vivid-relay/config.env  CHATWORK / NOTION / SLACK のトークンだけ。さくらの情報は無い
さくらのAPI             レンタルサーバのゾーン編集にAPIは無い（コントロールパネルのみ）
```

**＝ DNSレコードの追加も、FTPでのファイル配置も、有璽氏がコントロールパネルへログインして行う。**
「DNSを設定して」と言われても実行できない。**押す場所まで特定して渡すのが当方の仕事。**

## さくらのゾーン編集の作法

```
コントロールパネル → ドメイン/SSL → 該当ドメインの【ゾーン】→ レコード編集
  タイプ       CNAME
  エントリ名   ★サブドメイン部分だけ（例 gamemarke）。FQDNを入れない
  データ       向け先＋★末尾にドット（例 cname.vercel-dns.com.）
```

- ログインは「**初期ドメインまたは追加ドメイン ＋ パスワード**」。
  メールアドレスでログインするとメール設定しか出ない
- 反映の確認は `dig +short <サブドメイン>` で行う（当方でできる）

## ko-station.org（南河内こどもステーション）── 2026-10-03 実測

```
NS     ns1/ns2.dns.ne.jp（さくら）  レジストラ表示 JPRS（2026-05-30取得・2027-05-30期限）
A      219.94.129.104 ＝ www1094.sakura.ne.jp（★別のレンタルサーバ。vivid-global.com とは別契約）
AAAA   2403:3a00:101:a:219:94:129:104
www    → ko-station.org（CNAME）
MX     10 ko-station.org        ★メールは使用中（有璽氏）。A を外へ向けるとメールが止まる
TXT    v=spf1 a:www1094.sakura.ne.jp mx ~all
Web    空ページ（0バイト）
```
- Vercel へ乗せ替える順番：①MX を www1094.sakura.ne.jp. へ → 受信を確認 → ②A を Vercel・AAAA 削除 → ③www を CNAME
- ✅10/3 切替済み：MX→www1094.sakura.ne.jp.／A 216.150.1.1・216.150.16.1（Vercel）／AAAA削除／www はCNAMEのまま
- ✅10/5 TXT に google-site-verification を追加（Search Console ドメインプロパティ用・★消すと所有確認が外れる）。SPF の行と別行
- **戻し方は上の値へ戻すだけ**（A・AAAA・www の3つ）。MX は www1094 のままでも動く

## どこに置くかの判断（2026-08-22）

| | 当方が更新できるか | 有璽氏の手数 |
|---|---|---|
| **Vercel＋CNAME** | **できる**（deployするだけ） | login 1回 ＋ CNAME 1行 |
| さくらのサーバへ直接 | ×（FTP情報が無い。毎回人の手） | サブドメイン追加のみ（DNS不要） |

**更新が続くものは Vercel 側に置く。** LPは訴求別の出し分けや第2波の派生で必ず触るため。
→ [[project_gamebull_form_sales]]
