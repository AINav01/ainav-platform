(function () {
  "use strict";

  var RESULT_CAP = 8;

  function score(record, terms) {
    var hay = ((record.title || "") + " " + (record.text || "")).toLowerCase();
    var hits = 0;
    for (var i = 0; i < terms.length; i += 1) {
      if (hay.indexOf(terms[i]) >= 0) hits += 1;
    }
    return hits === terms.length ? hits : 0;
  }

  function setExpanded(input, open) {
    if (input) input.setAttribute("aria-expanded", open ? "true" : "false");
  }

  function restoreListbox(root) {
    if (!root) return;
    root.setAttribute("role", "listbox");
    root.setAttribute("aria-label", "Catalog matches");
  }

  function close(input, root) {
    if (root) root.textContent = "";
    restoreListbox(root);
    setExpanded(input, false);
  }

  function dismiss(input, root) {
    if (input) input.value = "";
    close(input, root);
  }

  function render(root, items, input) {
    root.textContent = "";
    setExpanded(input, true);
    if (!items.length) {
      root.setAttribute("role", "status");
      root.removeAttribute("aria-label");
      var empty = document.createElement("p");
      empty.className = "note";
      empty.textContent = "No catalog match. Search does not invent a page.";
      root.appendChild(empty);
      return;
    }
    restoreListbox(root);
    items.slice(0, RESULT_CAP).forEach(function (item, index) {
      var a = document.createElement("a");
      a.href = item.href;
      a.id = (input && input.id ? input.id : "search") + "-opt-" + index;
      a.textContent = item.title;
      a.setAttribute("role", "option");
      a.addEventListener("click", function (event) {
        dismiss(input, root);
        var href = item.href || a.getAttribute("href") || "";
        var hashAt = href.indexOf("#");
        if (hashAt < 0) return;
        var path = href.slice(0, hashAt);
        var hash = href.slice(hashAt);
        if (hash.length < 2) return;
        if (path) {
          var dest = path.split("/").pop() || "";
          var here = location.pathname.split("/").pop() || "index.html";
          if (here === "") here = "index.html";
          if (dest && dest !== here && dest !== ".") return;
        }
        var id;
        try {
          id = decodeURIComponent(hash.slice(1));
        } catch (err) {
          id = hash.slice(1);
        }
        var target = document.getElementById(id);
        if (!target) return;
        event.preventDefault();
        if (history.replaceState) history.replaceState(null, "", hash);
        window.dispatchEvent(new Event("hashchange"));
      });
      var p = document.createElement("p");
      p.className = "note";
      p.textContent = (item.text || "").slice(0, 160);
      var wrap = document.createElement("article");
      wrap.setAttribute("role", "presentation");
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
        close(input, out);
        return;
      }
      render(
        out,
        records.filter(function (item) {
          return score(item, terms) > 0;
        }),
        input
      );
    });
    input.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        event.preventDefault();
        dismiss(input, out);
      }
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
      window.addEventListener("hashchange", function () {
        dismiss(document.getElementById("site-search"), document.getElementById("site-search-out"));
        dismiss(document.getElementById("app-search"), document.getElementById("app-search-out"));
        dismiss(document.getElementById("kit-search"), document.getElementById("kit-search-out"));
      });
    })
    .catch(function () {});
})();
