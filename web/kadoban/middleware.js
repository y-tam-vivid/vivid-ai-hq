// 稼働盤に Basic 認証をかける（Vercel Edge Middleware・無料プランで動く）
//
// なぜ要るか（2026-08-25）
//   Vercel の Deployment Protection は「本番の固定URLまで守る」部分が有料プラン。
//   無料プランでは <project>.vercel.app が素の GET で 200 を返す＝誰でも読める。
//   ★稼働盤の中身は社内の運用実態（人名・Slackチャンネル・会社数・仕組みの穴・DBのID）。
//   → 設定で塞げないなら、入口で止める。
//
// 合言葉の置き場
//   Vercel の環境変数 KADOBAN_USER / KADOBAN_PASS（暗号化保存）。
//   ★ソースにも memory にも書かない → memory/reference_plaintext_credentials_handling.md
//   環境変数が無いときは「開けない」に倒す（開いてしまうより、開かない方が安全）。

export const config = { matcher: '/((?!_vercel|favicon.ico).*)' };

export default function middleware(request) {
  const user = process.env.KADOBAN_USER;
  const pass = process.env.KADOBAN_PASS;

  // ★鍵が無ければ通さない。設定漏れで全公開になるのを防ぐ
  if (!user || !pass) {
    return new Response('設定が終わっていません。', {
      status: 503,
      headers: { 'content-type': 'text/plain; charset=utf-8' },
    });
  }

  const header = request.headers.get('authorization') || '';
  if (header.startsWith('Basic ')) {
    let decoded = '';
    try {
      decoded = atob(header.slice(6));
    } catch (e) {
      decoded = '';
    }
    const i = decoded.indexOf(':');
    if (i > 0 && decoded.slice(0, i) === user && decoded.slice(i + 1) === pass) {
      return; // 通す
    }
  }

  return new Response('認証が必要です。', {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="fukuchi-kadoban", charset="UTF-8"',
      'content-type': 'text/plain; charset=utf-8',
      'x-robots-tag': 'noindex, nofollow, noarchive',
    },
  });
}
