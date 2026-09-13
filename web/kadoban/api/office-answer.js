// 会議室のボタンを「押したら残る」形にする受け口（③・2026-09-13）。
//
// なぜ要るか ── 有璽氏（2026-09-13）
//   「押してなくなっているはずやのに、更新するたびに毎回毎回戻ってんの。
//     ちゃんとこれ反応できてんの？」
//   ★真因：office_template.html の answer() は claude.use("db") があること前提で、
//     Vercel では DB=null。押した結果は `answers = {}` というページ内の変数にしか
//     残らず、再読込みで消える。＝★押しても何も起きていなかった。
//
// 設計は lsu-editor の書き戻し（2026-09-10・実測8項目合格）と同型。
//   画面 → このFunction → Vercel Blob(private) へキュー追記
//        → mini の office_answer_apply.py が拾って ask_hub_queue.json へ適用
//   ★Vercel Function のファイルシステムは読み取り専用なので、ここで台帳は書けない。
//   ★台帳（ask_hub_queue.json）は mini にしか無い（規範どおり）。
//
// 守り
//   ・middleware.js の Basic 認証がこのパスにも掛かる（matcher が /api/ を除外していない
//     ことは data.js 実装時に実測済み）。
//   ・KADOBAN_ANSWER_TOKEN が設定されていれば、それとの一致も要求する（任意・二重の錠）。
//   ・★同じ受付番号へ二度書かない（先に入った answer を上書きしない）。
//
// POST body : { askId, key, label }
// GET       : いま溜まっている回答（画面が再読込み時に「押した跡」を復元するのに使う）

import { put } from '@vercel/blob';

const BLOB_HOST = 'q0z2tsgdx1cbz2qc.private.blob.vercel-storage.com'; // fukuchi-kadoban-data
const PATHNAME = 'kadoban/office-answers.json';

async function readQueue(token) {
  try {
    const r = await fetch(`https://${BLOB_HOST}/${PATHNAME}`, {
      headers: { Authorization: `Bearer ${token}` },
      signal: AbortSignal.timeout(8000),
    });
    if (!r.ok) return { items: {} };           // まだ1件も無い＝これで正常
    const j = JSON.parse(await r.text());
    return j && typeof j === 'object' && j.items ? j : { items: {} };
  } catch (e) {
    return { items: {} };
  }
}

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow, noarchive');

  const blobToken = process.env.BLOB_READ_WRITE_TOKEN;
  if (!blobToken) {
    res.status(200).json({ ok: false, error: 'BLOB_READ_WRITE_TOKEN が未設定' });
    return;
  }
  const gate = process.env.KADOBAN_ANSWER_TOKEN;

  if (req.method === 'GET') {
    const q = await readQueue(blobToken);
    res.status(200).json({ ok: true, items: q.items });
    return;
  }

  if (req.method !== 'POST') {
    res.status(405).json({ ok: false, error: 'POSTかGETだけ' });
    return;
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { body = {}; }
  }
  body = body || {};

  if (gate && body.token !== gate) {
    res.status(403).json({ ok: false, error: 'token mismatch' });
    return;
  }

  const askId = String(body.askId || '').trim();
  const key = String(body.key || '').trim();
  const label = String(body.label || '').trim();
  if (!askId || !key || !label) {
    res.status(200).json({ ok: false, error: 'askId / key / label が要る' });
    return;
  }
  if (!/^[A-Za-z0-9_-]{1,40}$/.test(askId)) {
    res.status(200).json({ ok: false, error: '受付番号の形が違う' });
    return;
  }

  const q = await readQueue(blobToken);

  // ★先に入った回答を上書きしない（連打・二重送信で答えが変わらないように）
  if (q.items[askId]) {
    res.status(200).json({ ok: true, already: true, item: q.items[askId] });
    return;
  }

  q.items[askId] = {
    askId, key, label,
    at: new Date().toISOString(),
    by: '会議室（画面のボタン）',   // ★誰が押したかを偽らない
    applied: false,                 // mini が台帳へ入れたら true にする
  };
  q.updated_at = new Date().toISOString();

  try {
    await put(PATHNAME, JSON.stringify(q), {
      access: 'private',
      token: blobToken,
      contentType: 'application/json',
      addRandomSuffix: false,
      allowOverwrite: true,
      cacheControlMaxAge: 0,
    });
  } catch (e) {
    res.status(200).json({ ok: false, error: `Blobへ書けなかった: ${e && e.message ? e.message : String(e)}` });
    return;
  }

  res.status(200).json({ ok: true, queued: askId, total: Object.keys(q.items).length });
}
