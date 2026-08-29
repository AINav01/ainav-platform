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

  fetch("packs.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data || data.live || data.live_pin_ok || data.sku) return;
      function fill(id, items, line) {
        var root = document.getElementById(id);
        if (!root || !items || !items.length) return;
        root.textContent = "";
        items.forEach(function (item) {
          var li = document.createElement("li");
          li.setAttribute("data-id", item.id);
          li.innerHTML = line(item);
          root.appendChild(li);
        });
      }
      fill("pack-industry", data.industry, function (item) {
        var price = item.included
          ? "included with " + item.requires_sku
          : "$" + item.min.toLocaleString() + "–$" + item.max.toLocaleString() + " after " + item.requires_sku;
        return "<strong>" + item.id + "</strong> — " + price + ". Not a SKU.";
      });
      fill("pack-libraries", (data.libraries || []).concat(data.fee_for_service || []), function (item) {
        var extra = item.rate_usd_per_day ? " $" + item.rate_usd_per_day.toLocaleString() + "/day." : "";
        return "<strong>" + item.id + "</strong> — " + (item.note || item.requires_sku || "") + extra;
      });
    })
    .catch(function () {
      /* packs.json is optional when opened as a file */
    });

  fetch("review.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data || data.live || data.live_pin_ok || data.launch_ready) return;
      var equation = document.getElementById("review-equation");
      if (equation && data.success_equation) equation.textContent = "Success = " + data.success_equation;
      var score = document.getElementById("review-score");
      if (score && data.equation) {
        var pin = score.querySelector("[data-id='live_pin_ok'] .price");
        if (pin) pin.textContent = data.equation.live_pin_ok ? "claimed" : "open";
        var proof = score.querySelector("[data-id='proof_day'] .price");
        if (proof) {
          proof.textContent = data.equation.proof_day_sold ? "sold" : "executable · unsold";
        }
        var signed = score.querySelector("[data-id='signed_l1'] .price");
        if (signed) signed.textContent = data.equation.signed_l1 ? "signed" : "open";
        var padm = score.querySelector("[data-id='p_adm'] .price");
        if (padm) padm.textContent = String(data.equation.p_adm_attached);
      }
      var fitRoot = document.getElementById("review-fit");
      if (fitRoot && data.fit) {
        data.fit.forEach(function (item) {
          var card = fitRoot.querySelector("[data-id='" + item.id + "']");
          if (!card) return;
          card.setAttribute("data-status", item.status);
          card.setAttribute("data-live", "false");
          var price = card.querySelector(".price");
          if (price && item.status) price.textContent = item.status;
          var note = card.querySelector("p:not(.price)");
          if (note && item.note) note.textContent = item.note;
        });
      }
    })
    .catch(function () {
      /* review.json is optional when opened as a file */
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

  function paintCards(rootId, items) {
    var root = document.getElementById(rootId);
    if (!root || !items) return;
    items.forEach(function (item) {
      var card = root.querySelector("[data-id='" + item.id + "']");
      if (!card) return;
      card.setAttribute("data-mode", item.mode || "sandbox");
      card.setAttribute("data-live", "false");
      card.setAttribute("data-wired", item.wired ? "true" : "false");
      if (item.role) card.setAttribute("data-role", item.role);
      var price = card.querySelector(".price");
      if (price && item.role) {
        price.textContent = item.role + " · " + (item.mode || "sandbox");
      }
      var note = card.querySelector("p:not(.price)");
      if (note && item.note) note.textContent = item.note;
    });
  }

  fetch("stack.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data || data.live) return;
      paintCards("stack-cards", data.connections);
      paintCards("complement-cards", data.complements);
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
      var notify = document.getElementById("status-notify");
      if (notify && data.notify) {
        notify.textContent = data.notify.wired ? "wired · notify" : "licensed · not wired";
      }
      var gaps = document.getElementById("status-gaps");
      if (gaps && data.open_gaps && data.open_gaps.length) {
        gaps.textContent = data.open_gaps.join(" · ");
      }
      var equation = document.getElementById("status-equation");
      if (equation && data.success_equation) equation.textContent = data.success_equation;
      var revenue = document.getElementById("opp-revenue");
      if (revenue && data.opportunity) {
        revenue.textContent =
          "Recognized revenue: none. Named customers: none. Prove " +
          data.opportunity.prove +
          ". Keep " +
          data.opportunity.keep +
          ". Deepen " +
          data.opportunity.deepen +
          ".";
      }
      var pipeline = document.getElementById("opp-pipeline");
      if (pipeline && data.opportunity && data.opportunity.attached) {
        pipeline.textContent =
          "Signed L1: " +
          (data.opportunity.signed_l1 || 0) +
          ". P-ADM attached: " +
          data.opportunity.attached["P-ADM"] +
          ". U-DUAL attached: " +
          data.opportunity.attached["U-DUAL"] +
          ". Named customers: " +
          (data.opportunity.named_customers || []).length +
          ".";
      }
      function money(n) {
        return "$" + Math.round(n / 1000) + "k";
      }
      function paintSku(id, nodeId) {
        var node = document.getElementById(nodeId);
        var band = data.opportunity && data.opportunity.list && data.opportunity.list[id];
        if (!node || !band) return;
        var term = band.term === "annual" ? "/ year" : "· " + band.term;
        node.textContent = band.id + " · " + money(band.min) + "–" + money(band.max) + " " + term;
      }
      paintSku("L1", "opp-l1");
      paintSku("P-ADM", "opp-padm");
      paintSku("U-DUAL", "opp-udual");
      var year = document.getElementById("opp-year-one");
      if (year && data.opportunity && data.opportunity.year_one_list_if_all_three) {
        var band = data.opportunity.year_one_list_if_all_three;
        year.textContent =
          "Year-one catalog list if one controller buys all three: " +
          money(band.min) +
          "–" +
          money(band.max) +
          ". Not recognized revenue.";
      }
      if (data.fabric && data.fabric.path) {
        var fabric = document.getElementById("fabric-path");
        data.fabric.path.forEach(function (item) {
          var node = fabric ? fabric.querySelector("[data-id='" + item.id + "']") : null;
          if (!node) return;
          node.setAttribute("data-status", item.status);
          node.setAttribute("data-live", "false");
          var price = node.querySelector(".price");
          if (price && item.status && item.id !== "bc.premium" && item.id !== "sales.enterprise") {
            price.textContent = item.status;
          }
        });
      }
      if (data.complements) {
        paintCards("complement-cards", data.complements);
      }
      var toolsStatus = document.getElementById("agent-tools-status");
      if (toolsStatus && data.agent_tools) {
        toolsStatus.textContent =
          "wired=" +
          data.agent_tools.wired +
          " · cloud_agent_can_approve=" +
          data.agent_tools.cloud_agent_can_approve +
          " · is_admit_plane=" +
          data.agent_tools.is_admit_plane +
          " · live=false";
      }
    })
    .catch(function () {
      /* status.json is optional when opened as a file */
    });

  fetch("agent-tools.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data || data.live || data.is_admit_plane) return;
      function replaceList(id, items, textFn) {
        var node = document.getElementById(id);
        if (!node || !items || !items.length) return;
        node.innerHTML = "";
        items.forEach(function (item) {
          var li = document.createElement("li");
          li.textContent = textFn(item);
          node.appendChild(li);
        });
      }
      replaceList("agent-tools-allow", data.leave_available, function (item) {
        return item.name + " — " + item.note;
      });
      replaceList("agent-tools-block", data.block_until_dual, function (item) {
        return item.name + " — " + item.note;
      });
      replaceList("agent-tools-never", data.never_as_admit, function (item) {
        return item;
      });
      var steps = document.getElementById("agent-tools-steps");
      var playbook = data.owner_playbook && data.owner_playbook.steps;
      if (steps && playbook && playbook.length) {
        steps.innerHTML = "";
        playbook.forEach(function (step) {
          var li = document.createElement("li");
          li.appendChild(document.createTextNode(step.do + (step.url ? " " : "")));
          if (step.url) {
            var link = document.createElement("a");
            link.href = step.url;
            link.textContent = step.url_label || step.url;
            link.rel = "noopener";
            li.appendChild(link);
          }
          steps.appendChild(li);
        });
      }
    })
    .catch(function () {
      /* agent-tools.json is optional when opened as a file */
    });

  fetch("business.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data || data.live) return;
      var week = document.getElementById("week-path");
      if (week && data.delivery && data.delivery.week_one) {
        week.textContent = "This week: " + data.delivery.week_one.join(" → ") + ".";
      }
    })
    .catch(function () {
      /* business.json is optional when opened as a file */
    });

  var twin = {
    seats: null,
    consumed: {},
    lastEffect: null
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
    ["twin-journal", "twin-quote", "twin-notify", "twin-kit"].forEach(function (id) {
      var node = document.getElementById(id);
      if (node) node.disabled = !ready;
    });
  }

  function consumeAction(action, onOk) {
    if (!twin.seats) {
      writeLedger("denied", "effect_blocked · seats not bound\nNo Microsoft write left this browser.");
      return;
    }
    if (twin.consumed[action.action_class]) {
      writeLedger(
        "denied",
        "effect_blocked · grant already consumed for " +
          action.action_class +
          "\nSingle-use consume. No second write. live=false"
      );
      return;
    }
    actionHash(action).then(function (hash) {
      twin.consumed[action.action_class] = hash;
      twin.lastEffect = { action_class: action.action_class, action_hash: hash };
      onOk(hash);
    });
  }

  var bind = document.getElementById("twin-bind");
  if (bind) {
    bind.addEventListener("click", function () {
      var a = (document.getElementById("twin-seat-a") || {}).value || "";
      var b = (document.getElementById("twin-seat-b") || {}).value || "";
      var status = document.getElementById("twin-admit-status");
      if (!a.trim() || !b.trim() || a.trim() === b.trim()) {
        twin.seats = null;
        twin.consumed = {};
        twin.lastEffect = null;
        setTwinButtons(false);
        if (status) status.textContent = "Fail-closed. Seats must be two distinct principals.";
        writeLedger("denied", "admit_denied · same_or_empty_seat\nlive=false · live_pin_ok=false");
        return;
      }
      twin.seats = { seat_a: a.trim(), seat_b: b.trim() };
      twin.consumed = {};
      twin.lastEffect = null;
      setTwinButtons(true);
      if (status) status.textContent = "admit_ok. Each action_hash is single-use.";
      writeLedger(
        "ok",
        "admit_ok\nseat_a=" +
          twin.seats.seat_a +
          "\nseat_b=" +
          twin.seats.seat_b +
          "\nNo grant until an action is bound.\nlive=false · production=false"
      );
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
      consumeAction(
        {
          action_class: "bc.general_journal.post",
          payload: { account: "11100", balancing_account: "22100", amount: "250.00", company: "AINav" },
          sor_target: "bc.sandbox",
          live: false
        },
        function (hash) {
          writeLedger(
            "ok",
            "effect_applied · bc.sandbox\naction_class=bc.general_journal.post\naction_hash=" +
              hash +
              "\ncompany=AINav · document=AINAV-L1-TWIN · 250.00\n11100 debit / 22100 credit\nMicrosoft Business Central Production was not called.\nlive_pin_ok=false"
          );
        }
      );
    });
  }

  var quote = document.getElementById("twin-quote");
  if (quote) {
    quote.addEventListener("click", function () {
      if (!twin.seats) {
        writeLedger("denied", "effect_blocked · seats not bound");
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
      consumeAction(
        {
          action_class: "d365.quote.discount_override",
          payload: { discount: "12", company: "AINav" },
          sor_target: "d365.sales.sandbox",
          live: false
        },
        function (hash) {
          writeLedger(
            "ok",
            "effect_applied · d365.sales.sandbox\naction_class=d365.quote.discount_override\naction_hash=" +
              hash +
              "\nquote.discount_override preview on the Sales twin\nNo Dataverse write. No live Dataverse instance. G14 remains open."
          );
        }
      );
    });
  }

  var notifyBtn = document.getElementById("twin-notify");
  if (notifyBtn) {
    notifyBtn.addEventListener("click", function () {
      if (!twin.seats) {
        writeLedger("denied", "notify_held · seats not bound\nA chat is not a seat.");
        return;
      }
      if (!twin.lastEffect) {
        writeLedger(
          "denied",
          "notify_held · no effect to notify\nTeams Enterprise stays licensed_not_wired.\nA chat is not a seat. Graph is not called."
        );
        return;
      }
      writeLedger(
        "ok",
        "notify_preview · teams.enterprise + teams.premium\neffect=" +
          twin.lastEffect.action_class +
          "\nA chat is not a seat. Graph is not called.\nlicensed_not_wired · live=false"
      );
    });
  }

  var pim = document.getElementById("twin-pim");
  if (pim) {
    pim.addEventListener("click", function () {
      writeLedger(
        "denied",
        "admit_denied · entra.pim\nA PIM activation is not dual admit.\nEligible seats stay eligible. Graph is not called.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var copilot = document.getElementById("twin-copilot");
  if (copilot) {
    copilot.addEventListener("click", function () {
      writeLedger(
        "denied",
        "admit_denied · microsoft.copilot\nCopilot is not the admit plane.\nAgent 365 is not a SKU. Microsoft is not the product.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var agentTools = document.getElementById("twin-agent-tools");
  if (agentTools) {
    agentTools.addEventListener("click", function () {
      writeLedger(
        "denied",
        "admit_denied · m365.agent_tools\nA tool invocation is not dual admit.\nWork IQ / MCP stay complements. Dataverse MCP stays blocked until paid U-DUAL.\nThis Cloud Agent cannot approve tools.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var kit = document.getElementById("twin-kit");
  if (kit) {
    kit.addEventListener("click", function () {
      if (!twin.seats) {
        writeLedger("denied", "evidence_held · seats not bound");
        return;
      }
      if (!twin.lastEffect) {
        writeLedger(
          "denied",
          "evidence_held · no kit effect\nSharePoint sandbox stays empty until an admitted write."
        );
        return;
      }
      writeLedger(
        "ok",
        "evidence_preview · sharepoint.kit\neffect=" +
          twin.lastEffect.action_class +
          "\nNo Sites.Read.All. No SharePoint write.\nAcceptance Kit evidence stays on the twin. live=false"
      );
    });
  }
})();
