// 参考サイトの式に「割り引く／割り引かない」を付けて、芽育の金額を出す（2026-11-03 有璽氏の方針）
const R={dir:4000,write:3500,design:4500,code:4500,seo:4500,test:4000,photo:60000,wp:40000,ab:80000,lp_basic:15000,lp_full:36000,hp_basic:24000,hp_full:60000,server_h:4};
const DENS={s:.6,m:1,l:1.5},GD={tpl:.6,orig:1,high:1.6},GC={tpl:.8,orig:1,high:1.3};
function lines(s){const {kind,dens,grade:g,plan,write:wr}=s;const p=kind==="lp"?1:s.pages;const O=id=>s.opts.includes(id);
const d=DENS[dens],us=wr!=="client",E=d*(1+0.5*(p-1)),ceil=x=>Math.ceil(x-1e-9);const L=[];let wf=null;
L.push({item:"ディレクション",h:ceil(6+2*E+(kind==="hp"?4:kind==="lp"?2:0)),rate:R.dir,keep:true});
if(us){if(kind==="add")L.push({item:wr==="full"?"原稿作成（ライター）":"原稿整理",h:ceil((wr==="full"?12:6)*E),rate:R.write,keep:wr==="full"});
 else wf={item:wr==="full"?"原稿（ライター取材）":"原稿整理",amt:R[kind+"_"+wr],keep:wr==="full"};}
L.push({item:"デザイン",h:ceil(14*E*GD[g]+(plan==="2"?7*d*GD[g]:0)),rate:R.design});
let ch=14*E*GC[g];if(O("anim"))ch+=kind==="add"?0:2;if(O("form"))ch+=6;if(O("blog"))ch+=12;if(O("chat"))ch+=6;
L.push({item:"コーディング・実装",h:ceil(ch),rate:R.code});
if(O("seo")||O("jp")){let sh=0;if(O("jp"))sh+=2;if(O("seo"))sh+=3+p;L.push({item:"検索対策",h:ceil(sh),rate:R.seo});}
L.push({item:"テスト・公開",h:ceil(3+p),rate:R.test});
if(O("server"))L.push({item:"サーバー・ドメイン設定",h:R.server_h,rate:R.dir,keep:true});
L.forEach(l=>l.amt=l.h*l.rate);if(wf)L.splice(1,0,wf);
if(O("cms"))L.push({item:"WordPress化",amt:R.wp});if(O("ab"))L.push({item:"ABテスト",amt:R.ab});if(O("photo"))L.push({item:"写真撮影（外注）",amt:R.photo,keep:true});
return {L,hours:L.reduce((a,l)=>a+(l.h||0),0),kind};}
function price(s,ratio){const {L,hours,kind}=lines(s);const sum=f=>L.reduce((a,l)=>a+f(l),0);
 const scBase=sum(l=>l.amt), ourBase=sum(l=>l.keep?l.amt:l.amt*ratio);
 const rush=s.speed==="r";const scSub=scBase+(rush?Math.round(scBase*0.2/1000)*1000:0);const ourSub=ourBase+(rush?Math.round(ourBase*0.2/1000)*1000:0);
 const tax=x=>x+Math.floor(x*0.1);let w=Math.ceil(2+hours/32);if(rush)w=Math.max(2,Math.round(w*0.7));
 const add=kind==="hp"?2:1;
 return {sc:tax(scSub),ours:Math.round(tax(ourSub)/1000)*1000,keepAmt:Math.round(tax(sum(l=>l.keep?l.amt:0))),hours,scW:w,ourW:w+add,
   L:L.map(l=>({item:l.item,h:l.h||null,sc:l.amt,ours:Math.round((l.keep?l.amt:l.amt*ratio)),keep:!!l.keep}))};}
const base={add:{kind:"add",pages:1,dens:"m",grade:"orig",plan:"1",write:"full",speed:"n",opts:["form","seo","jp","anim"]},
lp:{kind:"lp",pages:1,dens:"m",grade:"orig",plan:"1",write:"basic",speed:"n",opts:["form","seo","server"]},
hp:{kind:"hp",pages:6,dens:"m",grade:"orig",plan:"1",write:"client",speed:"n",opts:["form","seo","cms","server"]}};
const MIN=k=>({kind:k,pages:1,dens:"s",grade:"tpl",plan:"1",write:"client",speed:"n",opts:[]});
const MAX=k=>({kind:k,pages:1,dens:"l",grade:"high",plan:"2",write:"full",speed:"n",opts:["form","seo","jp","cms","ab","blog","anim","chat","server","photo"]});
const C=[["既存サイトに1ページ追加","最小",MIN("add")],["既存サイトに1ページ追加","標準",base.add],["既存サイトに1ページ追加","標準＋特急",{...base.add,speed:"r"}],
["既存サイトに3ページ追加","標準",{...base.add,pages:3}],
["LP","最小",MIN("lp")],["LP","標準",base.lp],["LP","標準＋特急",{...base.lp,speed:"r"}],["LP","最大",MAX("lp")],
["HP 3ページ","標準",{...base.hp,pages:3}],["HP 6ページ","標準",base.hp],["HP 6ページ","標準＋特急",{...base.hp,speed:"r"}],
["HP 6ページ","標準＋ライター取材＋撮影",{...base.hp,write:"full",opts:[...base.hp.opts,"photo"]}],
["HP 10ページ","標準",{...base.hp,pages:10}],["HP 15ページ","標準",{...base.hp,pages:15}],["HP 20ページ","標準",{...base.hp,pages:20}],["HP 30ページ","標準",{...base.hp,pages:30}]];
const RATIOS=[0.4,0.5,0.6,0.7];
const out={bands:C.map(([a,b,s])=>{const r={name:a,cond:b};RATIOS.forEach(x=>{const p=price(s,x);r.sc=p.sc;r.hours=p.hours;r.scW=p.scW;r.ourW=p.ourW;r.keep=p.keepAmt;r["o"+x*10]=p.ours;});return r;}),
 breakdown:["add","lp","hp"].map(k=>({kind:k,L:price(base[k],1).L}))};
console.log(JSON.stringify(out));
