// smartcontents.co.jp/estimate の compute() を条件だけ受け取る形に写したもの（2026-11-03 取得）
const R={dir:4000,write:3500,design:4500,code:4500,seo:4500,test:4000,photo:60000,wp:40000,ab:80000,lp_basic:15000,lp_full:36000,hp_basic:24000,hp_full:60000,server_h:4};
const DENS={s:.6,m:1,l:1.5},GD={tpl:.6,orig:1,high:1.6},GC={tpl:.8,orig:1,high:1.3};
function calc(s){const {kind,dens,grade:g,plan,write:wr,speed}=s;let p=kind==="lp"?1:s.pages;const O=id=>s.opts.includes(id);
const d=DENS[dens],us=wr!=="client",rush=speed==="r",E=d*(1+0.5*(p-1)),ceil=x=>Math.ceil(x-1e-9);const L=[];let wf=null;
L.push({item:"ディレクション",h:ceil(6+2*E+(kind==="hp"?4:kind==="lp"?2:0)),rate:R.dir});
if(us){if(kind==="add")L.push({item:"原稿",h:ceil((wr==="full"?12:6)*E),rate:R.write});else wf={item:"原稿",amt:R[kind+"_"+wr]};}
L.push({item:"デザイン",h:ceil(14*E*GD[g]+(plan==="2"?7*d*GD[g]:0)),rate:R.design});
let ch=14*E*GC[g];if(O("anim"))ch+=kind==="add"?0:2;if(O("form"))ch+=6;if(O("blog"))ch+=12;if(O("chat"))ch+=6;
L.push({item:"コーディング",h:ceil(ch),rate:R.code});
if(O("seo")||O("jp")){let sh=0;if(O("jp"))sh+=2;if(O("seo"))sh+=3+p;L.push({item:"検索対策",h:ceil(sh),rate:R.seo});}
L.push({item:"テスト・公開",h:ceil(3+p),rate:R.test});
if(O("server"))L.push({item:"サーバー設定",h:R.server_h,rate:R.dir});
L.forEach(l=>l.amt=l.h*l.rate);if(wf)L.splice(1,0,wf);
if(O("cms"))L.push({item:"WordPress化",amt:R.wp});if(O("ab"))L.push({item:"ABテスト",amt:R.ab});if(O("photo"))L.push({item:"写真撮影",amt:R.photo});
const hours=L.reduce((a,l)=>a+(l.h||0),0);
if(rush){const b=L.reduce((a,l)=>a+l.amt,0);L.push({item:"特急",amt:Math.round(b*0.2/1000)*1000});}
const sub=L.reduce((a,l)=>a+l.amt,0),total=sub+Math.floor(sub*0.1);let weeks=Math.ceil(2+hours/32);if(rush)weeks=Math.max(2,Math.round(weeks*0.7));
return {sub,total,hours,weeks,L};}
const base={add:{kind:"add",pages:1,dens:"m",grade:"orig",plan:"1",write:"full",speed:"n",opts:["form","seo","jp","anim"]},
lp:{kind:"lp",pages:1,dens:"m",grade:"orig",plan:"1",write:"basic",speed:"n",opts:["form","seo","server"]},
hp:{kind:"hp",pages:6,dens:"m",grade:"orig",plan:"1",write:"client",speed:"n",opts:["form","seo","cms","server"]}};
const MIN=k=>({kind:k,pages:1,dens:"s",grade:"tpl",plan:"1",write:"client",speed:"n",opts:[]});
const MAX=k=>({kind:k,pages:k==="lp"?1:30,dens:"l",grade:"high",plan:"2",write:"full",speed:"n",opts:["form","seo","jp","cms","ab","blog","anim","chat","server","photo"]});
const y=n=>n.toLocaleString("ja-JP");const row=(name,s)=>{const r=calc(s);console.log([name,y(r.sub),y(r.total),y(Math.round(r.total*0.7/1000)*1000),r.hours+"h","約"+r.weeks+"週"].join(" | "));};
console.log("条件 | 税抜 | 税込 | 税込×0.7(千円丸め) | 工数 | 納期");
for(const k of ["add","lp","hp"]){row(k+" 最小",MIN(k));row(k+" 標準構成",base[k]);row(k+" 標準＋特急",{...base[k],speed:"r"});row(k+" 最大",MAX(k));}
// HP ページ数ごと（標準構成）
for(const p of [3,6,10,15,20,30])row("hp 標準 "+p+"P",{...base.hp,pages:p});
for(const p of [2,3,5])row("add 標準 "+p+"P",{...base.add,pages:p});
// 量・品質・原稿の振れ（LP標準）
for(const d of ["s","m","l"])row("lp 情報量"+d,{...base.lp,dens:d});
for(const g of ["tpl","orig","high"])row("lp 品質"+g,{...base.lp,grade:g});
for(const w of ["client","basic","full"])row("lp 原稿"+w,{...base.lp,write:w});
row("lp 2案",{...base.lp,plan:"2"});
console.log("--- 標準構成の内訳");for(const k of ["add","lp","hp"]){console.log(k, calc(base[k]).L.map(l=>l.item+(l.h?`(${l.h}h)`:"")+" "+y(l.amt)).join(" / "));}
