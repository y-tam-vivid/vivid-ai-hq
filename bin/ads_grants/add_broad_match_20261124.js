/**
 * こどもステーション Ad Grants ─ 2026-11-24 部分一致の語を足す（一回きり）
 * 理由   入札を替えて1週も表示0（11/17 診断：冬・くらぶはオークションに入れていない／62語中26語が RARELY_SERVED）。
 *        #e0af3b 有璽氏「一致の範囲を広げる（推奨）」＝今のフレーズ一致の語に、同じ語の部分一致を足す。
 * やること  有効なキャンペーンの有効な広告グループで、フレーズ一致（"…"）の語ごとに部分一致（引用符なし）を1つ足す。
 *           既にある語は足さない／1語だけの語は足さない（Ad Grants の決まり）／既存の語は変えない・消さない
 * 実行   「AdGrants 書き出し」の中身を一時的にこれへ替えて プレビュー → 有璽氏が「実行」 → export_script.js（4,538字）へ戻す
 * 戻し方 キーワード一覧で「一致タイプ＝部分一致」に絞り、足した語を一時停止または削除
 */
function main() {
  var added = 0, have = 0, skipped1 = 0, groups = 0, nk = 0;
  var cit = AdsApp.campaigns().withCondition("campaign.status = 'ENABLED'").get();
  while (cit.hasNext()) {
    var camp = cit.next();
    var git = camp.adGroups().withCondition("ad_group.status = 'ENABLED'").get();
    while (git.hasNext()) {
      var g = git.next(); groups++;
      var texts = {}, phrases = [];
      var kit = g.keywords().withCondition("ad_group_criterion.status != 'REMOVED'").get();
      while (kit.hasNext()) {
        // ★getText() の引用符で一致タイプを見分けると0件になった（11/24 プレビュー）→ getMatchType() で見る
        var k = kit.next(), t = k.getText(), mt = k.getMatchType(); nk++;
        if (nk <= 3) Logger.log('  見本 ' + JSON.stringify(t) + ' ' + mt);
        texts[mt + ':' + t.replace(/["\[\]+]/g, '')] = 1;
        if (mt === 'PHRASE') phrases.push(t.replace(/["\[\]+]/g, ''));
      }
      phrases.forEach(function (p) {
        if (p.split(/\s+/).length < 2) { skipped1++; Logger.log('  1語のため足さない ' + p); return; }
        if (texts['BROAD:' + p]) { have++; return; }
        var op = g.newKeywordBuilder().withText(p).build();
        if (op.isSuccessful()) { added++; Logger.log('  追加 ' + camp.getName() + ' / ' + g.getName() + ' ' + p); }
        else Logger.log('  ★失敗 ' + p + ' ' + op.getErrors().join(' / '));
      });
    }
  }
  Logger.log('完了 広告グループ' + groups + ' 追加' + added + ' 既にあり' + have + ' 1語で見送り' + skipped1 + ' 語の総数' + nk);
}
