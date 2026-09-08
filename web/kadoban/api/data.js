// 稼働盤 案B（2026-09-08）── 軽量な最新値を Vercel Blob（private）から読んで返す。
//
// ★このFunctionへのアクセスにも middleware.js の Basic 認証が掛かる
//   （matcher が /api/ を除外していないことを実装前に確認済み）。
//   ＝ブラウザ側は稼働盤本体を開いたときの認証情報をそのまま使ってこの endpoint を叩ける。
//
// ★Blob store（fukuchi-kadoban-data・private）の読み取りは、公開URLへ
//   Authorization: Bearer <BLOB_READ_WRITE_TOKEN> を付けるだけで通ることを実測済み
//   （2026-09-08）。@vercel/blob SDK は使わない（package.json への依存追加が不要になる）。
//
// ★中身が空・Blobが落ちている・トークンが無い等、どんな失敗でも
//   画面側（dashboard_build.py が出すJS）を壊さない形（stale:true 付きで返す）にする。
//   ここを黙って200で空を返すと「古い値を最新と誤読する」事故になるため、
//   失敗時は必ず ok:false を明記する。

const BLOB_HOST = 'q0z2tsgdx1cbz2qc.private.blob.vercel-storage.com';
const PATHNAME = 'kadoban/realtime.json';

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow, noarchive');

  const token = process.env.BLOB_READ_WRITE_TOKEN;
  if (!token) {
    res.status(200).json({ ok: false, stale: true, reason: 'BLOB_READ_WRITE_TOKEN が未設定' });
    return;
  }

  try {
    const upstream = await fetch(`https://${BLOB_HOST}/${PATHNAME}`, {
      headers: { Authorization: `Bearer ${token}` },
      // ★Vercel Functionからの外部fetchが詰まって画面全体を巻き込まないよう、
      //   タイムアウトを明示（AbortSignal.timeout はNode.js 18+相当のVercel Functionsで動く）
      signal: AbortSignal.timeout(8000),
    });

    if (!upstream.ok) {
      res.status(200).json({
        ok: false,
        stale: true,
        reason: `Blobから読めなかった（HTTP ${upstream.status}）`,
      });
      return;
    }

    const body = await upstream.text();
    let parsed;
    try {
      parsed = JSON.parse(body);
    } catch (e) {
      res.status(200).json({ ok: false, stale: true, reason: 'Blobの中身がJSONとして壊れている' });
      return;
    }

    res.status(200).json({ ok: true, stale: false, data: parsed });
  } catch (e) {
    res.status(200).json({
      ok: false,
      stale: true,
      reason: `取得中にエラー: ${e && e.message ? e.message : String(e)}`,
    });
  }
}
