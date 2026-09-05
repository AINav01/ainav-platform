(function () {
  "use strict";

  function refuse() {
    return {
      kind: "ainav.institute.insights.v1",
      claimed: false,
      connection_claimed: false,
      live: false,
      live_pin_ok: false,
      note: "Application Insights is fail-closed. No connection string. No CDN. connect-src stays 'self'."
    };
  }

  var meta = document.querySelector('meta[name="ainav-appinsights"]');
  var key = meta && meta.getAttribute("content");
  window.AINAV_INSIGHTS = refuse();
  if (key) {
    window.AINAV_INSIGHTS.note =
      "A connection string was present. This tree still refuses to load a telemetry SDK or open connect-src.";
  }
})();
