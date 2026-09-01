(function () {
  "use strict";

  function paintTools(data) {
    var root = document.getElementById("kit-tools");
    if (!root || !data || !data.tools) return;
    root.textContent = "";
    data.tools.forEach(function (item) {
      var art = document.createElement("article");
      art.setAttribute("data-tone", item.status === "wired" ? "ready" : "hold");
      var h = document.createElement("h3");
      h.textContent = item.id;
      var p = document.createElement("p");
      p.className = "price";
      p.textContent = item.status || "";
      var n = document.createElement("p");
      n.className = "note";
      n.textContent = "Not a SKU. Not a CMS.";
      art.appendChild(h);
      art.appendChild(p);
      art.appendChild(n);
      root.appendChild(art);
    });
    if (data.thesis) {
      var thesis = document.getElementById("kit-thesis");
      if (thesis) thesis.textContent = data.thesis;
    }
  }

  fetch("kit.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (data && !data.cms) paintTools(data);
    })
    .catch(function () {});
})();
