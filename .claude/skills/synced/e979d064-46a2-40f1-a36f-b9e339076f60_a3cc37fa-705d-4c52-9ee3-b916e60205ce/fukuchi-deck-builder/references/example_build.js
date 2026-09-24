/**
 * example_build.js — 企業向け17ページ構成の完成例
 *
 * このスキルの部品だけで実資料を組む実例。別の読者・構成を作るときの「型」として読む。
 * 実行: scripts/fukuchi_components.js への正しいパスで require し node 実行。
 *   node example_build.js  → /mnt/user-data/outputs/ に pptx 出力
 */
const path = require("path");
const F = require(path.join(__dirname, "../scripts/fukuchi_components.js"));

(async () => {
  const pres = F.newDeck({ title: "ふくち。グループ 全体資料（企業向け）" });

  // P1 表紙
  F.titleSlide(pres, {
    eyebrow: "FUKUCHI GROUP",
    title: "ふくち。グループ",
    subtitle: "企業向け 事業全体像・総合案内",
    tagline: "福祉・生活・金融・研究をつなぎ、人が前に進む社会をつくる。",
    footnote: "2026",
  });

  // P2 目次（番号リストを2系統で使う簡易版）
  let s = F.contentSlide(pres, "CONTENTS", "目次");
  F.bulletList(pres, s, [
    "本資料の目的／ふくち。グループとは／社会課題",
    "解決アプローチ／エコシステム",
    "送り出し型・地域・金融・教育研究の各連携モデル",
    "グループ会社紹介",
    "組織体制 Before → After",
    "実行ロードマップ／まとめ・会社概要",
  ], 2.2);
  F.brandFoot(s); F.pageNum(s, 2);

  // P3 本資料の目的
  s = F.contentSlide(pres, "PURPOSE", "本資料の目的");
  F.lead(s, "ふくち。グループの事業全体像と、企業・行政・金融機関との連携可能性を明確にするための総合案内です。");
  F.bulletList(pres, s, [
    "福祉・生活・金融・研究を統合したエコシステムの理解",
    "送り出し型福祉モデルの価値と社会的インパクトの共有",
    "地域・企業・行政との協働領域の提示／組織構造の可視化",
    "今後の事業展開・ロードマップの共有",
  ], 3.0);
  F.bandBox(pres, s, "ふくち。グループが目指す「人が前に進む社会」を、共に創るパートナーを求めています。",
    { fill: F.BRAND.sand, y:5.65, h:0.6 });
  F.brandFoot(s); F.pageNum(s, 3);

  // P4 ふくち。グループとは（濃色）
  s = F.contentSlide(pres, "ABOUT US", "ふくち。グループとは", true);
  F.lead(s, "「境界を耕す。」をミッションに掲げ、福祉・生活・金融・研究の領域を横断しながら、人が前に進むための環境づくりを行う組織です。", true);
  F.bulletList(pres, s, [
    "生きづらさを抱える人が、前に進める社会をつくる",
    "支援と経済をつなぎ、持続可能な仕組みをつくる",
    "地域・企業・行政と協働し、価値循環を生み出す",
    "個人の可能性を最大化する「送り出し型福祉」を実装する",
  ], 3.3, true);
  F.pageNum(s, 4);

  // P5 社会課題
  s = F.contentSlide(pres, "SOCIAL ISSUE", "社会課題：福祉・生活・金融の断絶");
  F.lead(s, "支援が必要な人ほど福祉・生活・金融・研究が分断され、必要な支援が届かない構造が続いています。");
  F.cards(pres, s, [
    { head:"福祉", body:"生活再建・就労支援とつながりにくい" },
    { head:"生活", body:"困窮が金融リテラシー不足と負債を生む" },
    { head:"金融", body:"福祉領域の実態を把握しづらい" },
    { head:"研究", body:"データが現場に還元されにくい" },
  ], { y:2.85, h:2.2 });
  F.bandBox(pres, s, ["この断絶が“支援が続かない”“前に進めない”負の循環を生む。",
    "ふくち。グループは、この分断をつなぎ直すことから始めます。"], { y:5.45, h:1.0 });
  F.brandFoot(s); F.pageNum(s, 5);

  // P6 解決アプローチ
  s = F.contentSlide(pres, "OUR APPROACH", "解決アプローチ");
  F.lead(s, "福祉・生活・金融・研究を一つのエコシステムとして統合し、「送り出し型福祉」を中心に据えた循環モデルを構築します。");
  F.cards(pres, s, [
    { head:"① 福祉", body:"個別支援・生活再建・自立支援", color:F.BRAND.deep },
    { head:"② 生活", body:"住まい・就労・日常サポート", color:F.BRAND.teal },
    { head:"③ 金融", body:"家計改善・負債整理・金融教育", color:F.BRAND.green },
    { head:"④ 研究", body:"データ分析・効果検証・政策提言", color:F.BRAND.gold },
  ], { y:2.85, h:2.55 });
  F.brandFoot(s); F.pageNum(s, 6);

  // P7 エコシステム（循環図）
  s = F.contentSlide(pres, "ECOSYSTEM", "事業全体像（エコシステム）");
  s.addText("「送り出し型福祉」を中心に、福祉・生活・金融・研究を統合した循環型エコシステム。支援 → 生活 → 金融 → 研究 → 支援 の循環を生み出します。",
    { x:0.85, y:1.85, w:4.2, h:3.4, fontFace:F.FONT, fontSize:14, color:F.BRAND.ink, lineSpacing:24, margin:0 });
  F.cycleDiagram(pres, s,
    { label:"ふくち。", sub:"送り出し型福祉" },
    [
      { label:"生活支援（ビビッド）", sub:"住まい／就労／生活" },
      { label:"金融サポート", sub:"家計／金融教育" },
      { label:"研究・データ", sub:"SWELLSOCIETY" },
      { label:"地域連携", sub:"行政／企業／NPO" },
    ]);
  F.brandFoot(s); F.pageNum(s, 7);

  // P8 送り出し型福祉モデル
  s = F.contentSlide(pres, "MODEL 01", "送り出し型福祉モデル");
  s.addText("支援を終わらせる福祉ではなく、支援を続けながら前に進める福祉。施設を出た後も各領域が連携し、支援が途切れず循環する構造をつくります。",
    { x:0.85, y:1.85, w:4.2, h:3.4, fontFace:F.FONT, fontSize:14, color:F.BRAND.ink, lineSpacing:24, margin:0 });
  F.cycleDiagram(pres, s,
    { label:"ふくち。", sub:"送り出し型福祉" },
    [
      { label:"支援フェーズ", sub:"生活・就労・相談" },
      { label:"送り出し", sub:"地域・企業・金融" },
      { label:"再支援・研究", sub:"効果検証・改善" },
      { label:"自立・社会参加", sub:"定着・キャリア" },
    ]);
  F.brandFoot(s); F.pageNum(s, 8);

  // P9 地域連携モデル
  s = F.contentSlide(pres, "MODEL 02", "地域連携モデル");
  s.addText("送り出し型福祉を地域社会全体に広げる協働構造。行政・企業・NPO・地域住民が強みを持ち寄り、地域循環を支えます。",
    { x:0.85, y:1.85, w:4.2, h:3.4, fontFace:F.FONT, fontSize:14, color:F.BRAND.ink, lineSpacing:24, margin:0 });
  F.cycleDiagram(pres, s,
    { label:"ふくち。", sub:"送り出し型福祉" },
    [
      { label:"行政", sub:"制度・公的連携" },
      { label:"企業", sub:"雇用・協働事業" },
      { label:"NPO・地域団体", sub:"現場ネットワーク" },
      { label:"地域住民", sub:"参加・見守り" },
    ]);
  F.brandFoot(s); F.pageNum(s, 9);

  // P10 金融連携モデル（核＝ビビッド）
  s = F.contentSlide(pres, "MODEL 03", "金融連携モデル");
  s.addText("経済的自立を最終ゴールにせず、支援が続く経済循環として設計。ビビッドを核に、福祉・生活・研究と協働します。",
    { x:0.85, y:1.85, w:4.2, h:3.4, fontFace:F.FONT, fontSize:14, color:F.BRAND.ink, lineSpacing:24, margin:0 });
  F.cycleDiagram(pres, s,
    { label:"ビビッド", sub:"金融連携の核" },
    [
      { label:"金融教育", sub:"知識・リテラシー" },
      { label:"家計改善", sub:"支出管理・相談" },
      { label:"負債整理", sub:"再生・再構築" },
      { label:"資金循環", sub:"地域・企業・支援機関" },
    ]);
  F.brandFoot(s); F.pageNum(s, 10);

  // P11 教育・研究連携モデル
  s = F.contentSlide(pres, "MODEL 04", "教育・研究連携モデル（SWELLSOCIETY）");
  s.addText("グループ全体をエビデンスで支える学術基盤。SWELLSOCIETY（リアンライフ）が「現場→データ→研究→改善→現場」の循環を生みます。",
    { x:0.85, y:1.85, w:4.2, h:3.4, fontFace:F.FONT, fontSize:14, color:F.BRAND.ink, lineSpacing:24, margin:0 });
  F.cycleDiagram(pres, s,
    { label:"SWELL", sub:"研究・学術基盤" },
    [
      { label:"データ分析", sub:"統計・可視化" },
      { label:"効果検証", sub:"アウトカム評価" },
      { label:"政策提言", sub:"行政・学会" },
      { label:"モデル改善", sub:"現場フィードバック" },
    ]);
  F.brandFoot(s); F.pageNum(s, 11);

  // P12 グループ会社紹介（役割を実態に整合）
  s = F.contentSlide(pres, "GROUP COMPANIES", "グループ会社紹介");
  F.lead(s, "4社がそれぞれ独自の専門領域を持ちながら相互に連携し、人の生活を支える仕組みを形成しています。");
  F.cards(pres, s, [
    { head:"株式会社ふくち。", sub:"統括・相談支援", lines:["生活支援・相談支援","経営支援（福祉事業者向け）","地域連携のハブ機能"], color:F.BRAND.accent },
    { head:"株式会社ビビッド", sub:"金融・資金調達", lines:["資金調達支援（補助金・融資）","金融教育・資産形成","家計改善プログラム"], color:F.BRAND.deep },
    { head:"株式会社ILIFE", sub:"福祉現場運営", lines:["就労支援・現場連携","生活再建支援","支援データの収集・分析"], color:F.BRAND.green },
    { head:"SWELLSOCIETY", sub:"研究・学術連携", lines:["研究・効果検証","データ分析","政策提言・モデル改善"], color:F.BRAND.purple },
  ], { y:2.75, h:3.65 });
  F.brandFoot(s); F.pageNum(s, 12);

  // P13 組織 Before
  s = F.contentSlide(pres, "ORGANIZATION — BEFORE", "現行組織（Before）");
  F.lead(s, "多様な機能が縦割りで構成されている現状の体制。");
  F.orgChart(pres, s,
    { label:"CEO\n田村 有璽" },
    ["経営企画","事業開発","マーケ","営業","管理","施設運営"],
    { title:"グループ会社", items:["ILIFE","SWELLSOCIETY","LIFE STAND UP","オレンジワークス藤井寺"] });
  F.brandFoot(s); F.pageNum(s, 13);

  // P14 進化ポイント（比較表）
  s = F.contentSlide(pres, "TRANSFORMATION", "進化ポイント（Before → After）");
  F.lead(s, "単なる再編ではなく「縦割りから横断連携へ」「支援から社会的循環へ」の構造転換です。");
  F.comparisonTable(pres, s, [
    ["観点","Before（現行）","After（v2.0）"],
    ["組織構造","縦割り型（部門ごとに独立）","横断連携型（本部間が連携）"],
    ["経営体制","各部門ごとの管理","統合マネジメント（経営本部）"],
    ["事業連携","部門間連携が限定的","支援・教育・研究・金融が統合"],
    ["データ活用","各部門で個別管理","SWELLSOCIETYによる統合分析"],
    ["社会的インパクト","現場中心の支援","社会循環モデルの創出"],
    ["外部連携","グループ内中心","行政・企業・大学との協働拡大"],
  ]);
  F.brandFoot(s); F.pageNum(s, 14);

  // P15 ロードマップ
  s = F.contentSlide(pres, "ROADMAP", "実行ロードマップ（3ヶ月／半年／1年）");
  F.lead(s, "「体制整備 → 運用開始 → 社会展開」の段階的進化を実現します。");
  F.roadmap(pres, s, [
    { tag:"Phase 1", period:"0〜3ヶ月｜準備・設計期", body:"v2.0体制発足／責任者任命／業務フロー設計／ブランド統合", kpi:"新組織稼働率80%・業務設計完了", color:F.BRAND.deep },
    { tag:"Phase 2", period:"4〜6ヶ月｜運用・連携期", body:"本部間連携の実運用／モデル連動／データ収集／外部連携試行", kpi:"連携3件以上・分析レポート初版", color:F.BRAND.teal },
    { tag:"Phase 3", period:"7〜12ヶ月｜展開・拡張期", body:"全国展開準備／FC試験導入／投資家・行政向け報告／成果発表", kpi:"FC1拠点稼働・インパクト指標公開", color:F.BRAND.green },
  ]);
  F.brandFoot(s); F.pageNum(s, 15);

  // P16 まとめ＋会社概要
  F.closingSlide(pres,
    { title:"企業と共に創る未来",
      body:"「人の生活を支える事業を、ひとつのエコシステムとして統合する。」という理念のもと、福祉・教育・金融・研究を横断的に結び、社会課題の解決を“共創”で進めます。",
      closing:"誰もが安心して挑戦できる社会を、“送り出し型福祉”を通じて形にしていきます。" },
    [
      ["会社名","株式会社ふくち。"],
      ["代表者","田村 有璽"],
      ["所在地","大阪府藤井寺市（詳細は別途）"],
      ["設立","2026年"],
      ["事業内容","福祉事業／教育支援／金融リテラシー推進／研究開発"],
      ["グループ構成","ふくち。／ビビッド／ILIFE／SWELLSOCIETY（リアンライフ）"],
    ]);

  const out = "/mnt/user-data/outputs/ふくち。グループ_全体資料_企業向け.pptx";
  await F.save(pres, out);
  console.log("BUILD OK:", out);
})().catch(e => { console.error("BUILD ERR:", e); process.exit(1); });
