(function () {
  "use strict";

  var WORKSPACES = ["floor", "capital", "programs"];
  var VIEW_COPY = {
    entire: {
      title: "Entire plane",
      note: "Anyone on the tenant. Can: see the ledger and the freeze state. Cannot: a view is not a seat."
    },
    client: {
      title: "Client executive",
      note: "The client executive dashboard is this plane. Included with L1. Not an upsell."
    },
    owner: {
      title: "Owner / board",
      note: "Oversee and freeze. Cannot: invent oid, seat B click, or LIVE_PIN_OK."
    },
    seats: {
      title: "Seats",
      note: "Seat A and seat B admit. One mailbox recorded. Zero oid. Zero click."
    },
    examiner: {
      title: "Examiner",
      note: "Second record and weekly keep. P-ADM is not attached. Claimed maps stay false."
    }
  };

  function $(id) {
    return document.getElementById(id);
  }

  function setText(id, value) {
    var node = $(id);
    if (node && value != null) node.textContent = value;
  }

  function workspaceFromHash() {
    var raw = (location.hash || "#floor").replace("#", "").toLowerCase();
    return WORKSPACES.indexOf(raw) >= 0 ? raw : "floor";
  }

  function showWorkspace(id) {
    document.body.setAttribute("data-workspace", id);
    WORKSPACES.forEach(function (name) {
      var node = $("workspace-" + name);
      if (!node) return;
      var on = name === id;
      node.hidden = !on;
    });
    Array.prototype.forEach.call(document.querySelectorAll(".app-rail a[data-workspace]"), function (link) {
      if (link.getAttribute("data-workspace") === id) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    });
  }

  function paintRail(root, items) {
    if (!root || !items || !items.length) return;
    root.textContent = "";
    items.forEach(function (item) {
      var li = document.createElement("li");
      if (item.id) li.setAttribute("data-step", item.id);
      var b = document.createElement("b");
      b.textContent = item.name || "";
      var span = document.createElement("span");
      span.textContent = item.note || "";
      li.appendChild(b);
      li.appendChild(span);
      root.appendChild(li);
    });
  }

  function paintTiles(root, items) {
    if (!root || !items || !items.length) return;
    root.textContent = "";
    items.forEach(function (item) {
      var art = document.createElement("article");
      art.setAttribute("data-tone", item.tone || "hold");
      var h = document.createElement("h3");
      h.textContent = item.label || "";
      var p = document.createElement("p");
      p.className = "price";
      p.textContent = item.value || "";
      var n = document.createElement("p");
      n.className = "note";
      n.textContent = item.note || "";
      art.appendChild(h);
      art.appendChild(p);
      art.appendChild(n);
      root.appendChild(art);
    });
  }

  function paintStrip(root, tiles) {
    if (!root || !tiles) return;
    var wanted = {
      plane_state: "Plane",
      pending_admits: "Pending",
      off_switch: "Off switch",
      recognized_revenue: "Revenue",
      signed_l1: "Signed L1",
      seats_recorded: "Seats"
    };
    root.textContent = "";
    tiles.forEach(function (item) {
      if (!wanted[item.id]) return;
      var span = document.createElement("span");
      span.appendChild(document.createTextNode(wanted[item.id] + " "));
      var b = document.createElement("b");
      b.textContent = item.value;
      span.appendChild(b);
      root.appendChild(span);
    });
  }

  function setView(id, views) {
    var copy = VIEW_COPY[id] || VIEW_COPY.entire;
    if (views && views.length) {
      var match = views.filter(function (item) {
        return item.id === id || item.view === id;
      })[0];
      if (match) {
        copy = {
          title: match.name || match.label || copy.title,
          note: match.note || match.can || copy.note
        };
      }
    }
    var card = $("app-view-card");
    if (card) {
      card.innerHTML = "";
      var h = document.createElement("h3");
      h.textContent = copy.title;
      var p = document.createElement("p");
      p.textContent = copy.note;
      card.appendChild(h);
      card.appendChild(p);
    }
    Array.prototype.forEach.call(document.querySelectorAll("#app-view-tabs [data-view]"), function (btn) {
      btn.setAttribute("aria-selected", btn.getAttribute("data-view") === id ? "true" : "false");
    });
  }

  function paintFloor(data) {
    var glance = (data.dashboard && data.dashboard.first_glance) || {};
    if (glance.lede) setText("app-floor-lede", glance.lede);
    paintRail($("app-write-rail"), glance.write_rail);
    paintStrip($("app-floor-strip"), data.tiles);
    paintTiles($("app-floor-tiles"), data.tiles);
    var tabs = $("app-view-tabs");
    if (tabs && !tabs.getAttribute("data-bound")) {
      tabs.setAttribute("data-bound", "true");
      tabs.addEventListener("click", function (event) {
        var btn = event.target.closest("[data-view]");
        if (!btn) return;
        setView(btn.getAttribute("data-view"), data.views);
      });
    }
    setView("entire", data.views);
  }

  function paragraph(text) {
    var p = document.createElement("p");
    p.textContent = text;
    return p;
  }

  function paintCapital(data) {
    if (data.executive_summary && data.executive_summary.lede) {
      setText("app-capital-lede", data.executive_summary.lede);
    } else if (data.one_liner) {
      setText("app-capital-lede", data.one_liner);
    }
    setText("app-capital-open", data.letter_open || "");
    setText("app-capital-close", data.letter_close || data.signoff || "");
    var body = $("app-capital-body");
    if (body) {
      body.textContent = "";
      String(data.letter_body || "")
        .split(/\n\n+/)
        .filter(Boolean)
        .forEach(function (block) {
          body.appendChild(paragraph(block));
        });
    }
    var kpis = $("app-capital-kpis");
    if (kpis && data.kpis) {
      var map = {
        "Recognized revenue": "$" + (data.kpis.recognized_revenue || 0),
        "Named customers": String(data.kpis.named_customers || 0),
        "Signed L1": String(data.kpis.signed_l1 || 0),
        "Priced round": data.priced_round ? "claimed" : "refused"
      };
      Array.prototype.forEach.call(kpis.querySelectorAll("article"), function (art) {
        var label = (art.querySelector("h3") || {}).textContent;
        var price = art.querySelector(".price");
        if (price && map[label]) price.textContent = map[label];
      });
    }
    var exec = document.querySelector("#app-capital-exec tbody");
    if (exec && data.executive_summary && data.executive_summary.items) {
      exec.textContent = "";
      data.executive_summary.items.forEach(function (item) {
        var tr = document.createElement("tr");
        var th = document.createElement("th");
        th.textContent = item.name || "";
        var td = document.createElement("td");
        td.textContent = item.note || "";
        tr.appendChild(th);
        tr.appendChild(td);
        exec.appendChild(tr);
      });
    }
    var refuse = $("app-capital-refuse");
    if (refuse && data.refuse) {
      refuse.textContent = "";
      data.refuse.forEach(function (item) {
        var li = document.createElement("li");
        li.textContent = item;
        refuse.appendChild(li);
      });
    }
  }

  function list(root, items) {
    if (!root) return;
    root.textContent = "";
    (items || []).forEach(function (item) {
      var li = document.createElement("li");
      li.textContent = item;
      root.appendChild(li);
    });
  }

  function paintPrograms(data) {
    if (data.lead_narrative) setText("app-programs-lede", data.lead_narrative);
    var contacts = data.contacts || {};
    var invited = contacts.invited || {};
    var contactRoot = $("app-program-contacts");
    if (contactRoot) {
      var cards = contactRoot.querySelectorAll("article p");
      if (cards[0]) {
        cards[0].textContent =
          (contacts.developer_intended || contacts.owner || "James Hodnett") +
          ". Owner. Top-level developer contact stays " +
          (contacts.developer == null ? "null" : String(contacts.developer)) +
          " until two unique humans exist.";
      }
      if (cards[1]) {
        cards[1].textContent =
          (invited.name || "Cynthia Hodnett") +
          ". Mailbox recorded=" +
          String(!!invited.recorded) +
          ". Inception role intended=" +
          (invited.inception_role || "business_executive") +
          ". Top-level business_executive stays " +
          (contacts.business_executive == null ? "null" : String(contacts.business_executive)) +
          ". Not an officer. Not stock.";
      }
      if (cards[2]) {
        cards[2].textContent =
          "false. Mailbox is not an Entra oid. Mailbox is not a click. The Cloud Agent is not a contact.";
      }
    }
    var ladder = $("app-program-ladder");
    if (ladder && data.ladder) {
      ladder.textContent = "";
      data.ladder.forEach(function (item) {
        var li = document.createElement("li");
        li.setAttribute("data-status", item.status || "");
        li.setAttribute("data-id", item.id || "");
        var kicker = document.createElement("p");
        kicker.className = "kicker";
        kicker.textContent =
          "Order " +
          (item.apply_order || "") +
          " · " +
          (item.status || "") +
          " · membership claimed=" +
          String(!!item.membership_claimed);
        var h = document.createElement("h3");
        h.textContent = item.name || "";
        var p = document.createElement("p");
        p.textContent = item.pitch_rule || item.note || "";
        var meta = document.createElement("p");
        meta.className = "note";
        meta.textContent =
          (item.cost || "") +
          ". Ready to apply=" +
          String(!!item.ready_to_apply) +
          ". Eligible to prepare=" +
          String(!!item.eligible_to_prepare) +
          ".";
        li.appendChild(kicker);
        li.appendChild(h);
        li.appendChild(p);
        li.appendChild(meta);
        ladder.appendChild(li);
      });
    }
    list($("app-program-prereqs"), data.apply_prerequisites);
  }

  function boot() {
    showWorkspace(workspaceFromHash());
    window.addEventListener("hashchange", function () {
      showWorkspace(workspaceFromHash());
    });
    fetch("control-plane.json")
      .then(function (res) {
        return res.ok ? res.json() : null;
      })
      .then(function (data) {
        if (data) paintFloor(data);
      })
      .catch(function () {});
    fetch("investor.json")
      .then(function (res) {
        return res.ok ? res.json() : null;
      })
      .then(function (data) {
        if (data) paintCapital(data);
      })
      .catch(function () {});
    fetch("programs.json")
      .then(function (res) {
        return res.ok ? res.json() : null;
      })
      .then(function (data) {
        if (data) paintPrograms(data);
      })
      .catch(function () {});
    fetch("schema.json")
      .then(function (res) {
        return res.ok ? res.json() : null;
      })
      .then(function (schema) {
        var node = document.getElementById("schema-graph");
        if (!node || !schema || schema.cms || schema.live_pin_ok) return;
        node.textContent = JSON.stringify(schema);
      })
      .catch(function () {});
  }

  boot();
})();
