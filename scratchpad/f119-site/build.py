# 福祉施設の119番 Webサイト（7ページ）を public/ に書き出す。共通のヘッダー・フッターをここで1か所にまとめる。
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")
CAL = "https://calendar.app.google/c5aJoxPMVB5brw9b8"
PARTNERS = "https://fukushi119-partners.vercel.app/"
IRYO = "https://iryo.vivid-global.com/"
MAIL = "sales-consulting@vivid-global.com"
# 計測セット（bin/web_tracking/snippet.html v2）。SB・GTM は自社共通、Clarity はこのサイト専用
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRACK = {"{{SB_TRACK_ID}}": "17e298ff-5e02-4630-a16d-0f4f25ede23a", "{{SB_TRACK_TOKEN}}": "8d63c4ed-05b5-4cd8-90cd-d1a8a89e947b",
         "{{GTM_ID}}": "GTM-PQX3L4TQ", "{{CLARITY_ID}}": "z46d8rwt4j"}
with open(os.path.join(REPO, "bin/web_tracking/snippet.html"), encoding="utf-8") as f:
    SNIPPET = f.read()
for k, v in TRACK.items():
    SNIPPET = SNIPPET.replace(k, v)

NAV = [("index.html", "トップ"), ("service.html", "サービス"), ("price.html", "料金"),
       ("flow.html", "導入の流れ"), ("about.html", "わたしたち"), ("faq.html", "よくある質問")]


def cal_btn(label, cta, cls="cta", extra=""):
    return f'<a class="btn {cls}{extra}" href="{CAL}" target="_blank" rel="noopener" data-cta="{cta}">{label}</a>'


def head(title, desc, cur):
    nav = "".join(f'<a href="{h}"{" aria-current=\"page\"" if h == cur else ""}>{t}</a>' for h, t in NAV)
    nav += f'<a href="{PARTNERS}" class="ext" data-cta="nav-partners">解決パートナー</a>'
    full = "福祉施設の119番" if cur == "index.html" else f"{title}｜福祉施設の119番"
    return f'''<!doctype html>
<html lang="ja">
<head>
<!--TRACKING-->
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<title>{full}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="assets/logo/fukushi119_logo_symbol_fullcolor.svg" type="image/svg+xml">
<link rel="stylesheet" href="css/styles.css">
<link rel="stylesheet" href="css/site.css">
</head>
<body>
<header class="hdr"><div class="wrap">
  <a class="logo" href="index.html"><img src="assets/logo/119ban-logo-tight.jpg" alt="福祉施設の119番 WELFARE FACILITY RESCUE LINE" width="200" height="42"></a>
  <nav class="nav" aria-label="サイト内">{nav}</nav>
  <a class="btn cta sm hdr-cta" href="{CAL}" target="_blank" rel="noopener" data-cta="header">無料相談を予約</a>
</div></header>
<main>
'''


def foot():
    links = "".join(f'<li><a href="{h}">{t}</a></li>' for h, t in NAV)
    return f'''</main>
<footer class="ftr">
  <div class="wrap top">
    <div class="brand">
      <img src="assets/logo/119ban-logo-white-tight.jpg" alt="福祉施設の119番" width="190" height="40">
      <p>放課後等デイサービス・児童発達支援・就労継続支援の運営法人さま向けの経営支援サービスです。<br>記載の金額はすべて税別です。</p>
    </div>
    <div><h4>SITE MAP</h4><ul>{links}<li><a href="contact.html">無料相談・お問い合わせ</a></li></ul></div>
    <div><h4>RELATED</h4><ul>
      <li><a href="{PARTNERS}" data-cta="footer-partners">解決パートナー</a></li>
      <li><a href="{IRYO}" target="_blank" rel="noopener">医療連携体制構築支援</a></li>
      <li>運営：株式会社ビビッド（ふくち。グループ）</li>
      <li>大阪市北区梅田1-1-3 大阪駅前第3ビル 29階</li>
    </ul></div>
  </div>
  <div class="bottom"><div class="wrap">
    <div class="id"><img src="assets/logo/fukushi119_logo_symbol_white.svg" alt="">福祉施設の119番<span class="sep">｜</span>ふくち。グループ／株式会社ビビッド</div>
    <div class="c">© 2026 VIVID Inc. ／ FUKUCHI GROUP</div>
  </div></div>
</footer>
</body>
</html>
'''


def sub_hero(eyebrow, title, lead):
    return f'''<section class="hero sub">
  <img class="sym" src="assets/logo/fukushi119_logo_symbol_white.svg" alt="">
  <div class="wrap inner">
    <div class="bar"></div>
    <div class="eyebrow">{eyebrow}</div>
    <h1>{title}</h1>
    <p class="lead">{lead}</p>
  </div>
</section>
'''


def sh(eyebrow, title, lead=""):
    l = f'<p class="lead">{lead}</p>' if lead else ""
    return f'<div class="sh"><div class="eyebrow">{eyebrow}</div><h2>{title}</h2>{l}</div>'


def cta_section(eyebrow="CONTACT", title="まずは、現在地を知ることから",
                lead="健康診断のご相談、過去の分の扱い、月額サービスの構成。どの段階のご相談でも構いません。率直なご状況をお聞かせください。", cta="band"):
    return f'''<section class="sec navy"><div class="wrap">
  {sh(eyebrow, title, lead)}
  <div class="btnrow">{cal_btn("無料相談を予約する（30分・オンライン）", cta, "cta", " lg")}<a class="btn on-dark" href="contact.html">お問い合わせ</a></div>
  <p class="small" style="margin-top:16px;color:var(--text-on-dark-muted)">予約フォームが開きます。ご都合のよい日時をお選びください。</p>
</div></section>
'''


def steps(rows):
    out = '<div class="steps">'
    for no, name, label, desc, when in rows:
        lab = ""
        if label:
            tone, txt = label
            lab = f'<span class="lbl {tone}">{txt}</span>'
        d = f'<span class="desc">{desc}</span>' if desc else ""
        out += f'<div class="step"><div class="rail"></div><div class="no">{no}</div><div class="main"><div class="name">{name}{lab}</div>{d}</div><div class="when">{when}</div></div>'
    return out + "</div>"


PAGES = {}

# ---------------- トップ ----------------
CHECKS = ['個別支援計画の期限切れ', '計画の作成手順の不備', '常勤換算の計算誤り', '提供時間帯の配置不足', '児発管／サビ管の要件・兼務違反',
          '加配加算の要件不備', '専門的支援加算の不備', '支援記録の記載漏れ', '自己評価の未公表', '契約・重説の書類不備']
sc_buttons = "".join(f'<button type="button" aria-pressed="false" data-sc><span class="num">{i+1:02d}</span><span class="dot"></span><span>{c}</span></button>' for i, c in enumerate(CHECKS))

PAGES["index.html"] = ("トップ", "放課後等デイサービス・児童発達支援・就労継続支援の運営法人さま向け。施設運営の健康診断を入口に、過去の是正と、これからの運営改善までを一体でご支援します。", f'''
<section class="hero">
  <img class="bg" src="assets/photo/field-staff.jpg" alt="">
  <div class="scrim"></div>
  <div class="wrap inner">
    <div class="bar"></div>
    <div class="eyebrow">WELFARE FACILITY RESCUE LINE</div>
    <h1>実地指導は、<br>必ず来ます。</h1>
    <p class="lead">施設運営の健康診断を入口に、過去の是正と、これからの運営改善までを一体でご支援します。設計しているのは、放課後等デイサービスと就労継続支援B型を自ら運営している事業者です。</p>
    <div class="actions">{cal_btn("無料相談を予約する", "hero", "cta-large")}<a class="btn on-dark" href="service.html">サービスを見る</a></div>
    <p class="hnote">健康診断はオンライン完結・最短2週間・3万円〜／事業所（税別）</p>
  </div>
</section>

<section class="sec tight"><div class="wrap">
  <div class="stats">
    <div class="stat"><div class="v">約40<small>年</small></div><div class="k">地域福祉に関わってきた年月</div><p class="n">親子二代・NPO活動を出発点に</p></div>
    <div class="stat"><div class="v">約10<small>年</small></div><div class="k">福祉施設の運営実績</div><p class="n">放課後等デイ・就労継続支援B型を直営</p></div>
    <div class="stat"><div class="v">3<small>つ</small></div><div class="k">運営指導・BPO・採用を1社で</div><p class="n">窓口がひとつ。3つの情報がつながる</p></div>
    <div class="stat"><div class="v" style="font-family:var(--font-sans)">産学連携</div><div class="k">大学との共同研究</div><p class="n">発達障害と金銭課題の調査研究</p></div>
  </div>
</div></section>

<section class="sec sand"><div class="wrap">
  {sh("REALITY CHECK", "「まだ来ていない」は、安心材料ではありません", "実地指導（運営指導）は概ね3年に1回、全事業所が対象です。こども家庭庁への移管、報酬改定、事業所の急増、オンライン活用。指導を取り巻く環境は、確認項目が増える方向に動いています。")}
  <div class="cards c3">
    <div class="bc"><div class="no">01</div><h3>最大5年の遡及返還義務</h3><div class="body">誤算定は過去分までまとめて返還対象になります。</div></div>
    <div class="bc"><div class="no">02</div><h3>+40％ 不正請求の加算金</h3><div class="body">返還額にさらに上乗せされます。</div></div>
    <div class="bc"><div class="no">03</div><h3>事業者名まで公表</h3><div class="body">信用・採用にも影響が及びます。</div></div>
  </div>
  <div class="split" style="margin-top:48px">
    <div class="stack">
      <h3 style="font-size:var(--fs-h3);color:var(--f119-navy)">返還額のシミュレーション</h3>
      <p class="small muted">児童指導員等加配加算 月37万円分の誤算定・定員10名モデル</p>
      <div class="tbl"><table style="min-width:0"><thead><tr><th>発覚の時期</th><th>返還額の目安</th></tr></thead><tbody>
        <tr><td>1年で発覚</td><td class="num">約450万円</td></tr>
        <tr><td>3年で発覚</td><td class="num">約1,350万円</td></tr>
        <tr><td>5年で発覚</td><td class="num">約2,240万円</td></tr>
        <tr><td>＋加算金40%</td><td class="num">約3,140万円</td></tr>
      </tbody></table></div>
      <p class="small muted">返還請求 約7,400万円の公表事例も（政令市）</p>
    </div>
    <div class="stack">
      <div class="eyebrow">ROOT CAUSE</div>
      <h3 style="font-size:24px;font-weight:500;color:var(--f119-navy);line-height:1.5">悪意がなくても、「不正請求」になり得ます。</h3>
      <p>指摘の原因は、当日ではなく日常業務にあります。計画の期限切れは日々の書類運用、常勤換算の誤りは毎月のシフト管理、加算要件の不備は毎月の請求業務。児発管に属人化した運用は、退職や異動で一気に崩れます。</p>
      <div class="concl"><p>だから、まず点検で現状を知り、日常業務そのものを外部化する。これが恒久対策です。</p></div>
    </div>
  </div>
</div></section>

<section class="sec"><div class="wrap">
  {sh("SELF CHECK", "よくある指摘事項 TOP10。いくつ該当しますか", "気になる項目を押してください。3つ以上なら、至急の是正をおすすめします。")}
  <div class="sc" id="sc">{sc_buttons}</div>
  <div class="verdict" aria-live="polite"><div class="cnt"><span id="sc-n">0</span><small>個 該当</small></div><div><div class="t" id="sc-t">現状維持でも大丈夫そうです</div><div class="b" id="sc-b">年1回の点検で、この状態を維持していきましょう。</div></div></div>
  <div class="btnrow">{cal_btn("まず健康診断について相談する", "selfcheck", "primary")}</div>
</div></section>

<section class="sec sand"><div class="wrap">
  {sh("SERVICE MAP", "点検を入口に、過去の是正と、これからの運営改善", "福祉施設の119番は、ご相談の窓口です。ここを起点に、過去と未来の両方をご支援します。")}
  <div class="cards c3">
    <div class="bc"><div class="no">01 ／ ENTRY ＝ 健康診断</div><h3>施設運営の健康診断</h3><div class="body">書類をデータで送るだけ。指定権者の視点で人員・運営・報酬請求の3領域を点検し、2週間で貴社の現在地をお返しします。</div><div class="meta">3万円〜／事業所（税別）</div><a class="more" href="service.html#entry">詳しく見る</a></div>
    <div class="bc"><div class="no">02 ／ THE PAST ＝ 治療</div><h3>遡及点検・是正支援</h3><div class="body">「これまでの分が不安で、前に進めない」。その状態をまず解消します。不備の洗い出しと重要度判定、自主点検報告書の作成支援、過誤調整・自主返還の判断支援まで。</div><div class="meta">別途お見積り</div><a class="more" href="service.html#past">詳しく見る</a></div>
    <div class="bc"><div class="no">03 ／ THE FUTURE ＝ かかりつけ医</div><h3>3つの月額サービス</h3><div class="body">運営指導コンサル、BPO（請求・電話・法定義務）、RPO（採用運用代行）。守り・実務・人材の3方向から、施設の経営を止める要因を解消します。</div><div class="meta">月額3万円〜（税別）</div><a class="more" href="service.html#future">詳しく見る</a></div>
  </div>
  <div class="note" style="margin-top:24px"><b>医療連携体制構築支援</b>　医療機関・訪問看護ステーションとの連携体制を整え、医療連携体制加算の算定開始までをご支援します。<a href="service.html#iryo">詳しく見る</a></div>
</div></section>

<section class="sec"><div class="wrap promo">
  <div>
    {sh("PARTNERS", "119番では解けないお悩みも、解ける会社へ", "人・お金・現場・経営者ご自身のこと。施設経営のお悩みごとに、解決できる協力企業とその想いを紹介する「解決パートナー」を準備しています。ご相談の窓口は119番ひとつです。")}
    <div class="btnrow" style="margin-top:0"><a class="btn secondary" href="{PARTNERS}" data-cta="promo-partners">解決パートナーを見る</a></div>
  </div>
  <div class="photo"><img src="assets/photo/partners.jpg" alt="施設経営者と協力企業の担当者が話し合う様子（イメージ）"><div class="cap-on">お悩みから、解ける会社へ</div></div>
</div></section>

<section class="sec sand"><div class="wrap">
  {sh("WHY US", "わたしたちは、福祉の現場を自ら運営している事業者です", "実地指導も請求も採用も、「受けてきた側」「やってきた側」の視点でご支援できます。")}
  <div class="cards c3">
    <div class="bc"><div class="no">01</div><h3>現場の運営者が、設計者</h3><div class="body">放課後等デイサービスと就労継続支援B型を直営。請求・電話・実地指導まで実体験しています。現場で使えるオペレーションを、そのまま外出しします。</div></div>
    <div class="bc"><div class="no">02</div><h3>親子二代・約40年の地域福祉</h3><div class="body">新規参入ではありません。地域福祉NPOの活動を出発点に、二代にわたり現場に関わり続けてきました。</div></div>
    <div class="bc"><div class="no">03</div><h3>大学との共同研究</h3><div class="body">現場の実感を、学術的な検証を伴う知見へ。研究者との共同研究に取り組んでいます。</div></div>
  </div>
  <div class="btnrow"><a class="btn secondary" href="about.html">わたしたちについて</a></div>
</div></section>
{cta_section()}
<script>
(function(){{
  var V=[["現状維持でも大丈夫そうです","年1回の点検で、この状態を維持していきましょう。"],["要点検","該当項目が返還リスクにつながる前に、書類ベースの健康診断をおすすめします。"],["至急、是正を","3つ以上の該当は、指摘の可能性が高い状態です。まず健康診断で現在地を確認してください。"]];
  var bs=document.querySelectorAll('[data-sc]');
  function upd(){{var n=0;bs.forEach(function(b){{if(b.getAttribute('aria-pressed')==='true')n++}});
    var v=n===0?V[0]:n<=2?V[1]:V[2];document.getElementById('sc-n').textContent=n;document.getElementById('sc-t').textContent=v[0];document.getElementById('sc-b').textContent=v[1];}}
  bs.forEach(function(b){{b.addEventListener('click',function(){{b.setAttribute('aria-pressed',b.getAttribute('aria-pressed')==='true'?'false':'true');upd();}})}});
}})();
</script>
''')

# ---------------- サービス ----------------
PAGES["service.html"] = ("サービス", "施設運営の健康診断・ドック、遡及点検・是正支援、3つの月額サービス（運営指導コンサル・BPO・RPO）、医療連携体制構築支援。", sub_hero("SERVICES", "点検を入口に、過去の是正と、これからの運営改善まで", "福祉施設の119番は、ご相談の窓口です。健康診断で現在地を知り、過去の分を整え、これからの運営を支えます。") + f'''
<section class="sec" id="entry"><div class="wrap">
  {sh("01 ／ ENTRY — BASIC CHECK", "まずは書類を送るだけ。2週間で、貴社の現在地が分かります", "新たな資料づくりは不要です。既存の書類だけで結構です。指摘リスクだけでなく、取得漏れ加算という収益の余地までお返しします。")}
  <div class="cards c3">
    <div class="bc"><div class="no">01</div><h3>オンラインで完結</h3><div class="body">現地訪問は不要。既存の書類をデータでお送りいただくだけです。</div></div>
    <div class="bc"><div class="no">02</div><h3>指定権者の視点で点検</h3><div class="body">人員基準・運営基準・報酬請求の3領域、計120項目超を、自治体の点検表に準拠して確認します。</div></div>
    <div class="bc"><div class="no">03</div><h3>現役の運営者が実施</h3><div class="body">実地指導を「受けてきた」当事者が、その経験をそのまま還元します。</div></div>
  </div>
  <div class="split" style="margin-top:48px">
    <div class="stack">
      <div class="eyebrow">SCOPE ／ 点検する3領域</div>
      <div class="tbl"><table style="min-width:0"><thead><tr><th>領域</th><th>主な確認項目</th></tr></thead><tbody>
        <tr><td>人員基準<br><span class="cap">約40項目</span></td><td>常勤換算／提供時間帯の配置／児発管の要件／資格・実務経験／勤務実態との突合</td></tr>
        <tr><td>運営基準<br><span class="cap">約50項目</span></td><td>個別支援計画／支援記録／契約・重要事項説明／虐待防止・身体拘束／自己評価の公表</td></tr>
        <tr><td>報酬請求<br><span class="cap">約30項目</span></td><td>基本報酬の区分／各種加算の要件／処遇改善加算／請求と記録の突合／過誤・返還の判断</td></tr>
      </tbody></table></div>
    </div>
    <div class="stack">
      <div class="eyebrow">DELIVERABLES ／ お返しするもの</div>
      <ul class="checklist">
        <li><b>指摘リスク点検結果</b><br><span class="small">該当箇所を重要度3段階で整理してご提示します</span></li>
        <li><b>返還リスク金額試算</b><br><span class="small">指摘ごとに、想定される返還額を金額で示します</span></li>
        <li><b>取得漏れ加算のご提案書</b><br><span class="small">現状で取得できていない加算を洗い出し、取得の道筋をご提案します</span></li>
      </ul>
      <p class="small muted">加算のご提案は費用に含まれます。届出・要件整備の実行支援のみ、別途お見積りです。</p>
    </div>
  </div>
  <div style="margin-top:48px">
    <div class="eyebrow" style="margin-bottom:12px">FLOW ／ 最短2週間で報告書まで</div>
    {steps([("STEP 1","事前書類調査",None,"","約1週間"),("STEP 2","点検（ドックは現地模擬調査）",None,"","半日〜1日"),("STEP 3","即日講評",None,"","当日"),("STEP 4","報告書納品・報告会",None,"","約1週間")])}
    <p class="small muted" style="margin-top:12px">健康診断＝書類のみ・オンライン ／ ドック＝現地訪問・当日演習まで。まずは健康診断から、でも構いません。</p>
  </div>
  <div class="cards" style="margin-top:32px">
    <div class="bc"><div class="no">ENTRY</div><h3>施設運営の健康診断（模擬実地指導・書類編）</h3><div class="body">オンライン完結・最短2週間。</div><div class="meta">30,000円／事業所（税別）</div></div>
    <div class="bc"><div class="no">ENTRY</div><h3>施設運営ドック（模擬実地指導・現地編）</h3><div class="body">現地訪問で模擬実地指導。当日のヒアリング演習から報告会まで。半日〜1日。</div><div class="meta">120,000円／事業所（税別）</div></div>
  </div>
</div></section>

<section class="sec sand" id="past"><div class="wrap">
  {sh("02 ／ THE PAST", "遡及点検・是正支援", "「これまでの分が不安で、前に進めない」。その状態をまず解消します。")}
  <div class="split">
    <div class="stack">
      <div class="eyebrow">できること</div>
      <ul class="checklist">
        <li>不備の洗い出しと重要度の判定</li>
        <li>是正可能な範囲の整理</li>
        <li>自主点検報告書の作成支援</li>
        <li>過誤調整・自主返還の判断支援</li>
        <li>今後の運用ルールへの反映</li>
      </ul>
      <p class="small muted">料金は別途お見積り。健康診断の結果を踏まえてご提示します。</p>
    </div>
    <div class="stack">
      <div class="eyebrow">できないこと</div>
      <div class="note warn"><b>わたしたちが行わないこと</b><ul class="checklist xlist" style="margin-top:8px;border-top:none">
        <li>支援記録・個別支援計画の後付け作成</li>
        <li>事実と異なる書類の作成</li></ul>
        <p class="small" style="margin-top:8px">既存の事実・記録にもとづいて整えます。無い記録を作ることはしません。</p></div>
    </div>
  </div>
</div></section>

<section class="sec" id="future"><div class="wrap">
  {sh("03 ／ THE FUTURE — MONTHLY", "守り・実務・人材。3つを1社で", "点検で是正した状態を、維持する。制度も現場も動き続けるためです。3つすべてを1社で受けられることが、わたしたちの特徴です。")}
  <div class="cards c3">
    <div class="bc"><div class="no">SERVICE 01 ／ 守り</div><h3>運営指導コンサル</h3><div class="body">制度対応を、任せられる状態に。<ul><li>月次顧問・随時相談</li><li>報酬改定フォロー</li><li>年1回の点検</li><li>実地指導当日の同席（別途）</li></ul></div><div class="meta">解決すること：制度対応の不安</div></div>
    <div class="bc"><div class="no">SERVICE 02 ／ 実務</div><h3>BPO（請求・電話・法定義務）</h3><div class="body">指摘TOP10の原因業務を、日常から代行。<ul><li>請求業務の完全代行</li><li>代表電話の一次受け</li><li>法定義務の管理</li><li>月次レポート</li></ul></div><div class="meta">解決すること：事務工数の逼迫（月45〜65時間／施設の削減）</div></div>
    <div class="bc"><div class="no">SERVICE 03 ／ 人材</div><h3>RPO（採用運用代行）</h3><div class="body">児発管・指導員の採用を、運用ごと代行。<ul><li>求人媒体の運用代行</li><li>スカウト送信</li><li>面接日程の調整</li><li>応募者対応</li></ul></div><div class="meta">解決すること：人材不足・欠員</div></div>
  </div>
  <div style="margin-top:40px">
    <div class="eyebrow" style="margin-bottom:12px">BPO ／ 3つのモジュール</div>
    <div class="tbl"><table><thead><tr><th>モジュール</th><th>内容</th><th>削減の目安</th></tr></thead><tbody>
      <tr><td>請求BPO</td><td>月次請求の完全代行／国保連への月次伝送・受給者証管理／上限管理事業者との連携／返戻・過誤対応・再請求／加算取得状況のモニタリング</td><td class="muted">月15〜20時間</td></tr>
      <tr><td>コールBPO</td><td>代表電話の一次受け（営業時間内）／保護者連絡の振り分け・一次対応／営業電話の遮断／重要案件のみエスカレーション</td><td class="muted">月20〜30時間</td></tr>
      <tr><td>コンプラBPO</td><td>法定研修の年間計画策定・実施管理／自己評価・保護者評価の実施と公表／BCP更新／実地指導（監査）対策の書類整備</td><td class="muted">月10〜15時間</td></tr>
    </tbody></table></div>
  </div>
  <div class="cards c3" style="margin-top:40px">
    <div class="bc"><div class="no">01</div><h3>窓口がひとつ</h3><div class="body">制度改正時の対応が一度で済みます。</div></div>
    <div class="bc"><div class="no">02</div><h3>採用と加算が連動</h3><div class="body">採った人材が加算要件を満たすかどうかまで確認します。</div></div>
    <div class="bc"><div class="no">03</div><h3>請求と運営が連動</h3><div class="body">算定の実態と記録の整合を維持します。</div></div>
  </div>
  <div class="note" style="margin-top:24px"><b>料金</b>　月額3万円〜（税別）。事業所数・利用者数・モジュールの組み合わせにより変動します。複数サービスの同時契約、2事業所目以降には割引があります。正式なお見積りは、健康診断の結果を踏まえてご提示します。<a href="price.html">料金を見る</a></div>
</div></section>

<section class="sec sand" id="iryo"><div class="wrap">
  {sh("MEDICAL COOPERATION", "医療連携体制構築支援", "医療連携体制加算は、障がい福祉事業所が医療機関や訪問看護ステーション等としっかり連携し、利用者さまの体調管理や医療的な支援が必要な場面にも対応できる体制を整えていることを評価する加算です。")}
  <div class="cards c3">
    <div class="bc"><div class="no">01</div><h3>利用者への支援強化</h3><div class="body">定期的に看護師が体調管理をすることで、利用者やそのご家族は安心感を得ることができます。</div></div>
    <div class="bc"><div class="no">02</div><h3>職員の負担軽減</h3><div class="body">利用者の健康管理や悩み相談をプロの看護師が受けることで、支援員の負担を軽減できます。</div></div>
    <div class="bc"><div class="no">03</div><h3>加算取得</h3><div class="body">利用者の健康管理に関する記録を適切に管理し、申請することで毎月加算を取得することができます。</div></div>
  </div>
  <div class="split" style="margin-top:48px">
    <div class="stack">
      <div class="eyebrow">SUPPORT ／ 連携のしくみ</div>
      <div class="flowmap">
        <div class="col"><div class="box">病院</div><div class="box navy">サポート本部</div><div class="box">訪問看護ステーション</div></div>
        <div class="arrows"><span>指示書の発行</span><span>連携サポート・システム提供</span><span>看護業務の提供</span></div>
        <div class="col"><div class="box teal">障がい福祉事業所</div></div>
      </div>
      <p class="small muted">サポート本部が病院・訪問看護ステーションとの連携をご支援します。</p>
    </div>
    <div class="stack">
      <div class="concl"><p>加算Ⅳ取得時の試算　最大 <strong>128</strong> 万円／1か月あたり</p></div>
      <p class="small muted">試算条件：対象人数16人・平均通所数20日／月・1単位10円（単価は自治体により異なります）。</p>
    </div>
  </div>
  <div style="margin-top:40px">
    <div class="eyebrow" style="margin-bottom:12px">FLOW ／ 導入開始までの流れ（最短約1か月）</div>
    {steps([("開始","契約締結",None,"ご契約後、準備に着手",""),("1〜2週目","利用者へのご説明",None,"同意書・アンケート回収（回収サポートあり）",""),("3週目","指示書の発行",None,"アンケート情報をもとに病院が各利用者分を発行",""),("4週目","面談・計画反映",None,"オンライン面談／個別支援計画へ反映",""),("完了","算定開始",None,"最短1か月ほどで準備が完了","")])}
  </div>
  <div class="btnrow"><a class="btn secondary" href="{IRYO}" target="_blank" rel="noopener" data-cta="iryo-lp">医療連携体制構築支援の詳しいページへ</a></div>
</div></section>
{cta_section(cta="band-service")}
''')

# ---------------- 料金 ----------------
PAGES["price.html"] = ("料金", "福祉施設の119番の料金。健康診断 30,000円／事業所、ドック 120,000円／事業所、運営指導コンサル 月50,000円など（税別）。", sub_hero("PRICE", "料金", "記載の金額はすべて税別です。正式なお見積りは、健康診断の結果を踏まえてご提示します。") + f'''
<section class="sec"><div class="wrap">
  {sh("ENTRY ／ 現状を知る", "まずは健康診断から")}
  <div class="tbl"><table><thead><tr><th>メニュー</th><th>内容</th><th>料金（税別）</th></tr></thead><tbody>
    <tr><td>施設運営の健康診断</td><td>模擬実地指導・書類編。オンライン完結・最短2週間。指摘リスク点検結果・返還リスク金額試算・取得漏れ加算のご提案書をお返しします</td><td class="num">30,000円／事業所</td></tr>
    <tr><td>施設運営ドック</td><td>模擬実地指導・現地編。現地訪問で半日〜1日。当日のヒアリング演習から報告会まで</td><td class="num">120,000円／事業所<br><span class="cap">2事業所目以降 80,000円</span></td></tr>
  </tbody></table></div>
  <p class="small muted" style="margin-top:12px">加算のご提案は費用に含まれます。届出・要件整備の実行支援のみ、別途お見積りです。</p>
</div></section>

<section class="sec sand"><div class="wrap">
  {sh("THE PAST ／ 過去を整える", "遡及点検・是正支援")}
  <div class="tbl"><table><thead><tr><th>メニュー</th><th>内容</th><th>料金（税別）</th></tr></thead><tbody>
    <tr><td>遡及点検・是正支援</td><td>不備の洗い出しと重要度の判定／是正可能な範囲の整理／自主点検報告書の作成支援／過誤調整・自主返還の判断支援／今後の運用ルールへの反映</td><td class="num">別途お見積り</td></tr>
  </tbody></table></div>
</div></section>

<section class="sec"><div class="wrap">
  {sh("THE FUTURE ／ これからを支える", "3つの月額サービス")}
  <div class="tbl"><table><thead><tr><th>メニュー</th><th>内容</th><th>料金（税別）</th></tr></thead><tbody>
    <tr><td>運営指導コンサル</td><td>月次顧問・随時相談／報酬改定フォロー／年1回の点検／実地指導当日の同席（別途）</td><td class="num">月50,000円</td></tr>
    <tr><td>BPO（請求・電話・法定義務）</td><td>請求BPO・コールBPO・コンプラBPO の3モジュール。事業所数・利用者数・組み合わせにより変動</td><td class="num">お見積り</td></tr>
    <tr><td>RPO（採用運用代行）</td><td>求人媒体の運用代行／スカウト送信／面接日程の調整／応募者対応</td><td class="num">月30,000円〜</td></tr>
  </tbody></table></div>
  <div class="note" style="margin-top:20px">複数サービスの同時契約、2事業所目以降には割引があります。料金は事業所単位です。</div>
</div></section>
{cta_section(title="構成とお見積りは、ご相談の中で", lead="事業所数・利用者数・お困りごとに合わせて、必要なものだけを組み合わせます。まずは30分のオンライン相談で、現在の状況をお聞かせください。", cta="band-price")}
''')

# ---------------- 導入の流れ ----------------
PAGES["flow.html"] = ("導入の流れ", "健康診断からご提案・契約、キックオフ、本稼働まで。最短4週間で本稼働します。", sub_hero("ONBOARDING", "導入の流れ。最短4週間で本稼働", "貴社の負担は、初期ヒアリング3時間程度のみ。現業務を止めずに切り替えられる設計です。") + f'''
<section class="sec"><div class="wrap">
  {sh("FROM CHECK TO OPERATION", "健康診断から本稼働まで")}
  {steps([("WEEK 0","健康診断",("navy","3万円〜"),"書類をお送りいただき、点検結果・返還リスク・取得漏れ加算をご報告。",""),
          ("WEEK 1","ご提案・契約",None,"貴社専用の構成・料金をご提示。NDA締結後、契約書を取り交わします。","ご検討期間あり"),
          ("WEEK 2–3","キックオフ",("teal","貴社負担：約3時間"),"受給者証・職員情報・運用ルールを共有。連絡フロー・電話番号も設計。",""),
          ("WEEK 4","本稼働",None,"各サービスの提供開始。月次レポートとレビュー会で改善。","ここから削減効果")])}
</div></section>

<section class="sec sand"><div class="wrap">
  {sh("BASIC CHECK FLOW", "健康診断・ドックの流れ", "最短2週間で報告書まで。健康診断＝書類のみ・オンライン ／ ドック＝現地訪問・当日演習まで。")}
  {steps([("STEP 1","事前書類調査",None,"","約1週間"),("STEP 2","点検（ドックは現地模擬調査）",None,"","半日〜1日"),("STEP 3","即日講評",None,"","当日"),("STEP 4","報告書納品・報告会",None,"","約1週間")])}
</div></section>

<section class="sec"><div class="wrap">
  {sh("WHAT WE ASK", "お願いすること")}
  <div class="cards c3">
    <div class="bc"><div class="no">01</div><h3>既存の書類をデータで</h3><div class="body">新たな資料づくりは不要です。既存の書類だけで結構です。</div></div>
    <div class="bc"><div class="no">02</div><h3>初期ヒアリング 約3時間</h3><div class="body">キックオフで受給者証・職員情報・運用ルールを共有いただきます。</div></div>
    <div class="bc"><div class="no">03</div><h3>月次のレビュー</h3><div class="body">本稼働後は月次レポートとレビュー会で改善を続けます。</div></div>
  </div>
</div></section>
{cta_section(cta="band-flow")}
''')

# ---------------- わたしたち ----------------
PAGES["about.html"] = ("わたしたち", "福祉施設の119番は、放課後等デイサービスと就労継続支援B型を自ら運営する株式会社ビビッド（ふくち。グループ）が運営しています。", sub_hero("ABOUT US", "わたしたちは、福祉の現場を自ら運営している事業者です", "実地指導も請求も採用も、「受けてきた側」「やってきた側」の視点でご支援できます。") + f'''
<section class="sec tight"><div class="wrap">
  <div class="stats">
    <div class="stat"><div class="v">約40<small>年</small></div><div class="k">地域福祉に関わってきた年月</div><p class="n">親子二代・NPO活動を出発点に</p></div>
    <div class="stat"><div class="v">約10<small>年</small></div><div class="k">福祉施設の運営実績</div><p class="n">放課後等デイ・就労継続支援B型を直営</p></div>
    <div class="stat"><div class="v">3<small>つ</small></div><div class="k">運営指導・BPO・採用を1社で</div><p class="n">窓口がひとつ。3つの情報がつながる</p></div>
    <div class="stat"><div class="v" style="font-family:var(--font-sans)">産学連携</div><div class="k">大学との共同研究</div><p class="n">発達障害と金銭課題の調査研究</p></div>
  </div>
</div></section>

<section class="sec sand"><div class="wrap">
  {sh("WHY US", "選ばれる3つの理由")}
  <div class="cards c3">
    <div class="bc"><div class="no">01</div><h3>現場の運営者が、設計者</h3><div class="body">放課後等デイサービスと就労継続支援B型を直営。請求・電話・実地指導まで実体験しています。現場で使えるオペレーションを、そのまま外出しします。</div></div>
    <div class="bc"><div class="no">02</div><h3>親子二代・約40年の地域福祉</h3><div class="body">新規参入ではありません。地域福祉NPOの活動を出発点に、二代にわたり現場に関わり続けてきました。</div></div>
    <div class="bc"><div class="no">03</div><h3>大学との共同研究</h3><div class="body">現場の実感を、学術的な検証を伴う知見へ。研究者との共同研究に取り組んでいます。</div></div>
  </div>
</div></section>

<section class="sec"><div class="wrap split">
  <div class="stack">
    <div class="eyebrow">REPRESENTATIVE</div>
    <h2 style="font-size:var(--fs-h2);font-weight:500;color:var(--f119-navy);line-height:1.5">田村 有璽</h2>
    <p class="small muted">代表取締役｜児童発達支援管理責任者・サービス管理責任者</p>
    <div class="concl"><p>書類の体裁を整えるだけの支援ではなく、施設が事業として続いていく状態そのものをご支援したい。</p></div>
    <p>放課後等デイサービス・就労継続支援B型の直営運営。事業の譲受・譲渡を経験。発達障害の当事者としての視点を持つ。</p>
    <p>指導する側の視点、経営する側の視点、そして支えるご家族の視点。自治体のアドバイザリー業務を歴任した外部アドバイザーを含む体制で、貴社を支援します。</p>
  </div>
  <div class="photo"><img src="assets/photo/field-staff.jpg" alt="自社運営の放課後等デイサービスの様子"><div class="cap-on">自社運営の放課後等デイサービス</div></div>
</div></section>

<section class="sec sand"><div class="wrap">
  {sh("COMPANY", "運営会社")}
  <div class="tbl"><table><tbody>
    <tr><td style="width:180px">運営会社</td><td>株式会社ビビッド（ふくち。グループ）</td></tr>
    <tr><td>代表者</td><td>代表取締役　田村 有璽</td></tr>
    <tr><td>所在地</td><td>大阪市北区梅田1-1-3 大阪駅前第3ビル 29階</td></tr>
    <tr><td>連絡先</td><td>{MAIL}</td></tr>
    <tr><td>運営実績</td><td>LIFE STAND UP（放課後等デイサービス）<br>オレンジワークス藤井寺（就労継続支援B型）</td></tr>
  </tbody></table></div>
</div></section>
{cta_section(cta="band-about")}
''')

# ---------------- よくある質問 ----------------
FAQ = [
    ("健康診断で現地への訪問は必要ですか？", "不要です。健康診断はオンラインで完結し、既存の書類をデータでお送りいただくだけです。現地訪問と当日演習まで行う「施設運営ドック」もご用意しています。"),
    ("どのくらいの期間で結果が分かりますか？", "健康診断は最短2週間で、貴社の現在地をお返しします（事前書類調査 約1週間／報告書納品・報告会 約1週間）。"),
    ("新しく資料を作る必要はありますか？", "ありません。既存の書類だけで結構です。"),
    ("何を点検しますか？", "人員基準・運営基準・報酬請求の3領域、計120項目超を、自治体の点検表に準拠して確認します。"),
    ("対象となるサービス種別は？", "放課後等デイサービス・児童発達支援・就労継続支援を運営する法人さまを対象としています。"),
    ("加算の提案は別料金ですか？", "加算のご提案は健康診断の費用に含まれます。届出・要件整備の実行支援のみ、別途お見積りです。"),
    ("過去の記録が足りない場合、作成してもらえますか？", "支援記録・個別支援計画の後付け作成や、事実と異なる書類の作成は行いません。既存の事実・記録にもとづいて、不備の洗い出し・是正可能な範囲の整理・自主点検報告書の作成支援などを行います。"),
    ("料金は税込ですか？", "記載の金額はすべて税別です。"),
    ("月額サービスを始めるまで、どのくらいかかりますか？", "健康診断から最短4週間で本稼働します。貴社のご負担は初期ヒアリング3時間程度のみです。"),
    ("相談は無料ですか？", "はい。無料相談（30分・オンライン）を予約フォームから承っています。"),
]
faq_html = "".join(f'<details><summary>{q}</summary><div class="a">{a}</div></details>' for q, a in FAQ)
PAGES["faq.html"] = ("よくある質問", "福祉施設の119番によくいただくご質問。健康診断の進め方、期間、料金、できないことなど。", sub_hero("FAQ", "よくある質問", "ここにないご質問は、無料相談でお気軽にお尋ねください。") + f'''
<section class="sec"><div class="wrap read">
  <div class="faq">{faq_html}</div>
</div></section>
{cta_section(cta="band-faq")}
''')

# ---------------- 無料相談 ----------------
PAGES["contact.html"] = ("無料相談・お問い合わせ", "福祉施設の119番への無料相談（30分・オンライン）のご予約とお問い合わせ。", sub_hero("CONTACT", "まずは、現在地を知ることから", "健康診断のご相談、過去の分の扱い、月額サービスの構成。どの段階のご相談でも構いません。率直なご状況をお聞かせください。") + f'''
<section class="sec"><div class="wrap split">
  <div class="stack">
    {sh("BOOKING", "無料相談を予約する", "30分・オンライン。予約フォームが開きます。ご都合のよい日時をお選びください。")}
    <div>{cal_btn("無料相談を予約する（30分・オンライン）", "contact", "cta", " lg")}</div>
    <div class="tbl" style="margin-top:24px"><table style="min-width:0"><tbody>
      <tr><td style="width:120px">運営</td><td>株式会社ビビッド（ふくち。グループ）</td></tr>
      <tr><td>所在地</td><td>大阪市北区梅田1-1-3 大阪駅前第3ビル 29階</td></tr>
      <tr><td>メール</td><td>{MAIL}</td></tr>
    </tbody></table></div>
  </div>
  <div class="stack">
    <div class="eyebrow">FORM ／ お問い合わせフォーム</div>
    <form class="form" id="cform" data-cta="contact-form">
      <label class="field" for="f-org"><span class="fl">法人名・事業所名<span class="lbl teal">必須</span></span><input class="input" id="f-org" name="org" required></label>
      <label class="field" for="f-name"><span class="fl">お名前<span class="lbl teal">必須</span></span><input class="input" id="f-name" name="name" required></label>
      <label class="field" for="f-mail"><span class="fl">メールアドレス<span class="lbl teal">必須</span></span><input class="input" id="f-mail" name="email" type="email" required></label>
      <label class="field" for="f-msg"><span class="fl">ご相談内容</span><textarea class="input" id="f-msg" name="message" rows="5"></textarea><span class="hint">直近の実地指導の時期、気になる加算など、分かる範囲で</span></label>
      <button class="btn primary lg full" type="submit">送信する</button>
      <div id="f-done" role="status" aria-live="polite"></div>
    </form>
  </div>
</div></section>
<script>
document.getElementById('cform').addEventListener('submit',function(e){{e.preventDefault();document.getElementById('f-done').innerHTML='<div class="done">試作のため送信はしません。</div>';}});
</script>
''')

for fn, (title, desc, body) in PAGES.items():
    with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
        f.write((head(title, desc, fn) + body + foot()).replace("<!--TRACKING-->", SNIPPET.strip(), 1))
for name, text in {"robots.txt": "User-agent: *\nDisallow: /\n", ".vercelignore": "*.md\n*.bak*\n",
                   "vercel.json": '{\n  "headers": [\n    { "source": "/(.*)", "headers": [ { "key": "X-Robots-Tag", "value": "noindex, nofollow" } ] }\n  ]\n}\n'}.items():
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(text)
print("wrote", len(PAGES), "pages")
