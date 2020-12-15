// Run it in browser console.
{
	let {AppConstants} = ChromeUtils.import("resource://gre/modules/AppConstants.jsm");
	let res = {};
	let preset = {
		"MOZ_REQUIRE_SIGNING": false,
		"MOZILLA_OFFICIAL": false,
		"MOZ_DEV_EDITION": true,
		"MOZ_TELEMETRY_REPORTING": false,
		"MOZ_CRASHREPORTER": false,
		"MOZ_DATA_REPORTING": false
	};
	for (let [k, v] of Object.entries(preset)) {
		//AppConstants[k] = v;
		res[k] = AppConstants[k];
	}
	console.log(res);
}
