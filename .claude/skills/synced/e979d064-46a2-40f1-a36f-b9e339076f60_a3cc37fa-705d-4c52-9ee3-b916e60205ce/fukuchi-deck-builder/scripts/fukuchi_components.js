/**
 * fukuchi_components.js
 * ふくち。グループ専用 スライドデザイン部品ライブラリ
 *
 * 設計思想:
 *   - ブランド定数(配色・フォント)は BRAND に固定。これを書き換えるとブランドが壊れるため触らない。
 *   - 各部品は slide を受け取り、その上に描画して返す純粋な関数。構成は呼び出し側が自由に組む。
 *   - 全部品は PowerPoint ネイティブ図形で構築。生成後も PowerPoint 上で色・文言を編集できる。
 *
 * 使い方:
 *   const F = require('./fukuchi_components.js');
 *   const pres = F.newDeck();
 *   let s = F.titleSlide(pres, { title:'...', subtitle:'...', tagline:'...' });
 *   s = F.contentSlide(pres, 'KICKER', 'タイトル');
 *   F.cards(s, [...]); F.pageNum(s, 2);
 *   await F.save(pres, '/mnt/user-data/outputs/xxx.pptx');
 */
const pptxgen = require("pptxgenjs");

// ===== ブランド定数（固定。変更禁止） =====
const BRAND = {
  navy:   "0E2A47",  // 主役（タイトル・締め背景）
  deep:   "0B4F6C",
  teal:   "1C7293",
  sky:    "57A6C9",
  sand:   "F4F1EA",  // 明背景アクセント
  white:  "FFFFFF",
  ink:    "1E2A33",  // 本文
  sub:    "5C6B73",  // サブ文字
  accent: "E2733B",  // ふくち。オレンジ
  line:   "D8DEE2",
  green:  "3E8E7E",
  gold:   "D9A441",
  purple: "7A4FA3",
};
const FONT = "Noto Sans CJK JP";  // 環境に応じて 'Yu Gothic' 等に差し替え可
// ノードや本部の色を循環的に割り当てる標準パレット
const SERIES = [BRAND.deep, BRAND.green, BRAND.purple, BRAND.gold, BRAND.teal, BRAND.sub];

function _shadow(){ return { type:"outer", color:"0E2A47", blur:9, offset:3, angle:135, opacity:0.13 }; }

// ===== デッキ初期化 =====
function newDeck(meta){
  const pres = new pptxgen();
  pres.defineLayout({ name:"W16x9", width:13.333, height:7.5 });
  pres.layout = "W16x9";
  pres.author  = (meta && meta.author)  || "ふくち。グループ";
  pres.company = "FUKUCHI GROUP";
  pres.title   = (meta && meta.title)   || "ふくち。グループ 資料";
  return pres;
}

// ===== 共通フッター部品 =====
function pageNum(slide, n){
  slide.addText(String(n).padStart(2,"0"), {
    x:12.45, y:7.0, w:0.7, h:0.35, fontFace:FONT,
    fontSize:10, color:BRAND.sub, align:"right", margin:0
  });
}
function brandFoot(slide, onDark){
  slide.addText("FUKUCHI GROUP", {
    x:0.6, y:7.0, w:4, h:0.35, fontFace:FONT,
    fontSize:9.5, color: onDark ? "9FB3C8" : BRAND.sub, charSpacing:3, margin:0
  });
}

// ===== 1. 表紙スライド =====
// opts: { eyebrow, title, subtitle, tagline, footnote }
function titleSlide(pres, opts){
  const s = pres.addSlide(); s.background = { color:BRAND.navy };
  s.addShape(pres.shapes.OVAL, { x:8.7, y:-2.3, w:7.6, h:7.6, fill:{color:BRAND.deep} });
  s.addShape(pres.shapes.OVAL, { x:10.6, y:1.2, w:4.2, h:4.2, fill:{color:BRAND.teal} });
  s.addShape(pres.shapes.OVAL, { x:11.6, y:4.7, w:1.2, h:1.2, fill:{color:BRAND.accent} });
  s.addText(opts.eyebrow || "FUKUCHI GROUP", {
    x:0.9, y:1.55, w:8, h:0.5, fontFace:FONT, fontSize:16,
    color:BRAND.sky, bold:true, charSpacing:6, margin:0 });
  s.addText(opts.title, {
    x:0.85, y:2.15, w:9.5, h:1.5, fontFace:FONT, fontSize:opts.title && opts.title.length>10?44:56,
    color:BRAND.white, bold:true, margin:0 });
  if(opts.subtitle) s.addText(opts.subtitle, {
    x:0.9, y:3.55, w:9, h:0.6, fontFace:FONT, fontSize:22, color:BRAND.white, margin:0 });
  if(opts.tagline) s.addText(opts.tagline, {
    x:0.9, y:4.4, w:9.5, h:0.6, fontFace:FONT, fontSize:15, color:"C7D7E3", margin:0 });
  s.addText(opts.footnote || "2026", {
    x:0.9, y:6.6, w:4, h:0.4, fontFace:FONT, fontSize:12, color:"8FA9BF", charSpacing:3, margin:0 });
  return s;
}

// ===== 2. 本文スライドの枠（kicker + title） =====
// onDark=true で濃色背景。戻り値の slide に各部品を重ねる。
function contentSlide(pres, kicker, title, onDark){
  const s = pres.addSlide();
  s.background = { color: onDark ? BRAND.navy : BRAND.white };
  if(kicker) s.addText(kicker, {
    x:0.85, y:0.62, w:9, h:0.4, fontFace:FONT, fontSize:13,
    color: onDark ? BRAND.sky : BRAND.teal, bold:true, charSpacing:4, margin:0 });
  s.addText(title, {
    x:0.8, y:1.0, w:11.7, h:1.0, fontFace:FONT, fontSize:32,
    color: onDark ? BRAND.white : BRAND.navy, bold:true, margin:0 });
  return s;
}

// ===== 3. リード文（タイトル直下の説明段落） =====
function lead(slide, text, onDark){
  slide.addText(text, {
    x:0.85, y:1.9, w:11.6, h:0.8, fontFace:FONT, fontSize:15,
    color: onDark ? "C7D7E3" : BRAND.sub, lineSpacing:24, margin:0 });
}

// ===== 4. 番号付きリスト（目的・要点の列挙） =====
// items: ["項目", ...]   y0 既定 3.0  ※ pres を要する
function bulletList(pres, slide, items, y0, onDark){
  let y = (y0==null?3.0:y0);
  items.forEach((t,i)=>{
    slide.addShape(pres.shapes.OVAL, { x:0.85, y:y, w:0.42, h:0.42, fill:{color:BRAND.teal} });
    slide.addText(String(i+1).padStart(2,"0"), {
      x:0.85, y:y, w:0.42, h:0.42, fontFace:FONT, fontSize:12,
      color:BRAND.white, bold:true, align:"center", valign:"middle", margin:0 });
    slide.addText(t, {
      x:1.5, y:y-0.02, w:10.8, h:0.46, fontFace:FONT, fontSize:15,
      color: onDark?BRAND.white:BRAND.ink, valign:"middle", margin:0 });
    y += 0.62;
  });
}

// ===== 5. 強調バンド（結論・キーメッセージの帯） =====
// band は pres を要するため bandBox を使う
// fill が明色(sand/white)のときは文字を濃色に自動切替して可読性を担保する
function bandBox(pres, slide, lines, opts){
  opts = opts || {};
  const y = opts.y==null?5.45:opts.y;
  const h = opts.h==null?1.0:opts.h;
  const fill = opts.fill || BRAND.navy;
  const isLight = (fill===BRAND.sand || fill===BRAND.white || fill==="F4F1EA" || fill==="FFFFFF");
  const c1 = isLight ? BRAND.navy : BRAND.white;
  const c2 = isLight ? BRAND.sub  : BRAND.sky;
  slide.addShape(pres.shapes.RECTANGLE, { x:0.85, y:y, w:11.6, h:h, fill:{color:fill} });
  const arr = Array.isArray(lines)?lines:[lines];
  const runs = arr.map((ln,i)=>({
    text: ln, options: { breakLine: i<arr.length-1,
      color: i===0?c1:c2, bold:i===0, fontSize:i===0?14:13 } }));
  slide.addText(runs, { x:1.1, y:y, w:11.1, h:h, fontFace:FONT, valign:"middle",
    lineSpacing:22, margin:0 });
}

// ===== 6. カードグリッド（2〜4分割の特徴・サービス紹介） =====
// cards: [{ head, sub?, body?, lines?[], color? }]   colors未指定はSERIES自動割当
function cards(pres, slide, items, opts){
  opts = opts || {};
  const n = items.length;
  const top = opts.y==null?2.85:opts.y;
  const h = opts.h==null?3.0:opts.h;
  const gap = 0.17;
  const totalW = 11.6;
  const w = (totalW - gap*(n-1)) / n;
  let x = 0.85;
  items.forEach((c,i)=>{
    const col = c.color || SERIES[i % SERIES.length];
    slide.addShape(pres.shapes.RECTANGLE, { x:x, y:top, w:w, h:h, fill:{color:BRAND.sand}, shadow:_shadow() });
    slide.addShape(pres.shapes.RECTANGLE, { x:x, y:top, w:w, h: c.sub?0.85:0.08, fill:{color:col} });
    if(c.sub){
      slide.addText(c.head, { x:x+0.12, y:top+0.07, w:w-0.24, h:0.5, fontFace:FONT,
        fontSize:14, color:BRAND.white, bold:true, align:"center", valign:"middle", margin:0 });
      slide.addText(c.sub, { x:x+0.12, y:top+0.5, w:w-0.24, h:0.35, fontFace:FONT,
        fontSize:11, color:"F0F4F2", align:"center", margin:0 });
    } else {
      slide.addText(c.head, { x:x, y:top+0.28, w:w, h:0.55, fontFace:FONT,
        fontSize:19, color:BRAND.navy, bold:true, align:"center", margin:0 });
    }
    const bodyY = c.sub ? top+1.0 : top+0.95;
    if(c.lines){
      let ly = bodyY;
      c.lines.forEach(li=>{
        slide.addShape(pres.shapes.RECTANGLE, { x:x+0.22, y:ly+0.09, w:0.1, h:0.1, fill:{color:col} });
        slide.addText(li, { x:x+0.42, y:ly, w:w-0.6, h:0.7, fontFace:FONT,
          fontSize:11, color:BRAND.ink, lineSpacing:15, margin:0 });
        ly += 0.78;
      });
    } else if(c.body){
      slide.addText(c.body, { x:x+0.2, y:bodyY, w:w-0.4, h:h-(bodyY-top)-0.2,
        fontFace:FONT, fontSize:12.5, color:BRAND.ink, align:"center", lineSpacing:18, margin:0 });
    }
    x += w + gap;
  });
}

// ===== 7. 循環図（4ノードのループ。エコシステム・連携モデルの核） =====
// center:{label,sub}  nodes:[{label,sub,color?}]×4 (上→右→下→左)
// cx,cy 既定 9.15,4.0（左にテキストを置く構成を想定）
function cycleDiagram(pres, slide, center, nodes, cx, cy){
  cx = cx==null?9.15:cx;  cy = cy==null?4.0:cy;
  const nodeW=2.6, nodeH=1.25, Rx=2.62, Ry=2.0;
  const pos = [
    { x:cx-nodeW/2,      y:cy-Ry-nodeH/2 },
    { x:cx+Rx-nodeW/2,   y:cy-nodeH/2 },
    { x:cx-nodeW/2,      y:cy+Ry-nodeH/2 },
    { x:cx-Rx-nodeW/2,   y:cy-nodeH/2 },
  ];
  const arcR=1.62;
  [0,90,180,270].forEach(rot=>{
    slide.addShape(pres.shapes.ARC, {
      x:cx-arcR, y:cy-arcR, w:arcR*2, h:arcR*2, rotate:rot,
      line:{ color:BRAND.line, width:6, beginArrowType:"none", endArrowType:"triangle" },
      fill:{ type:"none" }, angleRange:[5,80] });
  });
  const cR=1.7;
  slide.addShape(pres.shapes.OVAL, { x:cx-cR/2, y:cy-cR/2, w:cR, h:cR, fill:{color:BRAND.accent}, shadow:_shadow() });
  slide.addText([
    { text:center.sub||"", options:{ breakLine:true, fontSize:10, color:"FCE4D2" } },
    { text:center.label, options:{ fontSize:19, color:BRAND.white, bold:true } },
  ], { x:cx-cR/2, y:cy-cR/2, w:cR, h:cR, fontFace:FONT, align:"center", valign:"middle", lineSpacing:22, margin:0 });
  nodes.slice(0,4).forEach((nd,i)=>{
    const col = nd.color || SERIES[i % SERIES.length];
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x:pos[i].x, y:pos[i].y, w:nodeW, h:nodeH, rectRadius:0.1, fill:{color:col}, shadow:_shadow() });
    slide.addText([
      { text:nd.label, options:{ breakLine:true, fontSize:14, color:BRAND.white, bold:true } },
      { text:nd.sub||"", options:{ fontSize:10, color:"EAF1F4" } },
    ], { x:pos[i].x+0.08, y:pos[i].y, w:nodeW-0.16, h:nodeH, fontFace:FONT,
      align:"center", valign:"middle", lineSpacing:16, margin:0 });
  });
}

// ===== 8. Before→After 比較表 =====
// rows: [["観点","Before","After"], ...] 先頭行がヘッダ
function comparisonTable(pres, slide, rows, opts){
  opts = opts || {};
  const tbl = rows.map((r,ri)=>{
    if(ri===0) return r.map(c=>({ text:c, options:{ fill:{color:BRAND.navy},
      color:BRAND.white, bold:true, fontSize:13, align:"center", valign:"middle" } }));
    return [
      { text:r[0], options:{ fill:{color:BRAND.sand}, color:BRAND.navy, bold:true, fontSize:12.5, valign:"middle" } },
      { text:r[1], options:{ color:BRAND.sub, fontSize:12, valign:"middle" } },
      { text:r[2], options:{ color:BRAND.ink, fontSize:12, bold:true, valign:"middle" } },
    ];
  });
  slide.addTable(tbl, {
    x:0.85, y:opts.y==null?2.55:opts.y, w:11.6,
    colW:opts.colW||[2.4,4.4,4.8], rowH:opts.rowH||0.56,
    border:{ pt:0.5, color:BRAND.line }, fontFace:FONT, margin:[2,8,2,8] });
}

// ===== 9. フェーズ／ロードマップ（3カラム想定） =====
// phases: [{ tag, period, body, kpi, color? }]
function roadmap(pres, slide, phases, opts){
  opts = opts || {};
  const n = phases.length;
  const top = opts.y==null?2.65:opts.y;
  const h = opts.h==null?3.85:opts.h;
  const gap = 0.21;
  const w = (11.6 - gap*(n-1)) / n;
  let x = 0.85;
  phases.forEach((p,i)=>{
    const col = p.color || SERIES[i % SERIES.length];
    slide.addShape(pres.shapes.RECTANGLE, { x:x, y:top, w:w, h:h, fill:{color:BRAND.sand}, shadow:_shadow() });
    slide.addShape(pres.shapes.RECTANGLE, { x:x, y:top, w:w, h:0.95, fill:{color:col} });
    slide.addText(p.tag, { x:x+0.2, y:top+0.1, w:w-0.4, h:0.35, fontFace:FONT,
      fontSize:15, color:BRAND.white, bold:true, margin:0 });
    slide.addText(p.period||"", { x:x+0.2, y:top+0.45, w:w-0.4, h:0.45, fontFace:FONT,
      fontSize:11.5, color:"F0F4F2", margin:0 });
    slide.addText("主な実行内容", { x:x+0.2, y:top+1.1, w:w-0.4, h:0.3, fontFace:FONT,
      fontSize:10.5, color:col, bold:true, margin:0 });
    slide.addText(p.body||"", { x:x+0.2, y:top+1.4, w:w-0.4, h:1.5, fontFace:FONT,
      fontSize:11, color:BRAND.ink, lineSpacing:16, margin:0 });
    if(p.kpi){
      slide.addShape(pres.shapes.LINE, { x:x+0.2, y:top+2.9, w:w-0.4, h:0, line:{color:BRAND.line, width:1} });
      slide.addText("KPI", { x:x+0.2, y:top+2.95, w:w-0.4, h:0.28, fontFace:FONT,
        fontSize:10.5, color:col, bold:true, margin:0 });
      slide.addText(p.kpi, { x:x+0.2, y:top+3.23, w:w-0.4, h:0.6, fontFace:FONT,
        fontSize:10, color:BRAND.sub, lineSpacing:14, margin:0 });
    }
    x += w + gap;
  });
}

// ===== 10. 組織図（CEO/トップ + 横並び部門 + 任意の下段） =====
// top:{label}  depts:[label,...]  sub:{title,items:[label,...]}|null
function orgChart(pres, slide, top, depts, sub){
  const cxTop = 6.67;
  slide.addShape(pres.shapes.OVAL, { x:cxTop-0.7, y:2.55, w:1.4, h:1.4, fill:{color:BRAND.accent}, shadow:_shadow() });
  slide.addText(top.label, { x:cxTop-0.7, y:2.55, w:1.4, h:1.4, fontFace:FONT,
    fontSize:12, color:BRAND.white, bold:true, align:"center", valign:"middle", margin:0 });
  slide.addShape(pres.shapes.LINE, { x:cxTop, y:3.95, w:0, h:0.35, line:{color:BRAND.line, width:1.5} });
  const n = depts.length;
  const gap = 0.19;
  const dw = (11.6 - gap*(n-1)) / n;
  slide.addShape(pres.shapes.LINE, { x:0.85+dw/2, y:4.3, w:11.6-dw, h:0, line:{color:BRAND.line, width:1.5} });
  let x = 0.85;
  depts.forEach(d=>{
    slide.addShape(pres.shapes.LINE, { x:x+dw/2, y:4.3, w:0, h:0.25, line:{color:BRAND.line, width:1.5} });
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:x, y:4.55, w:dw, h:0.7, rectRadius:0.08, fill:{color:BRAND.deep} });
    slide.addText(d, { x:x+0.03, y:4.55, w:dw-0.06, h:0.7, fontFace:FONT,
      fontSize:12, color:BRAND.white, bold:true, align:"center", valign:"middle", margin:0 });
    x += dw + gap;
  });
  if(sub){
    slide.addText(sub.title||"グループ会社", { x:0.85, y:5.55, w:5, h:0.35, fontFace:FONT,
      fontSize:11, color:BRAND.sub, bold:true, margin:0 });
    const m = sub.items.length;
    const gw = (11.6 - gap*(m-1)) / m;
    let gx = 0.85;
    sub.items.forEach(g=>{
      slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x:gx, y:5.9, w:gw, h:0.65, rectRadius:0.08, fill:{color:BRAND.green} });
      slide.addText(g, { x:gx+0.03, y:5.9, w:gw-0.06, h:0.65, fontFace:FONT,
        fontSize:11.5, color:BRAND.white, bold:true, align:"center", valign:"middle", margin:0 });
      gx += gw + gap;
    });
  }
}

// ===== 11. 締め＋会社概要カード =====
// concl:{title,body,closing}  profile:[["項目","値"], ...]
function closingSlide(pres, concl, profile){
  const s = pres.addSlide(); s.background = { color:BRAND.navy };
  s.addShape(pres.shapes.OVAL, { x:-2.5, y:2.6, w:6.5, h:6.5, fill:{color:BRAND.deep} });
  s.addShape(pres.shapes.OVAL, { x:1.0, y:5.3, w:1.0, h:1.0, fill:{color:BRAND.accent} });
  s.addText("CONCLUSION", { x:0.85, y:0.7, w:8, h:0.4, fontFace:FONT,
    fontSize:13, color:BRAND.sky, bold:true, charSpacing:4, margin:0 });
  s.addText(concl.title, { x:0.8, y:1.1, w:7.5, h:1.0, fontFace:FONT,
    fontSize:34, color:BRAND.white, bold:true, margin:0 });
  s.addText(concl.body, { x:0.85, y:2.25, w:6.7, h:2.0, fontFace:FONT,
    fontSize:14, color:"D7E3EC", lineSpacing:24, margin:0 });
  if(concl.closing) s.addText(concl.closing, { x:0.85, y:4.35, w:6.7, h:1.0, fontFace:FONT,
    fontSize:14, color:BRAND.sky, italic:true, lineSpacing:22, margin:0 });
  if(profile){
    s.addShape(pres.shapes.RECTANGLE, { x:8.05, y:1.3, w:4.6, h:5.3, fill:{color:BRAND.white}, shadow:_shadow() });
    s.addShape(pres.shapes.RECTANGLE, { x:8.05, y:1.3, w:4.6, h:0.7, fill:{color:BRAND.accent} });
    s.addText("会社概要", { x:8.05, y:1.3, w:4.6, h:0.7, fontFace:FONT,
      fontSize:17, color:BRAND.white, bold:true, align:"center", valign:"middle", margin:0 });
    let py = 2.2;
    profile.forEach(p=>{
      s.addText(p[0], { x:8.3, y:py, w:4.1, h:0.28, fontFace:FONT,
        fontSize:10.5, color:BRAND.accent, bold:true, margin:0 });
      s.addText(p[1], { x:8.3, y:py+0.27, w:4.1, h:0.45, fontFace:FONT,
        fontSize:12, color:BRAND.ink, lineSpacing:15, margin:0 });
      py += 0.74;
    });
  }
  s.addText("FUKUCHI GROUP", { x:0.85, y:6.85, w:5, h:0.35, fontFace:FONT,
    fontSize:9.5, color:"8FA9BF", charSpacing:3, margin:0 });
  return s;
}

// ===== 保存 =====
async function save(pres, outPath){
  await pres.writeFile({ fileName: outPath });
  return outPath;
}

module.exports = {
  BRAND, FONT, SERIES,
  newDeck, save,
  titleSlide, contentSlide, lead, bulletList, bandBox,
  cards, cycleDiagram, comparisonTable, roadmap, orgChart, closingSlide,
  pageNum, brandFoot,
};
