(function () {
  "use strict";
  fetch("speculation.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (rules) {
      if (!rules || !rules.prefetch) return;
      var node = document.createElement("script");
      node.type = "speculationrules";
      node.textContent = JSON.stringify(rules);
      document.head.appendChild(node);
    })
    .catch(function () {});
})();
