(function () {
  "use strict";

  document.querySelectorAll("a[href^='#']").forEach(function (link) {
    link.addEventListener("click", function (event) {
      var id = link.getAttribute("href").slice(1);
      var target = document.getElementById(id);
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      if (history.replaceState) history.replaceState(null, "", "#" + id);
    });
  });

  fetch("org.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data || data.live || !data.departments) return;
      var root = document.getElementById("org-cards");
      if (!root) return;
      data.departments.forEach(function (item) {
        var card = root.querySelector("[data-id='" + item.id + "']");
        if (!card) return;
        card.setAttribute("data-status", item.status);
        card.setAttribute("data-wired", item.wired_now ? "true" : "false");
        var price = card.querySelector(".price");
        if (price && item.status) price.textContent = item.status;
      });
    })
    .catch(function () {
      /* org.json is optional when opened as a file */
    });

  fetch("stack.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data || data.live || !data.connections) return;
      var root = document.getElementById("stack-cards");
      if (!root) return;
      data.connections.forEach(function (item) {
        var card = root.querySelector("[data-id='" + item.id + "']");
        if (!card) return;
        card.setAttribute("data-mode", item.mode);
        card.setAttribute("data-live", "false");
      });
    })
    .catch(function () {
      /* stack.json is optional when opened as a file */
    });

  function buyerPayload() {
    var embedded = document.getElementById("buyer-data");
    try {
      return embedded ? JSON.parse(embedded.textContent) : {};
    } catch (err) {
      return {};
    }
  }

  function fillBuyer(data) {
    if (!data) return;
    var write = document.getElementById("buyer-write");
    var incident = document.getElementById("buyer-incident");
    var proof = document.getElementById("buyer-proof");
    var door = document.getElementById("buyer-door");
    if (write && data.write_that_must_not_happen) write.textContent = data.write_that_must_not_happen;
    if (incident && data.incident) incident.textContent = data.incident;
    if (proof && data.proof_day) proof.textContent = data.proof_day;
    if (door && data.door) door.textContent = data.door;
    function replaceList(id, items) {
      var node = document.getElementById(id);
      if (!node || !items || !items.length) return;
      node.innerHTML = "";
      items.forEach(function (item) {
        var li = document.createElement("li");
        li.textContent = item;
        node.appendChild(li);
      });
    }
    replaceList("buyer-seats", data.seats);
    replaceList("buyer-prices", data.prices);
    replaceList("buyer-refuse", data.refuse);
  }

  fetch("buyer.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      fillBuyer(data || buyerPayload());
    })
    .catch(function () {
      fillBuyer(buyerPayload());
    });

  var ask = document.getElementById("ask-proof-day");
  if (ask) {
    ask.addEventListener("click", function () {
      var page = buyerPayload();
      var brief = {
        kind: "ainav.proof_day.brief.v1",
        forwardable: true,
        write_that_must_not_happen: page.write_that_must_not_happen,
        incident: page.incident,
        seats: page.seats,
        prices: page.prices,
        proof_day: page.proof_day,
        refuse: page.refuse,
        ask: "Ask for a ninety-minute proof day on the existing treasury SOD.",
        contact_email: null,
        mailto: null,
        named_customer: null,
        signed_l1: false,
        live: false
      };
      var blob = new Blob([JSON.stringify(brief, null, 2)], { type: "application/json" });
      var link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "ainav-proof-day-brief.json";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      var status = document.getElementById("brief-status");
      if (status) {
        status.hidden = false;
        status.textContent = "Brief downloaded. Forward it. There is no contact inbox on this page.";
      }
    });
  }
})();
