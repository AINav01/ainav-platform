(function () {
  "use strict";

  function score(record, terms) {
    var hay = ((record.title || "") + " " + (record.text || "")).toLowerCase();
    var hits = 0;
    for (var i = 0; i < terms.length; i += 1) {
      if (hay.indexOf(terms[i]) >= 0) hits += 1;
    }
    return hits === terms.length ? hits : 0;
  }

  function render(root, items) {
    root.textContent = "";
    if (!items.length) {
      var empty = document.createElement("p");
      empty.className = "note";
      empty.textContent = "No catalog match. Search does not invent a page.";
      root.appendChild(empty);
      return;
    }
    items.forEach(function (item) {
      var a = document.createElement("a");
      a.href = item.href;
      a.textContent = item.title;
      var p = document.createElement("p");
      p.className = "note";
      p.textContent = (item.text || "").slice(0, 160);
      var wrap = document.createElement("article");
      wrap.appendChild(a);
      wrap.appendChild(p);
      root.appendChild(wrap);
    });
  }

  function bind(input, out, records) {
    if (!input || !out) return;
    input.addEventListener("input", function () {
      var terms = String(input.value || "")
        .toLowerCase()
        .split(/\s+/)
        .filter(Boolean);
      if (!terms.length) {
        out.textContent = "";
        return;
      }
      render(
        out,
        records.filter(function (item) {
          return score(item, terms) > 0;
        })
      );
    });
  }

  fetch("search.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data || data.cms || !data.records) return;
      bind(document.getElementById("site-search"), document.getElementById("site-search-out"), data.records);
      bind(document.getElementById("app-search"), document.getElementById("app-search-out"), data.records);
      bind(document.getElementById("kit-search"), document.getElementById("kit-search-out"), data.records);
    })
    .catch(function () {});
})();
