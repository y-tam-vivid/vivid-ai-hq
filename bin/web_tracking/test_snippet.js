// snippet.html のクリックログ部分（最後の <script>）を、最小のスタブ環境で実行して挙動を確かめる。
// 使い方: node test_snippet.js <snippet.html>   ★test_gate.py から呼ばれる。全件合格で exit 0
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync(process.argv[2], 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
const code = scripts[scripts.length - 1];
if (!code || code.indexOf('cta_click') < 0) { console.log('✗ クリックログ部分が取れない'); process.exit(1); }

// store=null → sessionStorage が使えない環境（例外を投げる）を模す
function page(o) {
  const L = {}, dl = [], cl = [];
  const store = o.store;
  const ss = store === null
    ? { getItem() { throw new Error('blocked'); }, setItem() { throw new Error('blocked'); } }
    : { getItem: k => (store.has(k) ? store.get(k) : null), setItem: (k, v) => store.set(k, String(v)) };
  const win = { dataLayer: dl, clarity: function () { cl.push([].slice.call(arguments)); } };
  const doc = { referrer: o.referrer || '', addEventListener: (t, f) => { L[t] = f; } };
  const ctx = vm.createContext({ window: win, document: doc, location: { pathname: o.path || '/', search: o.search || '' },
                                 sessionStorage: ss, URLSearchParams });
  vm.runInContext(code, ctx);
  const el = (attrs) => ({ getAttribute: n => (n in attrs ? attrs[n] : null), hasAttribute: n => n in attrs });
  return {
    dl, cl,
    click(attrs) { const e = el(attrs); L.click({ target: { closest: () => e } }); },
    submit(attrs) { L.submit({ target: el(attrs || {}) }); },
    meta() { return dl.filter(x => x.event === 'page_meta')[0]; },
    clicks() { return dl.filter(x => x.event === 'cta_click'); },
    forms() { return dl.filter(x => x.event === 'form_submit'); },
  };
}

let ng = 0;
function t(name, ok, detail) { if (!ok) ng++; console.log((ok ? '✓' : '✗') + ' JS ' + name + (ok ? '' : ' ／ ' + detail)); }

// 1. utm_source を保持し、2ページ目でも最初の経路を使う
let st = new Map();
let p1 = page({ store: st, search: '?utm_source=ig', path: '/kids/a' });
t('1ページ目 utm_source=ig', p1.meta().lp_source === 'ig', JSON.stringify(p1.meta()));
let p2 = page({ store: st, search: '', path: '/kids/b', referrer: 'https://site.example/kids/a' });
t('2ページ目も ig（referral にならない）', p2.meta().lp_source === 'ig', JSON.stringify(p2.meta()));

// 2. sessionStorage が使えなくても落ちず、従来どおり算出
let p3 = page({ store: null, search: '?utm_source=line' });
t('sessionStorage 不可でも utm を使う', p3.meta().lp_source === 'line', JSON.stringify(p3.meta()));
let p4 = page({ store: null, referrer: 'https://x.example/' });
t('sessionStorage 不可・参照元あり → referral', p4.meta().lp_source === 'referral', JSON.stringify(p4.meta()));

// 3. 最初が direct/referral のとき、後から utm が来たらそれを採る
st = new Map();
page({ store: st, referrer: 'https://google.example/' });
let p5 = page({ store: st, search: '?utm_source=mail', referrer: 'https://site.example/' });
t('referral のあとに utm が来たら utm', p5.meta().lp_source === 'mail', JSON.stringify(p5.meta()));

// 4. tel: / mailto: は中身を送らない
let p6 = page({ store: new Map() });
p6.click({ href: 'tel:0612345678' });
p6.click({ href: 'mailto:someone@example.com?subject=x' });
p6.click({ href: '/kids/a' });
const cs = p6.clicks().map(x => x.cta);
t('tel は "tel"', cs[0] === 'tel', JSON.stringify(cs));
t('mailto は "mailto"', cs[1] === 'mailto', JSON.stringify(cs));
t('通常リンクは href', cs[2] === '/kids/a', JSON.stringify(cs));
t('tel/mailto の中身がどこにも漏れない', JSON.stringify([p6.dl, p6.cl]).indexOf('0612345678') < 0 &&
  JSON.stringify([p6.dl, p6.cl]).indexOf('someone@example.com') < 0, 'leak');

// 5. data-cta つきは今までどおり
let p7 = page({ store: new Map() });
p7.click({ 'data-cta': 'hero', href: 'tel:0612345678' });
t('data-cta があればそれを送る', p7.clicks()[0].cta === 'hero', JSON.stringify(p7.clicks()));

// 6. form 送信（data-cta の有無を問わず）
let p8 = page({ store: new Map(), path: '/contact' });
p8.submit({ action: '/send?token=secret' });
p8.submit({ 'data-cta': 'apply' });
t('data-cta の無い form も form_submit', p8.forms().length === 2, JSON.stringify(p8.forms()));
t('form_submit は案・経路つき', p8.forms()[0].lp_variant === 'contact' && !!p8.forms()[0].lp_source, JSON.stringify(p8.forms()[0]));
t('form の action のクエリは送らない', JSON.stringify(p8.dl).indexOf('secret') < 0, 'leak');
t('form_submit は Clarity へも', p8.cl.some(a => a[0] === 'event' && a[1] === 'form_submit'), JSON.stringify(p8.cl));

console.log(ng ? '\n✗ JS 失敗 ' + ng + ' 件' : '\n✓ JS 全件合格');
process.exit(ng ? 1 : 0);
