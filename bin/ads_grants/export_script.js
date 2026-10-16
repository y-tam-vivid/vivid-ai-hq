/**
 * こどもステーション Ad Grants ─ 広告の数字を表へ書き出す（Google広告スクリプト）
 *
 * 置き場   Google広告 905-941-6874（npo.station）→ ツール → 一括操作 → スクリプト「AdGrants 書き出し」
 * 頻度     毎日 1回（朝 4時台）
 * 書く先   npo.station のドライブの表「AdGrants_書き出し」（無ければ作り、y_tam@vivid-global.com へ閲覧共有）
 * 読む側   Mac mini bin/ads_grants_report.py（週次・月次の報告）
 * ★正本はこのファイル。広告画面のスクリプトを直したら、ここも同じに直す。
 *
 * タブ
 *   campaign_daily   日付・キャンペーン・表示・クリック・クリック率・成果・費用（開始日〜昨日を毎回書き直す）
 *   conversions      日付・キャンペーン・成果の種類・成果の数（同上）
 *   search_terms     日付・キャンペーン・検索語・表示・クリック（直近35日を書き直す）
 *   keywords         キャンペーン・広告グループ・キーワード・状態・品質スコア（いまの状態）
 *   meta             最終更新の時刻・行数（読む側が「止まっていないか」を見る）
 */
var SHEET_NAME = 'AdGrants_書き出し';
var SHARE_TO = 'y_tam@vivid-global.com';
var START = '2026-10-07';

function main() {
  var ss = openOrCreate_();
  var tz = AdsApp.currentAccount().getTimeZone();
  var yesterday = Utilities.formatDate(new Date(Date.now() - 86400000), tz, 'yyyy-MM-dd');
  var from35 = Utilities.formatDate(new Date(Date.now() - 35 * 86400000), tz, 'yyyy-MM-dd');
  if (from35 < START) from35 = START;
  var counts = {};

  counts.campaign_daily = write_(ss, 'campaign_daily',
    ['date', 'campaign', 'impressions', 'clicks', 'ctr', 'conversions', 'cost'],
    'SELECT segments.date, campaign.name, metrics.impressions, metrics.clicks, metrics.ctr, ' +
    'metrics.conversions, metrics.cost_micros FROM campaign ' +
    "WHERE segments.date BETWEEN '" + START + "' AND '" + yesterday + "'",
    function (r) {
      return [r.segments.date, r.campaign.name, num_(r.metrics.impressions), num_(r.metrics.clicks),
              num_(r.metrics.ctr), num_(r.metrics.conversions), num_(r.metrics.costMicros) / 1e6];
    });

  counts.conversions = write_(ss, 'conversions',
    ['date', 'campaign', 'action', 'conversions'],
    'SELECT segments.date, campaign.name, segments.conversion_action_name, metrics.all_conversions ' +
    "FROM campaign WHERE segments.date BETWEEN '" + START + "' AND '" + yesterday + "'",
    function (r) {
      return [r.segments.date, r.campaign.name, r.segments.conversionActionName,
              num_(r.metrics.allConversions)];
    });

  counts.search_terms = write_(ss, 'search_terms',
    ['date', 'campaign', 'search_term', 'impressions', 'clicks'],
    'SELECT segments.date, campaign.name, search_term_view.search_term, metrics.impressions, ' +
    "metrics.clicks FROM search_term_view WHERE segments.date BETWEEN '" + from35 + "' AND '" + yesterday + "'",
    function (r) {
      return [r.segments.date, r.campaign.name, r.searchTermView.searchTerm,
              num_(r.metrics.impressions), num_(r.metrics.clicks)];
    });

  counts.keywords = write_(ss, 'keywords',
    ['campaign', 'ad_group', 'keyword', 'status', 'quality_score'],
    'SELECT campaign.name, ad_group.name, ad_group_criterion.keyword.text, ' +
    'ad_group_criterion.status, ad_group_criterion.quality_info.quality_score ' +
    "FROM keyword_view WHERE campaign.status = 'ENABLED' AND ad_group_criterion.status != 'REMOVED'",
    function (r) {
      var q = r.adGroupCriterion.qualityInfo ? r.adGroupCriterion.qualityInfo.qualityScore : '';
      return [r.campaign.name, r.adGroup.name, r.adGroupCriterion.keyword.text,
              r.adGroupCriterion.status, q === undefined ? '' : q];
    });

  var meta = tab_(ss, 'meta');
  meta.clear();
  var now = Utilities.formatDate(new Date(), tz, "yyyy-MM-dd'T'HH:mm:ss");
  var rows = [['key', 'value'], ['updated_at', now], ['through', yesterday]];
  for (var k in counts) rows.push(['rows_' + k, counts[k]]);
  meta.getRange(1, 1, rows.length, 2).setValues(rows);
  Logger.log('書き出し完了 ' + ss.getUrl() + ' ' + JSON.stringify(counts));
}

function openOrCreate_() {
  var it = DriveApp.getFilesByName(SHEET_NAME);
  var ss = it.hasNext() ? SpreadsheetApp.open(it.next()) : SpreadsheetApp.create(SHEET_NAME);
  var file = DriveApp.getFileById(ss.getId());
  var viewers = file.getViewers().map(function (u) { return u.getEmail(); });
  if (viewers.indexOf(SHARE_TO) < 0) file.addViewer(SHARE_TO);
  return ss;
}

function tab_(ss, name) {
  return ss.getSheetByName(name) || ss.insertSheet(name);
}

// ★毎回まるごと書き直す（追記にしない＝同じ日が二重にならない・数字の後からの修正も拾える）
function write_(ss, name, header, query, toRow) {
  var out = [header];
  var it = AdsApp.search(query);
  while (it.hasNext()) out.push(toRow(it.next()));
  var sh = tab_(ss, name);
  sh.clear();
  sh.getRange(1, 1, out.length, header.length).setValues(out);
  return out.length - 1;
}

function num_(v) {
  return v === undefined || v === null || v === '' ? 0 : Number(v);
}
