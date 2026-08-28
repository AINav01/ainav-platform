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

  fetch("status.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data || data.live || data.live_pin_ok) return;
      var bc = document.getElementById("status-bc");
      var note = document.getElementById("status-bc-note");
      if (bc && data.bc) {
        bc.textContent = data.bc.environment + " · " + data.bc.operating_company;
      }
      if (note && data.bc) {
        note.textContent =
          "Document " +
          data.bc.sandbox_document +
          ". Wedge " +
          data.bc.wedge +
          ". Production blocked. Not LIVE_PIN_OK.";
      }
      var sales = document.getElementById("status-sales");
      if (sales && data.sales) {
        sales.textContent = data.sales.wired ? "wired · twin" : "licensed · not wired";
      }
    })
    .catch(function () {
      /* status.json is optional when opened as a file */
    });

  var twin = {
    grant: null,
    consumed: false
  };

  function hex(buffer) {
    return Array.from(new Uint8Array(buffer))
      .map(function (b) {
        return b.toString(16).padStart(2, "0");
      })
      .join("");
  }

  function actionHash(action) {
    var encoded = new TextEncoder().encode(JSON.stringify(action));
    if (!window.crypto || !window.crypto.subtle) {
      return Promise.resolve("lab-hash-" + encoded.length);
    }
    return window.crypto.subtle.digest("SHA-256", encoded).then(hex);
  }

  function writeLedger(state, text) {
    var box = document.getElementById("twin-ledger");
    if (!box) return;
    box.dataset.state = state;
    box.textContent = text;
  }

  function setTwinButtons(ready) {
    var journal = document.getElementById("twin-journal");
    var quote = document.getElementById("twin-quote");
    if (journal) journal.disabled = !ready;
    if (quote) quote.disabled = !ready;
  }

  var bind = document.getElementById("twin-bind");
  if (bind) {
    bind.addEventListener("click", function () {
      var a = (document.getElementById("twin-seat-a") || {}).value || "";
      var b = (document.getElementById("twin-seat-b") || {}).value || "";
      var status = document.getElementById("twin-admit-status");
      if (!a.trim() || !b.trim() || a.trim() === b.trim()) {
        twin.grant = null;
        twin.consumed = false;
        setTwinButtons(false);
        if (status) status.textContent = "Fail-closed. Seats must be two distinct principals.";
        writeLedger("denied", "admit_denied · same_or_empty_seat\nlive=false · live_pin_ok=false");
        return;
      }
      var action = {
        action_class: "bc.general_journal.post",
        payload: { account: "11100", balancing_account: "22100", amount: "250.00", company: "AINav" },
        sor_target: "bc.sandbox",
        live: false
      };
      actionHash(action).then(function (hash) {
        twin.grant = { seat_a: a.trim(), seat_b: b.trim(), action_hash: hash, used: false };
        twin.consumed = false;
        setTwinButtons(true);
        if (status) status.textContent = "admit_ok. Grant is single-use.";
        writeLedger(
          "ok",
          "admit_ok\nseat_a=" +
            twin.grant.seat_a +
            "\nseat_b=" +
            twin.grant.seat_b +
            "\naction_hash=" +
            hash +
            "\nlive=false · production=false"
        );
      });
    });
  }

  var same = document.getElementById("twin-same");
  if (same) {
    same.addEventListener("click", function () {
      var field = document.getElementById("twin-seat-b");
      var a = document.getElementById("twin-seat-a");
      if (field && a) field.value = a.value;
      if (bind) bind.click();
    });
  }

  var journal = document.getElementById("twin-journal");
  if (journal) {
    journal.addEventListener("click", function () {
      if (!twin.grant || twin.grant.used) {
        writeLedger("denied", "effect_blocked · grant missing or already consumed\nNo Business Central write left this browser.");
        return;
      }
      twin.grant.used = true;
      twin.consumed = true;
      setTwinButtons(true);
      writeLedger(
        "ok",
        "effect_applied · bc.sandbox\ncompany=AINav · document=AINAV-L1-TWIN · 250.00\n11100 debit / 22100 credit\nMicrosoft Business Central Production was not called.\nlive_pin_ok=false"
      );
    });
  }

  var quote = document.getElementById("twin-quote");
  if (quote) {
    quote.addEventListener("click", function () {
      if (!twin.grant) {
        writeLedger("denied", "effect_blocked · no grant");
        return;
      }
      var paid = document.getElementById("twin-udual");
      if (!paid || !paid.checked) {
        writeLedger(
          "denied",
          "provision_denied · U-DUAL is not free with P-ADM\nDynamics 365 Sales Enterprise stays on the twin until a paid attach.\nNo Dataverse write. live=false"
        );
        return;
      }
      writeLedger(
        "ok",
        "effect_applied · d365.sales.sandbox\nquote.discount_override preview on the Sales twin\nNo live Dataverse instance. G14 remains open."
      );
    });
  }
})();
