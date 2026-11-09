/** こどもステーション Ad Grants ─ 2026-11-09 表示0の再診断（読むだけ・何も変えない・プレビューのみ）
 * ①地域追加（10/27）後のオークションの負け方 ②成果（コンバージョン）の計測の状態 ③入札の設定 */
function main() {
  Logger.log('■①キャンペーン（10/28〜昨日）');
  var it = AdsApp.search("SELECT campaign.name, campaign.primary_status, campaign.primary_status_reasons, campaign.bidding_strategy_type, " +
    "campaign.target_spend.cpc_bid_ceiling_micros, metrics.impressions, metrics.search_impression_share, " +
    "metrics.search_rank_lost_impression_share, metrics.search_budget_lost_impression_share " +
    "FROM campaign WHERE campaign.status = 'ENABLED' AND segments.date BETWEEN '2026-10-28' AND '2026-11-08'");
  while (it.hasNext()) { var r = it.next(), m = r.metrics, c = r.campaign;
    Logger.log(c.name + ' | ' + c.primaryStatus + ' ' + JSON.stringify(c.primaryStatusReasons || []) + ' | 入札 ' + c.biddingStrategyType +
      ' 上限 ' + (c.targetSpend && c.targetSpend.cpcBidCeilingMicros ? c.targetSpend.cpcBidCeilingMicros / 1e6 : 'なし') +
      ' | 表示 ' + m.impressions + ' | シェア ' + m.searchImpressionShare + ' | ランク損失 ' + m.searchRankLostImpressionShare); }

  Logger.log('■②成果の計測（コンバージョン アクション）');
  var ca = AdsApp.search("SELECT conversion_action.name, conversion_action.status, conversion_action.type, conversion_action.category, " +
    "conversion_action.primary_for_goal, conversion_action.include_in_conversions_metric, conversion_action.origin " +
    "FROM conversion_action WHERE conversion_action.status != 'REMOVED'");
  while (ca.hasNext()) { var a = ca.next().conversionAction;
    Logger.log(a.name + ' | ' + a.status + ' | ' + a.type + ' | ' + a.category + ' | メイン ' + a.primaryForGoal + ' | 集計に入れる ' + a.includeInConversionsMetric); }

  Logger.log('■②の2 成果の記録（10/7〜昨日・すべての成果）');
  var cv = AdsApp.search("SELECT segments.conversion_action_name, metrics.all_conversions FROM customer " +
    "WHERE segments.date BETWEEN '2026-10-07' AND '2026-11-08'");
  var any = 0; while (cv.hasNext()) { var r = cv.next(); any++; Logger.log(r.segments.conversionActionName + ' ' + r.metrics.allConversions); }
  Logger.log('成果の行数 ' + any);

  Logger.log('■③キーワード（理由ごとの語数）');
  var k = AdsApp.search("SELECT ad_group_criterion.keyword.text, ad_group_criterion.primary_status, ad_group_criterion.primary_status_reasons " +
    "FROM keyword_view WHERE campaign.status = 'ENABLED' AND ad_group_criterion.status != 'REMOVED'");
  var by = {}; while (k.hasNext()) { var c = k.next().adGroupCriterion; var key = c.primaryStatus + ' ' + JSON.stringify(c.primaryStatusReasons || []);
    (by[key] = by[key] || []).push(c.keyword.text); }
  for (var key in by) Logger.log(by[key].length + '語 ' + key + ' 例: ' + by[key].slice(0, 3).join(' / '));
  Logger.log('完了（読むだけ）');
}
