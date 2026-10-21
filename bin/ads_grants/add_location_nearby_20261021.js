/**
 * こどもステーション Ad Grants ─ 2026-10-21 配信地域に近隣5市町を足す（一回きり）
 * 理由   10/15 開始から表示0。6市だけでは検索が少ない。規約は「サービスが役立つ地域」→ 通える近隣だけ（#0bed94）
 * 実行   「AdGrants 書き出し」の中身を一時的にこれへ替えて DRY→プレビュー→実行 → export_script.js へ戻す
 * 戻し方 各キャンペーンの地域から下の5つを外す（元の6市は触っていない）
 */
var DRY = true;
var NAMES = ['Sakai', 'Osakasayama', 'Kawachinagano', 'Yao', 'Kanan'];

function main() {
  var ids = [];
  for (var i = 0; i < NAMES.length; i++) {
    var it = AdsApp.search("SELECT geo_target_constant.id, geo_target_constant.canonical_name, geo_target_constant.target_type, " +
      "geo_target_constant.status FROM geo_target_constant WHERE geo_target_constant.country_code = 'JP' " +
      "AND geo_target_constant.name = '" + NAMES[i] + "' AND geo_target_constant.canonical_name LIKE '%Osaka%'");
    var hit = [];
    while (it.hasNext()) { var g = it.next().geoTargetConstant; hit.push(g); }
    hit.forEach(function (g) { Logger.log('候補 ' + NAMES[i] + ' → ' + g.id + ' ' + g.canonicalName + ' ' + g.targetType + ' ' + g.status); });
    if (hit.length !== 1) { Logger.log('★' + NAMES[i] + ' が1件に絞れない（' + hit.length + '件）。止める'); return; }
    ids.push(Number(hit[0].id));
  }
  var cit = AdsApp.campaigns().withCondition("campaign.status = 'ENABLED'").get();
  var n = 0;
  while (cit.hasNext()) {
    var c = cit.next();
    var have = [];
    var lit = c.targeting().targetedLocations().get();
    while (lit.hasNext()) have.push(lit.next().getId());
    ids.forEach(function (id) {
      if (have.indexOf(id) >= 0) { Logger.log('済 ' + c.getName() + ' ' + id); return; }
      Logger.log((DRY ? '予定 ' : '追加 ') + c.getName() + ' ← ' + id);
      if (!DRY) { c.addLocation(id); n++; }
    });
  }
  Logger.log('完了 追加' + n + (DRY ? '（DRY）' : ''));
}
