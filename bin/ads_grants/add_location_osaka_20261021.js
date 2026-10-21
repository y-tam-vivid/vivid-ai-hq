/**
 * こどもステーション Ad Grants ─ 2026-10-21 配信地域に大阪府を足す（一回きり）
 * 理由   10/15 開始から表示0。6市（羽曳野・松原・富田林・藤井寺・柏原・太子）だけでは検索が少ない。#bf1088 有璽氏「進める」
 * 実行   「AdGrants 書き出し」の中身を一時的にこれへ替えて DRY→プレビュー→実行 → export_script.js へ戻す
 * 戻し方 各キャンペーンの地域から「Osaka」を外す（6市は触っていない）
 */
var DRY = true;

function main() {
  var it = AdsApp.search("SELECT geo_target_constant.id, geo_target_constant.name, geo_target_constant.target_type, " +
    "geo_target_constant.canonical_name FROM geo_target_constant WHERE geo_target_constant.country_code = 'JP' " +
    "AND geo_target_constant.target_type = 'Prefecture' AND geo_target_constant.name = 'Osaka'");
  var ids = [];
  while (it.hasNext()) { var g = it.next().geoTargetConstant; ids.push(g.id); Logger.log('候補 ' + g.id + ' ' + g.canonicalName + ' ' + g.targetType); }
  if (ids.length !== 1) { Logger.log('★大阪府が1件に絞れない（' + ids.length + '件）。止める'); return; }
  var id = Number(ids[0]);
  var cit = AdsApp.campaigns().withCondition("campaign.status = 'ENABLED'").get();
  var n = 0;
  while (cit.hasNext()) {
    var c = cit.next();
    var have = [];
    var lit = c.targeting().targetedLocations().get();
    while (lit.hasNext()) { var l = lit.next(); have.push(l.getId()); }
    if (have.indexOf(id) >= 0) { Logger.log('済 ' + c.getName()); continue; }
    Logger.log((DRY ? '予定 ' : '追加 ') + c.getName() + ' ← 大阪府(' + id + ')（いまの地域 ' + have.length + '件）');
    if (!DRY) { c.addLocation(id); n++; }
  }
  Logger.log('完了 追加' + n + (DRY ? '（DRY）' : ''));
}
