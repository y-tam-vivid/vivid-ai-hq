// 会議室（Vercel版）── 軽量な最新値を Vercel Blob（private）から読んで返す。
// api/data.js（案B・2026-09-08）と全く同じパターン。pathname だけ office 用に分けている。
//
// ★このFunctionへのアクセスにも middleware.js の Basic 認証が掛かる
//   （matcher が /api/ を除外していないことを data.js 実装時に確認済み・流用）。
//
// ★中身が空・Blobが落ちている・トークンが無い等、どんな失敗でも
//   画面側（office_build.py が出すJS）を壊さない形（stale:true 付きで返す）にする。

const BLOB_HOST = 'q0z2tsgdx1cbz2qc.private.blob.vercel-storage.com';
const PATHNAME = 'kadoban/office-realtime.json';

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
