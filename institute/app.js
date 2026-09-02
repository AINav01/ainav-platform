(function () {
  "use strict";

  var WORKSPACES = ["floor", "capital", "business", "programs"];
  var VIEW_COPY = {
    entire: {
      title: "Entire plane",
      note: "Anyone on the tenant. Can: see the ledger and the freeze state. Cannot: a view is not a seat."
    },
    client: {
      title: "Client executive",
      note: "The client executive dashboard is this plane. Estate is the same plane: other uses, failsafe, records, maps. Included with L1. Not an upsell."
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
    },
    remote: {
      title: "Remote human",
      note: "Same Entra object id from any network. MFA may identify. It does not admit."
    },
    it: {
      title: "IT / identity",
      note: "Host Copilot and agents. PIM is not dual. MFA is identify, not admit."
    },
    provision: {
      title: "Provision / upsells",
      note: "Standard seating plus options. Not a second dashboard SKU. U-DUAL never free."
    },
    records: {
      title: "Records / keep",
      note: "First record, second record, weekly keep. Not a certificate."
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

  var SHOW_TO_TILE = {
    seats: "seats_recorded",
    maps: "compliance_maps",
    signed_l1: "signed_l1",
    off_switch: "off_switch",
    pending_admits: "pending_admits",
    first_record: "first_record",
    second_record: "second_record"
  };

  function tilesForView(viewId, tiles, views, board) {
    var list = tiles || [];
    if (viewId === "entire") return list;
    if (viewId === "client") {
      var wanted = (board && board.tile_ids) || [];
      if (!wanted.length) return list;
      return list.filter(function (item) {
        return wanted.indexOf(item.id) >= 0;
      });
    }
    var view = (views || []).filter(function (item) {
      return item.id === viewId;
    })[0];
    var shows = (view && view.shows) || [];
    var ids = shows
      .map(function (key) {
        return SHOW_TO_TILE[key] || key;
      })
      .filter(Boolean);
    if (!ids.length) return list;
    return list.filter(function (item) {
      return ids.indexOf(item.id) >= 0;
    });
  }

  function pickById(items, ids) {
    var map = {};
    (items || []).forEach(function (item) {
      if (item && item.id) map[item.id] = item;
    });
    return (ids || [])
      .map(function (id) {
        return map[id];
      })
      .filter(Boolean);
  }

  function setView(id, data) {
    var views = (data && data.views) || [];
    var board = ((data && data.client_dashboard) || {}).executive_board || {};
    var copy = VIEW_COPY[id] || VIEW_COPY.client;
    var match = views.filter(function (item) {
      return item.id === id || item.view === id;
    })[0];
    if (match) {
      copy = {
        title: match.name || match.label || copy.title,
        note: match.can || match.note || copy.note
      };
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
    paintTiles($("app-floor-tiles"), tilesForView(id, data.tiles, views, board));
    var boardRoot = $("app-floor-board");
    var governRoot = $("app-floor-govern");
    var estateRoot = $("app-floor-estate");
    var showGlance = id === "client" || id === "entire" || id === "provision";
    var showGovern = showGlance || id === "owner" || id === "it" || id === "remote";
    var showEstate = showGovern || id === "examiner" || id === "records";
    if (boardRoot) boardRoot.hidden = !showGlance;
    if (governRoot) governRoot.hidden = !showGovern;
    if (estateRoot) estateRoot.hidden = !showEstate;
  }

  function paintOfferBoard(root, offer) {
    var glance = (offer && offer.first_glance) || {};
    if (!root || !glance.columns || !glance.columns.length) return;
    if (offer.sku || offer.fourth_sku || offer.included_means_free) return;
    root.textContent = "";
    glance.columns.forEach(function (item) {
      var art = document.createElement("article");
      art.setAttribute("data-band", item.upsell === true ? "advanced" : "standard");
      var h = document.createElement("h3");
      h.textContent = item.name || "";
      var price = document.createElement("p");
      price.className = "price";
      price.textContent = item.price || "";
      var ul = document.createElement("ul");
      ul.className = "stack";
      (item.items || []).forEach(function (line) {
        var li = document.createElement("li");
        li.textContent = line;
        ul.appendChild(li);
      });
      art.appendChild(h);
      art.appendChild(price);
      art.appendChild(ul);
      root.appendChild(art);
    });
  }

  function paintAssignment(root, assign, departments) {
    if (!root) return;
    var tbody = root.querySelector("tbody") || root;
    tbody.textContent = "";
    var depts = {};
    (departments || []).forEach(function (item) {
      if (item && item.id) depts[item.id] = item;
    });
    (assign.matrix || []).forEach(function (row) {
      var tr = document.createElement("tr");
      var names = (row.org_nodes || [])
        .map(function (id) {
          return (depts[id] && depts[id].name) || id;
        })
        .join(", ");
      [
        names,
        row.org_role || "",
        row.default_view || "",
        row.may_bind === true ? "yes" : "no",
        row.provision_band === "provision.advanced" ? "options" : "standard"
      ].forEach(function (value) {
        var td = document.createElement("td");
        td.textContent = value;
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  }

  function paintLifecycle(root, items, priceKey) {
    if (!root || !items || !items.length) return;
    root.textContent = "";
    items.forEach(function (item) {
      var art = document.createElement("article");
      art.setAttribute("data-tone", item.live === true ? "list" : "hold");
      var h = document.createElement("h3");
      h.textContent = item.name || item.label || "";
      var price = document.createElement("p");
      price.className = "price";
      price.textContent = item[priceKey] || item.grants || item.effect || "";
      var note = document.createElement("p");
      note.className = "note";
      note.textContent = item.note || "";
      art.appendChild(h);
      art.appendChild(price);
      art.appendChild(note);
      root.appendChild(art);
    });
  }

  function paintMfa(root, mfa) {
    if (!root || !mfa) return;
    if (mfa.sku || mfa.mfa_live || mfa.is_admit) return;
    root.textContent = "";
    ["internal", "remote"].forEach(function (key) {
      var item = mfa[key];
      if (!item) return;
      var art = document.createElement("article");
      art.setAttribute("data-band", key === "remote" ? "advanced" : "standard");
      var h = document.createElement("h3");
      h.textContent = item.name || key;
      var price = document.createElement("p");
      price.className = "price";
      price.textContent = item.mfa || "";
      var ul = document.createElement("ul");
      ul.className = "stack";
      [item.identify, "Admit: " + String(!!item.admit), "MFA live: " + String(!!item.mfa_live)].forEach(function (line) {
        if (!line) return;
        var li = document.createElement("li");
        li.textContent = line;
        ul.appendChild(li);
      });
      art.appendChild(h);
      art.appendChild(price);
      art.appendChild(ul);
      root.appendChild(art);
    });
  }

  function paintMaps(root, items) {
    if (!root) return;
    var tbody = root.querySelector("tbody") || root;
    tbody.textContent = "";
    (items || []).forEach(function (item) {
      var tr = document.createElement("tr");
      [item.name || "", item.maps_to || "", item.scope || "", "false"].forEach(function (value) {
        var td = document.createElement("td");
        td.textContent = value;
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  }

  function paintNotes(root, items) {
    if (!root || !items || !items.length) return;
    root.textContent = "";
    items.forEach(function (item) {
      var art = document.createElement("article");
      art.setAttribute("data-tone", "hold");
      var h = document.createElement("h3");
      h.textContent = item.name || "";
      var p = document.createElement("p");
      p.className = "note";
      p.textContent = item.note || "";
      art.appendChild(h);
      art.appendChild(p);
      root.appendChild(art);
    });
  }

  function paintUses(root, bands) {
    if (!root || !bands || !bands.length) return;
    root.textContent = "";
    bands.forEach(function (item) {
      var art = document.createElement("article");
      art.setAttribute("data-tone", "hold");
      var h = document.createElement("h3");
      h.textContent = item.name || "";
      var price = document.createElement("p");
      price.className = "price";
      price.textContent = item.sku || "";
      var p = document.createElement("p");
      p.className = "note";
      p.textContent = item.note || "";
      var ul = document.createElement("ul");
      ul.className = "stack";
      var wedge = (item.wedge || []).join(", ");
      if (wedge) {
        var li = document.createElement("li");
        li.textContent = "Wedge: " + wedge;
        ul.appendChild(li);
      }
      var desks = (item.desks || []).join(", ");
      if (desks) {
        var li = document.createElement("li");
        li.textContent = "Desks: " + desks;
        ul.appendChild(li);
      }
      art.appendChild(h);
      if (price.textContent) art.appendChild(price);
      art.appendChild(p);
      if (ul.childNodes.length) art.appendChild(ul);
      root.appendChild(art);
    });
  }

  function paintOversee(root, items) {
    if (!root || !items || !items.length) return;
    root.textContent = "";
    items.forEach(function (item) {
      var art = document.createElement("article");
      art.setAttribute("data-tone", "hold");
      var h = document.createElement("h3");
      h.textContent = item.name || "";
      var price = document.createElement("p");
      price.className = "price";
      price.textContent = item.role || "oversee";
      var ul = document.createElement("ul");
      ul.className = "stack";
      [
        "Admit: " + String(!!item.admit),
        "Freeze: " + (item.freeze || "request"),
        "Keep: " + (item.keep || "view")
      ].forEach(function (line) {
        var li = document.createElement("li");
        li.textContent = line;
        ul.appendChild(li);
      });
      var p = document.createElement("p");
      p.className = "note";
      p.textContent = item.note || "";
      art.appendChild(h);
      art.appendChild(price);
      art.appendChild(ul);
      art.appendChild(p);
      root.appendChild(art);
    });
  }

  function paintFloor(data) {
    if (!data || data.sku || data.live_pin_ok) return;
    var glance = (data.dashboard && data.dashboard.first_glance) || {};
    var board = (data.client_dashboard && data.client_dashboard.executive_board) || {};
    if (board.sku || board.upsell) return;
    if (glance.lede) setText("app-floor-lede", glance.lede);
    if (board.lede) setText("app-floor-board-lede", board.lede);
    paintRail($("app-write-rail"), glance.write_rail);
    paintStrip($("app-floor-strip"), data.tiles);
    paintTiles($("app-floor-attention"), pickById(data.attention, board.attention_ids));
    paintTiles(
      $("app-floor-seats"),
      pickById(data.tiles, (board.seat_tile_ids || []).concat(board.keep_tile_ids || []))
    );
    var offer = data.included_and_upsells || {};
    if (offer.first_glance && offer.first_glance.lede) setText("app-floor-offer-lede", offer.first_glance.lede);
    paintOfferBoard($("app-floor-offer"), offer);
    var estate = data.estate || {};
    if (!(estate.sku || estate.fourth_sku || estate.live_pin_ok)) {
      var glanceE = estate.first_glance || {};
      if (glanceE.lede) setText("app-floor-estate-lede", glanceE.lede);
      if (estate.other_uses && estate.other_uses.lede) setText("app-floor-uses-lede", estate.other_uses.lede);
      paintUses($("app-floor-uses"), estate.other_uses && estate.other_uses.bands ? estate.other_uses.bands : []);
      if (estate.failsafe && estate.failsafe.lede) setText("app-floor-failsafe-lede", estate.failsafe.lede);
      paintNotes($("app-floor-failsafe"), estate.failsafe && estate.failsafe.verbs ? estate.failsafe.verbs : []);
      if (estate.executive && estate.executive.lede) setText("app-floor-exec-lede", estate.executive.lede);
      paintOversee($("app-floor-exec"), [
        Object.assign({ name: "Owner / executive" }, estate.executive && estate.executive.owner ? estate.executive.owner : {}),
        Object.assign({ name: "Board" }, estate.executive && estate.executive.board ? estate.executive.board : {})
      ]);
      if (estate.records && estate.records.lede) setText("app-floor-records-lede", estate.records.lede);
      paintNotes($("app-floor-records"), estate.records && estate.records.items ? estate.records.items : []);
      if (estate.immutable && estate.immutable.lede) setText("app-floor-immutable-lede", estate.immutable.lede);
      paintNotes($("app-floor-immutable"), (data.governance_immutable && data.governance_immutable.pins) || []);
      if (estate.instruments && estate.instruments.lede) setText("app-floor-maps-lede", estate.instruments.lede);
      paintMaps($("app-floor-maps"), data.maps || []);
      var cons = data.governance_consequences || {};
      if (cons.thesis) setText("app-floor-consequences", cons.thesis);
    }
    var assign = data.view_assignment || {};
    if (!(assign.sku || assign.upsell || assign.assignment_live)) {
      var glanceA = assign.first_glance || {};
      if (glanceA.lede) setText("app-floor-assign-lede", glanceA.lede);
      paintAssignment($("app-floor-assign"), assign, data.departments);
      var auth = assign.authorize || {};
      if (auth.note) setText("app-floor-auth-lede", auth.note);
      paintLifecycle($("app-floor-auth"), data.authorizations || [], "grants");
      paintLifecycle($("app-floor-revoke"), data.revocations || [], "effect");
      var mfa = assign.mfa || {};
      if (mfa.note) setText("app-floor-mfa-lede", mfa.note);
      paintMfa($("app-floor-mfa"), mfa);
      var disc = assign.disclaimers || {};
      if (disc.lede) setText("app-floor-legal-lede", disc.lede);
      paintNotes($("app-floor-legal"), disc.items || []);
      paintNotes($("app-floor-advantage"), (assign.advantage && assign.advantage.items) || []);
    }
    var tabs = $("app-view-tabs");
    if (tabs && !tabs.getAttribute("data-bound")) {
      tabs.setAttribute("data-bound", "true");
      tabs.addEventListener("click", function (event) {
        var btn = event.target.closest("[data-view]");
        if (!btn) return;
        setView(btn.getAttribute("data-view"), data);
      });
    }
    setView(board.default_view || "client", data);
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
    if (data.why_client) setText("app-capital-why-client", data.why_client);
    if (data.why_investor) setText("app-capital-why-investor", data.why_investor);
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
    paintScenarioTable($("app-capital-scenarios"), data.scenarios);
  }

  function paintScenarioTable(table, rows) {
    var body = table ? table.querySelector("tbody") : null;
    if (!body || !rows) return;
    body.textContent = "";
    rows.forEach(function (row) {
      var tr = document.createElement("tr");
      var th = document.createElement("th");
      th.textContent = row.if || row.name || "";
      var td = document.createElement("td");
      td.textContent = "$" + Number(row.min || 0).toLocaleString() + "–$" + Number(row.max || 0).toLocaleString();
      tr.appendChild(th);
      tr.appendChild(td);
      body.appendChild(tr);
    });
  }

  function namedList(root, items, pick) {
    if (!root) return;
    root.textContent = "";
    (items || []).forEach(function (item) {
      var li = document.createElement("li");
      li.textContent = pick ? pick(item) : item;
      root.appendChild(li);
    });
  }

  function paintBusiness(data) {
    if (!data || data.cms || data.priced_round || data.forecast || data.live_pin_ok) return;
    var two = data.number_two || {};
    if (two.all_aspects || two.officer || two.seat_clicked || two.entra_oid) return;
    if (data.thesis) setText("app-business-lede", data.thesis);
    setText("app-business-commercial", (data.commercial || "") + ". Closed: false. Lab pin is " + (data.lab_pin || "LIVE_PIN_OK") + ".");
    var elevator = data.elevator || {};
    if (elevator.ten) setText("app-business-elevator-ten", elevator.ten);
    if (elevator.thirty) setText("app-business-elevator-thirty", elevator.thirty);
    if (elevator.ask) setText("app-business-elevator-ask", elevator.ask);
    if (data.why_client) setText("app-business-why-client", data.why_client);
    if (data.why_investor) setText("app-business-why-investor", data.why_investor);
    var offer = data.included_and_upsells || {};
    if (!offer.sku && !offer.fourth_sku && !offer.included_means_free) {
      var glance = offer.first_glance || {};
      if (glance.lede) setText("app-business-offer-lede", glance.lede);
      if (offer.attach_means) setText("app-business-attach", offer.attach_means);
      var offerRoot = $("app-business-offer");
      if (offerRoot && glance.columns && glance.columns.length) {
        offerRoot.textContent = "";
        glance.columns.forEach(function (item) {
          var art = document.createElement("article");
          art.setAttribute("data-band", item.upsell === true ? "advanced" : "standard");
          var h = document.createElement("h3");
          h.textContent = item.name || "";
          var price = document.createElement("p");
          price.className = "price";
          price.textContent = item.price || "";
          var ul = document.createElement("ul");
          ul.className = "stack";
          (item.items || []).forEach(function (line) {
            var li = document.createElement("li");
            li.textContent = line;
            ul.appendChild(li);
          });
          art.appendChild(h);
          art.appendChild(price);
          art.appendChild(ul);
          offerRoot.appendChild(art);
        });
      }
    }
    var close = data.close || {};
    var kpis = $("app-business-close");
    if (kpis) {
      var map = {
        "Named dual seats": close.named_dual_seats ? "claimed" : "open",
        "Proof day sold": String(!!close.proof_day_sold),
        "Signed L1": String(close.signed_l1 || 0),
        "Commercial close": close.closed ? "claimed" : "open"
      };
      Array.prototype.forEach.call(kpis.querySelectorAll("article"), function (art) {
        var label = (art.querySelector("h3") || {}).textContent;
        var price = art.querySelector(".price");
        if (price && map[label]) price.textContent = map[label];
      });
    }
    var path = $("app-business-path");
    if (path && data.path) {
      path.textContent = "";
      data.path.forEach(function (item) {
        var li = document.createElement("li");
        li.setAttribute("data-status", item.state || "");
        var kicker = document.createElement("p");
        kicker.className = "kicker";
        kicker.textContent = item.state || "";
        var h = document.createElement("h3");
        h.textContent = item.name || "";
        var p = document.createElement("p");
        p.textContent = item.note || "";
        li.appendChild(kicker);
        li.appendChild(h);
        li.appendChild(p);
        path.appendChild(li);
      });
    }
    var bake = data.bake_off || {};
    setText("app-business-bake-lede", bake.lede || "");
    namedList($("app-business-they-win"), bake.they_win, function (item) {
      return (item.name || "") + " — " + (item.note || "");
    });
    namedList($("app-business-we-win"), bake.we_win, function (item) {
      return (item.name || "") + " — " + (item.note || "");
    });
    namedList($("app-business-walk"), (data.qualify || {}).walk_away);
    var objections = $("app-business-objections");
    if (objections && data.objections) {
      objections.textContent = "";
      data.objections.forEach(function (item) {
        var art = document.createElement("article");
        var h = document.createElement("h3");
        h.textContent = item.hear || "";
        var p = document.createElement("p");
        p.textContent = item.answer || "";
        art.appendChild(h);
        art.appendChild(p);
        objections.appendChild(art);
      });
    }
    paintScenarioTable($("app-business-scenarios"), data.scenarios);
    list($("app-business-missing"), data.honest_missing);
    if (two.note) setText("app-business-number-two", two.note);
    namedList($("app-business-manages"), two.manages);
    namedList($("app-business-cannot"), two.cannot);
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
    fetch("plane-business.json")
      .then(function (res) {
        return res.ok ? res.json() : null;
      })
      .then(function (data) {
        if (data) paintBusiness(data);
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
