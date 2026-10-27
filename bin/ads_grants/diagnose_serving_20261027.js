/**
 * こどもステーション Ad Grants ─ 2026-10-27 表示0の理由を読む（読むだけ・何も変えない）
 * 理由   10/15 開始から表示0。キーワード・入札・地域を直しても0のまま（有璽氏「なんでゼロのままなんやろな」）
 * 実行   「AdGrants 書き出し」の中身を一時的にこれへ替えて★プレビューだけ → export_script.js へ戻す
 * 読むもの Google広告が付けている「主なステータス」とその理由（キャンペーン・広告・キーワード）
 */
function main() {
  log_('■キャンペーン', "SELECT campaign.name, campaign.status, campaign.serving_status, campaign.primary_status, " +
    "campaign.primary_status_reasons, campaign.bidding_strategy_type FROM campaign WHERE campaign.status = 'ENABLED'",
    function (r) { return [r.campaign.name, r.campaign.servingStatus, r.campaign.primaryStatus,
      JSON.stringify(r.campaign.primaryStatusReasons || []), r.campaign.biddingStrategyType]; });
  log_('■広告グループ', "SELECT campaign.name, ad_group.name, ad_group.status, ad_group.primary_status, " +
    "ad_group.primary_status_reasons FROM ad_group WHERE campaign.status = 'ENABLED'",
    function (r) { return [r.campaign.name, r.adGroup.name, r.adGroup.primaryStatus,
      JSON.stringify(r.adGroup.primaryStatusReasons || [])]; });
  log_('■広告', "SELECT ad_group.name, ad_group_ad.ad.id, ad_group_ad.status, ad_group_ad.primary_status, " +
    "ad_group_ad.primary_status_reasons, ad_group_ad.policy_summary.approval_status, " +
    "ad_group_ad.policy_summary.review_status FROM ad_group_ad WHERE campaign.status = 'ENABLED' AND ad_group_ad.status != 'REMOVED'",
    function (r) { return [r.adGroup.name, r.adGroupAd.primaryStatus, JSON.stringify(r.adGroupAd.primaryStatusReasons || []),
      r.adGroupAd.policySummary ? r.adGroupAd.policySummary.approvalStatus + '/' + r.adGroupAd.policySummary.reviewStatus : '']; });
  // キーワードは理由ごとに数える（62語を全部並べるとログが長いので、理由の組み合わせごとの語数＋例）
  var it = AdsApp.search("SELECT ad_group.name, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type, " +
    "ad_group_criterion.primary_status, ad_group_criterion.primary_status_reasons, " +
    "ad_group_criterion.system_serving_status, ad_group_criterion.approval_status " +
    "FROM keyword_view WHERE campaign.status = 'ENABLED' AND ad_group_criterion.status != 'REMOVED'");
  var by = {};
  while (it.hasNext()) {
    var r = it.next(), c = r.adGroupCriterion;
    var k = c.primaryStatus + ' ' + JSON.stringify(c.primaryStatusReasons || []) + ' serving=' + c.systemServingStatus + ' appr=' + c.approvalStatus;
    (by[k] = by[k] || []).push(c.keyword.text + '(' + c.keyword.matchType + ')');
  }
  Logger.log('■キーワード（理由ごとの語数）');
  for (var k in by) Logger.log(by[k].length + '語  ' + k + '  例: ' + by[k].slice(0, 4).join(' / '));
  Logger.log('完了（読むだけ）');
}

function log_(title, q, row) {
  Logger.log(title);
  var it = AdsApp.search(q);
  while (it.hasNext()) Logger.log('  ' + row(it.next()).join(' | '));
}
