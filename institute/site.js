(function () {
  "use strict";

  function paintIntegrate(rootId, body) {
    var root = document.getElementById(rootId);
    if (!root || !body || !body.items || !body.items.length) return;
    root.textContent = "";
    body.items.forEach(function (item) {
      var li = document.createElement("li");
      var url = String(item.url || "");
      var label = item.url_label || item.name || "";
      var note = item.note || "";
      if (
        url.indexOf("https://") === 0 &&
        url.toLowerCase().indexOf("entra_client") === -1 &&
        url.indexOf("2ad041b8") === -1
      ) {
        var a = document.createElement("a");
        a.setAttribute("href", url);
        a.textContent = label;
        li.appendChild(a);
        li.appendChild(document.createTextNode(note ? " — " + note : ""));
      } else {
        li.textContent = label + (note ? " — " + note : "");
      }
      root.appendChild(li);
    });
  }

  document.querySelectorAll("a[href^='#']").forEach(function (link) {
    link.addEventListener("click", function (event) {
      var id = link.getAttribute("href").slice(1);
      var target = document.getElementById(id);
      if (!target) return;
      event.preventDefault();
      target.scrollIntoView({ behavior: "smooth", block: "start" });
      if (history.replaceState) history.replaceState(null, "", "#" + id);
      var box = document.getElementById("nav-open");
      if (box) box.checked = false;
    });
  });

  fetch("governance.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data || data.live || data.live_pin_ok || data.sku || data.certified) return;
      var thesis = document.getElementById("gov-thesis");
      if (thesis && data.thesis) thesis.textContent = data.thesis;
      var cascade = document.getElementById("gov-cascade");
      if (cascade && data.cascade && data.cascade.does) {
        cascade.textContent = "Cascade: " + data.cascade.does + " Invented names: refused.";
      }
      var records = document.getElementById("gov-records");
      if (records && data.records && data.records.first && data.records.second) {
        records.textContent =
          "First record: " +
          data.records.first.what +
          " Second record: " +
          data.records.second.what;
      }
      var must = document.getElementById("gov-must");
      if (must && data.must_have && data.must_have.why) {
        must.textContent =
          "Must-have: " +
          data.must_have.why +
          " For owner, board, examiner. Mandated: false. Not a fourth SKU.";
      }
      var mustFor = document.getElementById("must-for");
      if (mustFor && data.must_have && data.must_have.for) {
        var labels = { owner: "Owner", board: "Board", examiner: "Examiner" };
        mustFor.textContent = "";
        ["owner", "board", "examiner"].forEach(function (who) {
          if (!data.must_have.for[who]) return;
          var art = document.createElement("article");
          var h = document.createElement("h3");
          h.textContent = labels[who];
          var p = document.createElement("p");
          p.textContent = data.must_have.for[who];
          art.appendChild(h);
          art.appendChild(p);
          mustFor.appendChild(art);
        });
      }
      var plane = document.getElementById("gov-plane");
      if (plane && data.plane && data.plane.off_switch && data.plane.rollback) {
        plane.textContent =
          "Off switch: " +
          data.plane.off_switch.does +
          " Reset: " +
          (data.plane.reset && data.plane.reset.does ? data.plane.reset.does + " " : "") +
          "Rollback: " +
          data.plane.rollback.does;
      }
      function fill(id, items, line) {
        var root = document.getElementById(id);
        if (!root || !items || !items.length) return;
        root.textContent = "";
        items.forEach(function (item) {
          var li = document.createElement("li");
          li.textContent = line(item);
          root.appendChild(li);
        });
      }
      fill("gov-separate", (data.failsafe && data.failsafe.separate_from) || [], function (item) {
        return item;
      });
      fill("gov-maps", data.maps || [], function (item) {
        return item.name + " — " + item.scope + ". Claimed: false.";
      });
      fill("gov-risks", data.risks || [], function (item) {
        return item.harm;
      });
      fill("gov-refuse", data.refuse || [], function (item) {
        return item;
      });
    })
    .catch(function () {
      /* governance.json is optional when opened as a file */
    });

  fetch("control-plane.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data || data.live || data.live_pin_ok || data.sku || data.certified || data.real_time_claimed) return;
      function set(id, text) {
        var node = document.getElementById(id);
        if (node && text) node.textContent = text;
      }
      function fill(id, items, line) {
        var root = document.getElementById(id);
        if (!root || !items || !items.length) return;
        root.textContent = "";
        items.forEach(function (item) {
          var li = document.createElement("li");
          li.textContent = line(item);
          root.appendChild(li);
        });
      }
      if (data.release) {
        document.querySelectorAll("#control-plane > .kicker").forEach(function (node) {
          node.textContent =
            "Ultimate control plane · " +
            data.release +
            " · must-have · not a SKU · not LIVE_PIN_OK";
        });
      }
      function paintOffer(rootId, offer) {
        var root = document.getElementById(rootId);
        var glance = (offer && offer.first_glance) || {};
        if (!root || !glance.columns || !glance.columns.length) return;
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
      var offer = data.included_and_upsells || {};
      if (!offer.sku && !offer.fourth_sku && !offer.included_means_free) {
        var offerGlance = offer.first_glance || {};
        if (offerGlance.lede) {
          set("commercial-lede", offerGlance.lede);
          set("plane-offer-lede", offerGlance.lede);
        }
        if (offer.attach_means) set("commercial-attach", offer.attach_means);
        paintOffer("included-upsells", offer);
        paintOffer("plane-offer", offer);
        fill("commercial-refuse", offer.refuse || [], function (item) {
          return item;
        });
      }
      var dashGlance = (data.dashboard && data.dashboard.first_glance) || {};
      var floorGlance = (data.floor && data.floor.first_glance) || {};
      if (dashGlance.lede) set("plane-dash-lede", dashGlance.lede);
      var planeRail = document.getElementById("plane-write-rail");
      var railItems = dashGlance.write_rail || floorGlance.write_rail;
      if (planeRail && railItems && railItems.length) {
        planeRail.textContent = "";
        railItems.forEach(function (item) {
          var li = document.createElement("li");
          if (item.id) li.setAttribute("data-step", item.id);
          var b = document.createElement("b");
          b.textContent = item.name || "";
          var span = document.createElement("span");
          span.textContent = item.note || "";
          li.appendChild(b);
          li.appendChild(span);
          planeRail.appendChild(li);
        });
      }
      var thesisNode = document.getElementById("plane-thesis");
      if (thesisNode && data.floor && data.floor.lede && thesisNode.getAttribute("data-keep") === "short") {
        thesisNode.textContent = data.floor.lede;
      } else if (thesisNode && data.thesis && thesisNode.getAttribute("data-keep") !== "short") {
        thesisNode.textContent = data.thesis;
      }
      if (!thesisNode || thesisNode.getAttribute("data-keep") !== "short") {
        set("plane-doctrine", data.thesis);
      }
      function paintCards(id, items, titleKey, noteKey) {
        var root = document.getElementById(id);
        if (!root || !items || !items.length) return;
        root.textContent = "";
        items.forEach(function (item) {
          var art = document.createElement("article");
          var h = document.createElement("h3");
          h.textContent = item[titleKey] || item.name || "";
          var p = document.createElement("p");
          p.textContent = item[noteKey] || item.note || "";
          art.appendChild(h);
          art.appendChild(p);
          root.appendChild(art);
        });
      }
      if (data.floor && data.floor.not_the_gate) {
        paintCards("not-the-gate", data.floor.not_the_gate, "name", "note");
        var glance = data.floor.first_glance || {};
        if (glance.lede) set("hero-contrast-lede", glance.lede);
        var contrast = document.getElementById("hero-contrast");
        if (contrast) {
          var pin = contrast.querySelector("[data-pin='job-c']");
          if (pin && glance.job_c) {
            pin.setAttribute("data-lane", "gate");
            var pinNote = pin.querySelector("p");
            if (pinNote) pinNote.textContent = glance.job_c;
          }
          Array.prototype.slice.call(contrast.querySelectorAll("article:not([data-pin])")).forEach(function (art) {
            art.parentNode.removeChild(art);
          });
          data.floor.not_the_gate.forEach(function (item) {
            var art = document.createElement("article");
            art.setAttribute("data-lane", "copy");
            var h = document.createElement("h3");
            h.textContent = item.name || "";
            var p = document.createElement("p");
            p.textContent = item.note || "";
            art.appendChild(h);
            art.appendChild(p);
            contrast.appendChild(art);
          });
        }
      }
      if (data.floor && data.floor.accountable && data.floor.accountable.items) {
        paintCards("accountable", data.floor.accountable.items, "name", "note");
        set("hero-accountable", (data.floor.accountable.lede || "") + " Lab oids are not two named treasury humans.");
        set("buyer-duty", data.floor.accountable.lede || "");
      }
      if (data.floor && data.floor.protect && data.floor.protect.items) {
        paintCards("protect", data.floor.protect.items, "name", "note");
        var prot = data.floor.protect;
        var protBy = {};
        (prot.items || []).forEach(function (item) {
          protBy[item.id] = item;
        });
        var policyNote = (protBy.policy && protBy.policy.note) || "";
        set("hero-protect", (prot.lede || "") + (policyNote ? " " + policyNote : ""));
        set("buyer-protect-lede", prot.lede || "");
      }
      if (data.floor && data.floor.memory && data.floor.memory.items) {
        paintCards("memory", data.floor.memory.items, "name", "note");
        var mem = data.floor.memory;
        var memBy = {};
        (mem.items || []).forEach(function (item) {
          memBy[item.id] = item;
        });
        var rollbackNote = (memBy.rollback && memBy.rollback.note) || "";
        set(
          "hero-memory",
          (mem.lede || "") +
            " Reset is the last sealed keep." +
            (rollbackNote ? " " + rollbackNote : "") +
            " A mailbox is not the second record."
        );
        set("buyer-memory-lede", mem.lede || "");
      }
      if (data.floor && data.floor.integrate && data.floor.integrate.items) {
        paintIntegrate("integrate", data.floor.integrate);
        set("hero-integrate", (data.floor.integrate.lede || "") + " The owner clicks the Microsoft admin links. Do not create a new Entra app.");
        set("buyer-integrate-lede", data.floor.integrate.lede || "");
      }
      if (data.floor && data.floor.page) {
        set("hero-sale", (data.floor.page.sale || "The sale is the ninety-minute proof.") + " The product is the admit plane.");
      }
      if (data.floor && data.floor.proof_close) {
        var close = data.floor.proof_close;
        var noMeans = data.floor.no_means || {};
        paintCards("proof-close", [
          { name: "Walk in", note: (close.minutes || 90) + " minutes. " + (close.walk_in || "") },
          { name: "Walk out", note: (close.walk_out || []).join(". ") + ". " + (close.note || "") },
          { name: "What no does", note: (noMeans.refuse || "") + " " + (noMeans.fail_closed || "") + " " + (noMeans.off_switch || "") }
        ], "name", "note");
      }
      if (data.equation) set("plane-equation", "Interface = " + data.equation);
      if (data.dashboard && data.dashboard.realtime_means) set("plane-realtime", data.dashboard.realtime_means);
      set("plane-week-one", "Three scopes. One dashboard. Attached 0 / 0 / 0.");
      if (data.access) {
        set(
          "plane-access",
          "Internal: " +
            data.access.internal +
            " Remote: " +
            data.access.remote +
            " Same plane. Not a VPN SKU."
        );
      }
      if (data.letter) set("plane-letter", data.letter);
      function flag(value) {
        if (value === true) return "yes";
        if (value === false) return "no";
        if (value == null) return "no";
        return String(value);
      }
      function cell(text) {
        var td = document.createElement("td");
        td.textContent = text;
        return td;
      }
      function fillRows(id, rows, cells, role) {
        var root = document.getElementById(id);
        if (!root || !rows || !rows.length) return;
        root.textContent = "";
        rows.forEach(function (item) {
          var tr = document.createElement("tr");
          if (role) tr.setAttribute("data-role", role(item));
          cells(item).forEach(function (value) {
            tr.appendChild(cell(value));
          });
          root.appendChild(tr);
        });
      }
      var tiles = document.getElementById("plane-tiles");
      if (tiles && data.tiles && data.tiles.length) {
        tiles.textContent = "";
        data.tiles.forEach(function (item) {
          var art = document.createElement("article");
          art.setAttribute("data-tone", item.tone || "hold");
          var h = document.createElement("h3");
          h.textContent = item.label;
          var p = document.createElement("p");
          p.className = "price";
          p.textContent = item.value;
          var n = document.createElement("p");
          n.className = "note";
          n.textContent = item.note || "";
          art.appendChild(h);
          art.appendChild(p);
          art.appendChild(n);
          tiles.appendChild(art);
        });
      }
      var strip = document.getElementById("plane-strip");
      if (strip && data.tiles && data.tiles.length) {
        var wanted = {
          plane_state: "Plane",
          pending_admits: "Pending",
          off_switch: "Off switch",
          recognized_revenue: "Revenue",
          signed_l1: "Signed L1",
          seats_recorded: "Seats"
        };
        strip.textContent = "";
        data.tiles.forEach(function (item) {
          if (!wanted[item.id]) return;
          var span = document.createElement("span");
          span.appendChild(document.createTextNode(wanted[item.id] + " "));
          var b = document.createElement("b");
          b.textContent = item.value;
          span.appendChild(b);
          strip.appendChild(span);
        });
      }
      var cascade = document.getElementById("plane-cascade");
      if (cascade && data.cascade && data.cascade.length) {
        cascade.textContent = "";
        data.cascade.forEach(function (item) {
          var art = document.createElement("article");
          art.setAttribute("data-role", item.role || "");
          var h = document.createElement("h3");
          h.textContent = item.label;
          var p = document.createElement("p");
          p.textContent = (item.names || []).join(" · ");
          art.appendChild(h);
          art.appendChild(p);
          cascade.appendChild(art);
        });
      }
      fillRows("plane-levels", data.levels || [], function (item) {
        return [item.name, item.role, flag(item.admit), flag(item.freeze), flag(item.keep), item.note || ""];
      }, function (item) {
        return item.role || "";
      });
      fillRows("plane-depts", data.departments || [], function (item) {
        return [item.name, item.role, item.seat || "—", item.ai || "Not a seat.", item.note || ""];
      }, function (item) {
        return item.role || "";
      });
      var assign = data.view_assignment || {};
      if (assign.first_glance && assign.first_glance.lede) set("plane-assign-lede", assign.first_glance.lede);
      var deptsById = {};
      (data.departments || []).forEach(function (item) {
        if (item && item.id) deptsById[item.id] = item;
      });
      fillRows("plane-assign", assign.matrix || [], function (row) {
        var names = (row.org_nodes || [])
          .map(function (id) {
            return (deptsById[id] && deptsById[id].name) || id;
          })
          .join(", ");
        return [
          names,
          row.org_role || "",
          row.default_view || "",
          row.may_bind === true ? "yes" : "no",
          row.provision_band === "provision.advanced" ? "options" : "standard"
        ];
      });
      if (assign.mfa && assign.mfa.note) set("plane-mfa-lede", assign.mfa.note);
      var mfaRoot = document.getElementById("plane-mfa");
      if (mfaRoot && assign.mfa && !assign.mfa.sku && !assign.mfa.mfa_live && !assign.mfa.is_admit) {
        mfaRoot.textContent = "";
        ["internal", "remote"].forEach(function (key) {
          var item = assign.mfa[key];
          if (!item) return;
          card(mfaRoot, {
            name: item.name || key,
            state: item.mfa || "",
            note: (item.identify || "") + ". Admit: " + String(!!item.admit) + ". MFA live: " + String(!!item.mfa_live)
          }, function (art) {
            art.setAttribute("data-band", key === "remote" ? "advanced" : "standard");
          });
        });
      }
      if (assign.disclaimers && assign.disclaimers.lede) set("plane-legal-lede", assign.disclaimers.lede);
      paintBoard("plane-legal", assign.disclaimers && assign.disclaimers.items ? assign.disclaimers.items : [], function () {
        return "AINav, Inc.";
      });
      var estate = data.estate || {};
      if (estate.first_glance && estate.first_glance.lede) set("plane-estate-lede", estate.first_glance.lede);
      paintBoard(
        "plane-estate-glance",
        ((estate.first_glance && estate.first_glance.columns) || []).map(function (item) {
          return Object.assign({}, item, {
            note: (item.items || []).join(". ")
          });
        }),
        function (item) {
          return item.price || "same plane";
        }
      );
      paintBoard(
        "plane-uses",
        ((estate.other_uses && estate.other_uses.bands) || []).map(function (item) {
          var wedge = (item.wedge || []).join(", ");
          var desks = (item.desks || []).join(", ");
          return Object.assign({}, item, {
            note:
              (item.note || "") +
              (wedge ? " Wedge: " + wedge + "." : "") +
              (desks ? " Desks: " + desks + "." : "")
          });
        }),
        function (item) {
          return item.sku || "desk";
        }
      );
      paintBoard("plane-failsafe", estate.failsafe && estate.failsafe.verbs ? estate.failsafe.verbs : [], function () {
        return "failsafe";
      });
      if (estate.executive && estate.executive.lede) set("plane-exec-lede", estate.executive.lede);
      paintBoard("plane-exec", [
        Object.assign({ name: "Owner / executive" }, estate.executive && estate.executive.owner ? estate.executive.owner : {}),
        Object.assign({ name: "Board" }, estate.executive && estate.executive.board ? estate.executive.board : {})
      ], function (item) {
        return item.role || "oversee";
      });
      paintBoard("plane-estate-records", estate.records && estate.records.items ? estate.records.items : [], function () {
        return "record";
      });
      if (estate.immutable && estate.immutable.lede) set("plane-immutable-lede", estate.immutable.lede);
      paintBoard("plane-immutable", (data.governance_immutable && data.governance_immutable.pins) || [], function () {
        return "pin";
      });
      if (data.governance_consequences && data.governance_consequences.thesis) {
        set("plane-consequences", data.governance_consequences.thesis);
      }
      var audit = data.audit || {};
      if (audit.first_glance && audit.first_glance.lede) set("plane-audit-lede", audit.first_glance.lede);
      paintBoard(
        "plane-audit-glance",
        ((audit.first_glance && audit.first_glance.columns) || []).map(function (item) {
          return Object.assign({}, item, {
            note: (item.items || []).join(". ")
          });
        }),
        function (item) {
          return item.price || "same plane";
        }
      );
      var rooms = audit.rooms || {};
      paintBoard("plane-audit-rooms", [
        Object.assign({ name: "Internal audit" }, rooms.internal || {}),
        Object.assign({ name: "Regulator exam" }, rooms.regulator || {}),
        Object.assign({ name: "Archive" }, rooms.archive || {})
      ], function (item) {
        return item.role || item.what || "keep";
      });
      var regulated = audit.regulated || {};
      if (regulated.lede) set("plane-regulated-lede", regulated.lede);
      paintBoard("plane-rooms12", [regulated.room_1 || {}, regulated.room_2 || {}], function (item) {
        return item.buy === false ? "buy: false" : (item.buy || "");
      });
      fillRows("plane-regulated", regulated.items || [], function (item) {
        return [item.name, item.room === "2" ? "2 refuse" : "1 books", "claimed=" + String(item.claimed === true), item.note || ""];
      });
      fillRows("plane-maps", data.maps || [], function (item) {
        return [item.name, item.maps_to || "", item.scope || "", "claimed=" + String(item.claimed)];
      });
      function card(root, item, extra) {
        var art = document.createElement("article");
        if (item.tone) art.setAttribute("data-tone", item.tone);
        if (extra) extra(art, item);
        var h = document.createElement("h3");
        h.textContent = item.name || item.label || "";
        var p = document.createElement("p");
        p.className = "price";
        p.textContent = item.state || item.price || "";
        var n = document.createElement("p");
        n.className = "note";
        n.textContent = item.note || "";
        art.appendChild(h);
        if (p.textContent) art.appendChild(p);
        art.appendChild(n);
        root.appendChild(art);
        return art;
      }
      var path = document.getElementById("plane-path");
      if (path && data.write_path && data.write_path.length) {
        path.textContent = "";
        data.write_path.forEach(function (item) {
          card(path, item, function (art) {
            art.setAttribute("data-step", item.id || "");
            var note = art.querySelector(".note");
            if (note) note.textContent = item.by + ". " + (item.note || "");
          });
        });
      }
      var lod = document.getElementById("plane-lod");
      if (lod && data.lines_of_defense && data.lines_of_defense.length) {
        lod.textContent = "";
        data.lines_of_defense.forEach(function (item) {
          card(lod, {
            name: item.name,
            state: item.in_force ? "in force" : "not claimed",
            tone: item.in_force ? "ready" : "hold",
            note: item.is + ". " + item.who + ". " + (item.note || "")
          });
        });
      }
      var ledger = document.getElementById("plane-ledger");
      if (ledger && data.ledger) {
        ledger.textContent = "";
        var pending = document.createElement("article");
        pending.innerHTML = "<h3>Pending binds</h3><p class=\"price\">" +
          String(data.ledger.pending_binds || 0) +
          "</p><p class=\"note\">No named treasury pair has a live bind.</p>";
        ledger.appendChild(pending);
        (data.ledger.events || []).forEach(function (item) {
          var art = document.createElement("article");
          art.innerHTML = "<h3>" + item.kind + " · " + item.where + "</h3><p>" +
            item.action + "</p><p class=\"note\">" + item.seats + ". " + (item.note || "") + "</p>";
          ledger.appendChild(art);
        });
      }
      fillRows("plane-coverage", data.coverage || [], function (item) {
        return [item.id, item.sku, item.wedge ? "wedge" : "desk", "live=false", item.note || ""];
      });
      var mech = document.getElementById("plane-mechanics");
      if (mech && data.mechanics && data.mechanics.length) {
        mech.textContent = "";
        data.mechanics.forEach(function (item) {
          var art = document.createElement("article");
          art.innerHTML = "<h3></h3><p></p><p class=\"note\"></p>";
          art.querySelector("h3").textContent = item.name;
          art.querySelector("p").textContent = item.does;
          art.querySelector(".note").textContent = "Does not: " + item.does_not;
          mech.appendChild(art);
        });
      }
      var viewCard = document.getElementById("plane-view-card");
      var viewById = {};
      (data.views || []).forEach(function (item) { viewById[item.id] = item; });
      var clock = document.getElementById("plane-clock");
      if (clock && data.clock) {
        clock.textContent =
          "As of " +
          data.clock.as_of +
          " " +
          data.clock.release +
          " · last event " +
          data.clock.last_event +
          " · pending " +
          data.clock.pending_binds +
          " · frozen " +
          String(data.clock.frozen) +
          " · live clock claimed=" +
          String(data.clock.live_clock_claimed);
      }
      function paintBoard(rootId, items, price) {
        var root = document.getElementById(rootId);
        if (!root || !items || !items.length) return;
        root.textContent = "";
        items.forEach(function (item) {
          var art = document.createElement("article");
          art.setAttribute("data-tone", item.tone || "hold");
          var h = document.createElement("h3");
          h.textContent = item.label || item.name || "";
          var p = document.createElement("p");
          p.className = "price";
          p.textContent = price ? price(item) : String(item.value || item.result || "");
          var n = document.createElement("p");
          n.className = "note";
          n.textContent = item.note || item.when || "";
          art.appendChild(h);
          art.appendChild(p);
          art.appendChild(n);
          root.appendChild(art);
        });
      }
      paintBoard("plane-attention", data.attention || []);
      paintBoard("plane-exceptions", data.exceptions || [], function (item) {
        return item.result || "";
      });
      paintBoard("plane-authorizations", data.authorizations || [], function (item) {
        return item.grants || "";
      });
      paintBoard("plane-revocations", data.revocations || [], function (item) {
        return item.effect || "";
      });
      paintBoard("plane-comms", data.communications || [], function (item) {
        return item.kind || "notify";
      });
      paintBoard("plane-records", data.records || [], function (item) {
        return item.state || "";
      });
      var provision = document.getElementById("plane-provision");
      if (provision && data.provisioning && data.provisioning.path) {
        provision.textContent = "";
        data.provisioning.path.forEach(function (item) {
          card(provision, { name: item.name, state: item.state, tone: "hold", note: item.note || "" });
        });
      }
      var scopes = document.getElementById("plane-scopes");
      if (scopes && data.floor && data.floor.scopes) {
        scopes.textContent = "";
        data.floor.scopes.forEach(function (item) {
          card(
            scopes,
            {
              name: item.name,
              state: item.value,
              tone: item.id === "advanced" ? "list" : "ready",
              note: item.note || ""
            },
            function (art) {
              art.setAttribute("data-scope", item.id || "");
            }
          );
        });
      }
      var bands = document.getElementById("plane-bands");
      if (bands && data.provision_bands && data.provision_bands.items) {
        bands.textContent = "";
        data.provision_bands.items.forEach(function (item) {
          var upsell = item.upsell === true;
          card(
            bands,
            {
              name: item.name,
              state: upsell ? "upsell band" : "included with L1",
              tone: upsell ? "list" : "ready",
              note: item.note || ""
            },
            function (art) {
              art.setAttribute("data-band", upsell ? "advanced" : "standard");
            }
          );
        });
      }
      var deskRoot = document.getElementById("plane-desks");
      if (deskRoot && data.provision_bands) {
        deskRoot.textContent = "";
        function deskGroup(label) {
          var tr = document.createElement("tr");
          tr.setAttribute("data-group", "true");
          var th = document.createElement("th");
          th.colSpan = 5;
          th.textContent = label;
          tr.appendChild(th);
          deskRoot.appendChild(tr);
        }
        function deskRows(list, kind) {
          (list || []).forEach(function (item) {
            if (kind && item.kind && item.kind !== kind) return;
            var tr = document.createElement("tr");
            [item.name, item.band || "", item.sku || "", item.attach || "", item.note || ""].forEach(function (value) {
              tr.appendChild(cell(value));
            });
            deskRoot.appendChild(tr);
          });
        }
        deskGroup("Standard — included with L1");
        deskRows(data.provision_bands.included_l1, "desk");
        deskGroup("Advanced — priced attach");
        deskRows(data.provision_bands.priced_l1, "desk");
        deskRows(data.provision_bands.priced_padm, "desk");
        deskRows(data.provision_bands.priced_udual, "desk");
        deskGroup("Advanced — included with P-ADM (not free)");
        deskRows(data.provision_bands.included_padm);
        deskGroup("Advanced — included with paid U-DUAL (not free)");
        deskRows(data.provision_bands.included_udual);
        deskGroup("Hours");
        (data.provision_bands.included_hours || []).forEach(function (item) {
          var tr = document.createElement("tr");
          [item.name, "standard", "hours", "included with L1", item.note || ""].forEach(function (value) {
            tr.appendChild(cell(value));
          });
          deskRoot.appendChild(tr);
        });
        (data.provision_bands.priced_hours || []).forEach(function (item) {
          var rate = item.rate ? ("$" + Number(item.rate).toLocaleString() + "/day") : "priced";
          var tr = document.createElement("tr");
          [item.name, "advanced · priced", "hours", rate, item.note || ""].forEach(function (value) {
            tr.appendChild(cell(value));
          });
          deskRoot.appendChild(tr);
        });
        deskGroup("Libraries — same modules, not extra SKUs");
        deskRows(data.provision_bands.included_l1, "library");
        deskRows(data.provision_bands.priced_l1, "library");
        deskRows(data.provision_bands.priced_padm, "library");
        deskRows(data.provision_bands.priced_udual, "library");
      }
      if (data.zero_trust) {
        set("plane-zero-trust", data.zero_trust.does + " Does not: " + data.zero_trust.does_not);
        fill("plane-never-trust", data.zero_trust.never_trust || [], function (item) {
          return "Never trust: " + item + ". Identify is not admit.";
        });
      }
      fillRows("plane-matrix", data.compliance_matrix || [], function (item) {
        return [item.name, item.record || "map_only", "claimed=false", item.maps_to || ""];
      });
      fillRows("plane-duties", data.duties || [], function (item) {
        return [
          item.name,
          flag(item.admit),
          flag(item.freeze),
          flag(item.keep),
          flag(item.draft),
          flag(item.host),
          flag(item.counsel)
        ];
      }, function (item) {
        return item.role || "";
      });
      var dutyBody = document.getElementById("plane-duties");
      if (dutyBody) {
        Array.prototype.forEach.call(dutyBody.querySelectorAll("tr"), function (tr) {
          var admit = tr.children[1];
          if (admit && admit.textContent === "yes") tr.setAttribute("data-admit", "yes");
        });
      }
      var inspector = document.getElementById("plane-inspector");
      function paintInspector(kind) {
        if (!inspector) return;
        inspector.textContent = "";
        function add(title, value, note) {
          var art = document.createElement("article");
          var h = document.createElement("h3");
          h.textContent = title;
          var p = document.createElement("p");
          p.className = "price";
          p.textContent = value;
          var n = document.createElement("p");
          n.className = "note";
          n.textContent = note || "";
          art.appendChild(h);
          art.appendChild(p);
          if (note) art.appendChild(n);
          inspector.appendChild(art);
        }
        var event = (data.ledger && data.ledger.events && data.ledger.events[0]) || {};
        if (kind === "inspector" || kind === "attention") {
          var must = (data.floor && data.floor.must_have) || data.must_have || {};
          var page = (data.floor && data.floor.page) || {};
          add("The sale", "ninety-minute proof", page.sale || "The sale is the ninety-minute proof.");
          add("The twin", "the admit plane", page.twin_is || "Microsoft is identity, notify, SoR, and audit sink. The product is the admit plane.");
          var acc = (data.floor && data.floor.accountable) || {};
          add("Who may", "admit · freeze · keep", acc.lede || "The duty matrix is who may admit, freeze, keep, draft, host, or counsel. Only seat A and seat B admit.");
          var protAttn = (data.floor && data.floor.protect) || {};
          add("Disclaimer", "not a certificate", protAttn.lede || "Governance is a catalog map. It is not counsel, not a filing, and not a certificate.");
          (protAttn.items || []).forEach(function (item) {
            if (item.id === "attest" || item.id === "policy" || item.id === "update") {
              add(item.name, item.id, item.note || "");
            }
          });
          var memAttn = (data.floor && data.floor.memory) || {};
          add("Memory", "two records and a keep", memAttn.lede || "Record keeping is two records and a keep.");
          (memAttn.items || []).forEach(function (item) {
            add(item.name, item.id, item.note || "");
          });
          var intAttn = (data.floor && data.floor.integrate) || {};
          add("Integrate", "owner clicks", intAttn.lede || "This Cloud Agent cannot create users, grant Graph roles, publish the Institute, or mark LIVE_PIN_OK.");
          (intAttn.items || []).forEach(function (item) {
            add(item.url_label || item.name, item.id, item.note || "");
          });
          add("Must-have", "one plane over every new client AI", must.why || "Every new client AI is another unauthorized-write surface unless one human plane sits over all of them.");
          add("First record", "1 sandbox / 0 production", event.note || "AINAV-L1 lab operator identities.");
          add("Action", event.action || "bc.general_journal.post", (event.where || "sandbox") + ". " + (event.seats || "lab operator identities"));
          add("Second record", "0", "P-ADM keep not attached. Examiner cannot certify.");
          add("Pending binds", String((data.ledger && data.ledger.pending_binds) || 0), "No named treasury pair has a live bind.");
        }
        if (kind === "freeze") {
          add("Off switch", "READY", "Fail-closed. Does not power down Copilot.");
          add("Catalog plane", "OPEN", "A console freeze is local rehearsal. It does not mark LIVE_PIN_OK.");
          add("Signed L1", "0", "Counsel pack G13 stays open. Owner is not both seats.");
          add("Seats recorded", "1 mailbox / 0 oid", (data.invited || "Cynthia Hodnett") + " mailbox recorded. Mailbox is not an Entra oid and not a click.");
        }
        if (kind === "access") {
          add("Internal", "Same Entra object id", (data.access && data.access.internal) || "");
          add("Remote", "Same plane", (data.access && data.access.remote) || "");
          add("VPN SKU", "false", "Remote is not a second control plane.");
          add("Conditional Access", "may identify", "It does not admit the write.");
        }
        if (kind === "host") {
          add("IT role", "host", "Copilot, Agent 365, and BYO MCP stay hosted. They are not seats.");
          add("PIM", "not dual", "An eligible activation is not an admit.");
          add("Teams", "not a seat", "A chat is not dual admit.");
          add("Agent Tools", "not the plane", "A tool invocation is not dual admit.");
        }
        if (kind === "provision") {
          var attached = (data.provisioning && data.provisioning.attached) || {};
          var scopes = (data.floor && data.floor.scopes) || [];
          scopes.forEach(function (item) {
            add(item.name, item.value, item.note || "");
          });
          add("Attached SKUs", String(attached.L1 || 0) + " / " + String(attached["P-ADM"] || 0) + " / " + String(attached["U-DUAL"] || 0), "L1 / P-ADM / U-DUAL. Not LIVE_PIN_OK.");
          var intProv = (data.floor && data.floor.integrate) || {};
          add("Integrate", "owner clicks", intProv.lede || "This Cloud Agent cannot create users, grant Graph roles, publish the Institute, or mark LIVE_PIN_OK.");
          (intProv.items || []).forEach(function (item) {
            add(item.url_label || item.name, item.id, item.note || "");
          });
        }
        if (kind === "client") {
          var mustHave = (data.floor && data.floor.must_have) || data.must_have || {};
          var audience = mustHave.for || {};
          add("Must-have", "one human plane", mustHave.why || "Every new client AI is another unauthorized-write surface unless one human plane sits over all of them.");
          add("The write that must not happen", "unauthorized journal", mustHave.incident || "The unauthorized general-journal post the client's AI or the client's customer AI drafted and two humans did not admit.");
          add("Already have", "BC · Entra · SOD", (data.floor && data.floor.already_have) || "Controllers already have Business Central Premium, Entra, and two-person journal SOD.");
          add("Still lack", "the gate", (data.floor && data.floor.still_lack) || "They do not have a gate in front of the write.");
          var page = (data.floor && data.floor.page) || {};
          add("The sale", "ninety-minute proof", page.sale || "The sale is the ninety-minute proof.");
          add("The twin", "the admit plane", page.twin_is || "Microsoft is identity, notify, SoR, and audit sink. The product is the admit plane.");
          var acc = (data.floor && data.floor.accountable) || {};
          add("Who may", "admit · freeze · keep", acc.lede || "The duty matrix is who may admit, freeze, keep, draft, host, or counsel. Only seat A and seat B admit.");
          (acc.items || []).forEach(function (item) {
            add(item.name, item.id, item.note || "");
          });
          var prot = (data.floor && data.floor.protect) || {};
          add("Disclaimer", "not a certificate", prot.lede || "Governance is a catalog map. It is not counsel, not a filing, and not a certificate.");
          (prot.items || []).forEach(function (item) {
            add(item.name, item.id, item.note || "");
          });
          var mem = (data.floor && data.floor.memory) || {};
          add("Memory", "two records and a keep", mem.lede || "Record keeping is two records and a keep.");
          (mem.items || []).forEach(function (item) {
            add(item.name, item.id, item.note || "");
          });
          var integ = (data.floor && data.floor.integrate) || {};
          add("Integrate", "owner clicks", integ.lede || "This Cloud Agent cannot create users, grant Graph roles, publish the Institute, or mark LIVE_PIN_OK.");
          (integ.items || []).forEach(function (item) {
            add(item.url_label || item.name, item.id, item.note || "");
          });
          add("Owner", "must-have", audience.owner || "Cannot let any AI post a journal without two seats.");
          add("Board", "must-have", audience.board || "Inventory of models is not a control.");
          add("Examiner", "must-have", audience.examiner || "First record is the SoR write. Second record is who admitted it.");
          add("Not the gate", "BC · Teams · PIM · Copilot", "A vendor-native button only covers that vendor. A Teams vote is not dual admit. PIM is not dual admit.");
          var close = (data.floor && data.floor.proof_close) || {};
          add("Walk out", (close.minutes || 90) + " minutes", (close.walk_out || ["sealed DecisionRecord", "Merkle / audit export"]).join(". "));
          var noMeans = (data.floor && data.floor.no_means) || {};
          add("What no does", "fail-closed", noMeans.fail_closed || "If either person is missing, the write does not land.");
          add("Off switch", "READY", noMeans.off_switch || "Humans freeze new grants. Inference may continue. Consequence does not.");
          add("This dashboard", "included with L1", "The same plane, tiled. Not a second product. Not Standard vs Advanced dashboard.");
          add("Week-one prove", "treasury + wedge", "What we provision first. Not the whole standard band.");
          add("Advanced upsell", "not a SKU", "Priced desks, P-ADM, paid U-DUAL, hours. U-DUAL is never free.");
          add("Attached", "0 / 0 / 0", "Year-one if all three is catalog list. Not a forecast. Mandated: false.");
        }
        if (kind === "records") {
          var memRec = (data.floor && data.floor.memory) || {};
          add("Memory", "two records and a keep", memRec.lede || "Record keeping is two records and a keep.");
          (memRec.items || []).forEach(function (item) {
            add(item.name, item.id, item.note || "");
          });
          add("First record", "1 sandbox / 0 production", "AINAV-L1 lab operator identities.");
          add("Second record", "0", "P-ADM keep not attached. Not a filing.");
          add("Weekly keep", "none", "After kit PASS. A chat is not the keep.");
          add("Retention", "claimed=false", "Books-and-records and COSO maps. Not a 17a-4 opinion.");
        }
      }
      var rehearsal = {
        step: "idle",
        frozen: false,
        hash: "",
        consumed: false
      };
      var railIds = ["draft", "bind", "seat_a", "seat_b", "first_record", "second_record", "keep"];
      var rail = document.getElementById("plane-rehearsal-rail");
      var actions = document.getElementById("plane-rehearsal-actions");
      var tape = document.getElementById("plane-tape");
      var rehearsalRoot = document.getElementById("plane-rehearsal");
      function writeTape(state, text) {
        if (!tape) return;
        tape.dataset.state = state;
        tape.textContent = text;
      }
      function paintRail() {
        if (!rail) return;
        rail.textContent = "";
        var reached = railIds.indexOf(rehearsal.step);
        railIds.forEach(function (id, index) {
          var span = document.createElement("span");
          span.setAttribute("data-step", id);
          span.setAttribute("data-active", rehearsal.step === id ? "true" : "false");
          span.setAttribute("data-done", reached > index ? "true" : "false");
          var found = (data.write_path || []).filter(function (item) { return item.id === id; })[0];
          span.textContent = found ? found.name : id.replace("_", " ");
          rail.appendChild(span);
        });
      }
      function rehearsalLabel() {
        var spec = data.rehearsal || {};
        return (
          (spec.label || "Sandbox rehearsal.") +
          "\nwedge=" +
          (spec.wedge || "bc.general_journal.post") +
          "\nwrites_sor=false · production=false · named_humans=false"
        );
      }
      function resetRehearsal(reason) {
        rehearsal.step = "idle";
        rehearsal.frozen = false;
        rehearsal.hash = "";
        rehearsal.consumed = false;
        paintRail();
        writeTape(
          "idle",
          (reason ? reason + "\n" : "") +
            "rehearsal_idle\n" +
            rehearsalLabel() +
            "\nMicrosoft was not called. Catalog plane stays OPEN."
        );
      }
      function deny(code, detail) {
        writeTape(
          "denied",
          code +
            "\n" +
            detail +
            "\n" +
            rehearsalLabel() +
            "\nlive=false · live_pin_ok=false · Microsoft was not called."
        );
      }
      function bindHash() {
        return actionHash({
          action_class: (data.rehearsal && data.rehearsal.wedge) || "bc.general_journal.post",
          payload: { document: "AINAV-L1", company: "AINav", rehearsal: true },
          sor_target: "bc.sandbox",
          live: false
        });
      }
      function runRehearsal(kind) {
        if (kind === "reset") {
          resetRehearsal("rehearsal_reset");
          return;
        }
        if (kind === "freeze") {
          rehearsal.frozen = true;
          deny("fail_closed · freeze", "Owner/board requested the off switch in this browser. New grants stop. Catalog plane stays OPEN. Inference may continue. Consequence does not.");
          return;
        }
        if (rehearsal.frozen && kind !== "reset") {
          deny("fail_closed · frozen", "Console is frozen in rehearsal. Reset the rehearsal. Catalog plane stays OPEN.");
          return;
        }
        if (kind === "same_seat") {
          deny("admit_denied · same_seat", "One title cannot click both admits. One Entra object id cannot be both seats.");
          return;
        }
        if (kind === "agent") {
          deny("admit_denied · agent_click", "Cloud Agent / client AI may draft. It cannot bind an action_hash.");
          return;
        }
        if (kind === "pim") {
          deny("admit_denied · entra.pim", "PIM is not dual admit. Eligible seats stay eligible.");
          return;
        }
        if (kind === "copilot") {
          deny("admit_denied · microsoft.copilot", "Copilot, Agent 365, and Agent Tools are not the admit plane.");
          return;
        }
        if (kind === "refuse") {
          rehearsal.step = "idle";
          rehearsal.hash = "";
          rehearsal.consumed = false;
          paintRail();
          deny("write_held · seat_refuse", "Seat A or seat B refused. No grant. No SoR write.");
          return;
        }
        if (kind === "draft") {
          rehearsal.step = "draft";
          paintRail();
          writeTape("ok", "draft_ok · department AI / payables / sales\nNot a seat. Waiting for a bind.\n" + rehearsalLabel());
          return;
        }
        if (kind === "bind") {
          if (rehearsal.step !== "draft" && rehearsal.step !== "idle") {
            deny("bind_held", "Reset the rehearsal to bind a new action_hash.");
            return;
          }
          bindHash().then(function (hash) {
            rehearsal.hash = hash;
            rehearsal.step = "bind";
            rehearsal.consumed = false;
            paintRail();
            writeTape(
              "ok",
              "bind_ok · action_hash=" +
                hash +
                "\nPending dual admit. Catalog pending binds stay 0.\n" +
                rehearsalLabel()
            );
          });
          return;
        }
        if (kind === "seat_a") {
          if (rehearsal.step !== "bind") {
            deny("admit_held · seat_a", "Bind an action_hash first.");
            return;
          }
          rehearsal.step = "seat_a";
          paintRail();
          writeTape("ok", "admit_ok · seat_a=lab operator identity A\nWaiting for seat B. Named humans=false.\n" + rehearsalLabel());
          return;
        }
        if (kind === "seat_b") {
          if (rehearsal.step !== "seat_a") {
            deny("admit_held · seat_b", "Seat A must admit first. One title cannot be both seats.");
            return;
          }
          if (rehearsal.consumed) {
            deny("effect_blocked · replay", "Single-use consume. No second write.");
            return;
          }
          rehearsal.step = "first_record";
          rehearsal.consumed = true;
          paintRail();
          writeTape(
            "ok",
            "rehearsal_preview · first_record sandbox\naction_class=bc.general_journal.post\naction_hash=" +
              rehearsal.hash +
              "\ndocument=AINAV-L1 · company=AINav\nThis does not create a new SoR write. The catalog first record stays 1 sandbox / 0 production.\nsecond_record=held · keep=held · P-ADM not attached.\nMicrosoft Business Central Production was not called.\n" +
              rehearsalLabel()
          );
          return;
        }
      }
      if (actions && !actions.dataset.bound) {
        actions.dataset.bound = "true";
        [
          ["draft", "Draft wedge", ""],
          ["bind", "Bind action_hash", "ask"],
          ["seat_a", "Seat A admit", ""],
          ["seat_b", "Seat B admit", ""],
          ["refuse", "Refuse", "deny"],
          ["same_seat", "Same seat", "deny"],
          ["agent", "Agent click", "deny"],
          ["pim", "PIM as dual", "deny"],
          ["copilot", "Copilot as plane", "deny"],
          ["freeze", "Request freeze", "deny"],
          ["reset", "Reset rehearsal", ""]
        ].forEach(function (row) {
          var btn = document.createElement("button");
          btn.type = "button";
          btn.textContent = row[1];
          btn.setAttribute("data-rehearse", row[0]);
          if (row[2]) btn.className = row[2];
          btn.addEventListener("click", function () {
            runRehearsal(row[0]);
          });
          actions.appendChild(btn);
        });
        paintRail();
      }
      var consoleRoot = document.getElementById("plane-console");
      var consoleKicker = document.getElementById("plane-console-kicker");
      var consoleTitle = document.getElementById("plane-console-title");
      var consoleNote = document.getElementById("plane-console-note");
      var attention = document.getElementById("plane-attention");
      function showView(id) {
        var item = viewById[id] || viewById.entire;
        var consoleKind = (item && item.console) || "attention";
        document.body.setAttribute("data-view", id);
        document.querySelectorAll("[data-view-tab]").forEach(function (btn) {
          btn.setAttribute("aria-selected", btn.getAttribute("data-view-tab") === id ? "true" : "false");
        });
        if (viewCard && item) {
          viewCard.querySelector("h3").textContent = item.name;
          viewCard.querySelector("p").textContent =
            item.who + ". Can: " + (item.can || "") + " Cannot: " + (item.cannot || "");
        }
        if (consoleRoot) consoleRoot.setAttribute("data-console", consoleKind);
        if (consoleKicker) consoleKicker.textContent = "Command console · " + ((item && item.name) || id);
        var titles = {
          attention: "Attention board",
          freeze: "Owner deck — freeze and the off switch",
          rehearsal: "Seat deck — walkable rehearsal",
          inspector: "Examiner deck — bind inspector",
          access: "Remote deck — same Entra plane",
          host: "IT deck — host, not a seat",
          provision: "Provision deck — standard included, advanced upsell",
          records: "Records deck — first, second, keep",
          client: "Client deck — already have SOD, still lack the gate"
        };
        if (consoleTitle) consoleTitle.textContent = titles[consoleKind] || "Command console";
        if (consoleNote) {
          consoleNote.textContent =
            consoleKind === "rehearsal"
              ? ((data.rehearsal && data.rehearsal.label) || "Sandbox rehearsal.") + " Completing it does not create a new SoR write."
              : (item && item.can
                ? item.can + (item.cannot ? " Cannot: " + item.cannot : "")
                : "");
        }
        if (attention) attention.hidden = consoleKind !== "attention";
        if (rehearsalRoot) rehearsalRoot.hidden = consoleKind !== "rehearsal";
        paintInspector(consoleKind);
      }
      document.querySelectorAll("[data-view-tab]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          showView(btn.getAttribute("data-view-tab"));
        });
      });
      showView(document.body.getAttribute("data-view") || "entire");
      fill("plane-refuse", data.refuse || [], function (item) {
        return item;
      });
      if (data.access) {
        var grid = document.getElementById("plane-access-grid");
        if (grid) {
          grid.textContent = "";
          [
            ["Internal", data.access.internal],
            ["Remote", data.access.remote]
          ].forEach(function (pair) {
            var art = document.createElement("article");
            art.className = "plane-panel";
            var h = document.createElement("h3");
            h.textContent = pair[0];
            var p = document.createElement("p");
            p.textContent = pair[1];
            art.appendChild(h);
            art.appendChild(p);
            grid.appendChild(art);
          });
        }
        fill("plane-access-rules", [
          "Same plane: " + String(data.access.same_plane) + ". Second remote plane: " + String(data.access.second_remote_plane) + ". VPN SKU: " + String(data.access.vpn_sku) + ".",
          "Entra required. PIM is not dual. Teams is not a seat."
        ], function (item) {
          return item;
        });
      }
    })
    .catch(function () {
      /* control-plane.json is optional when opened as a file */
    });

  fetch("investor.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data || data.live || data.live_pin_ok || data.sku || data.priced_round || data.raise_claimed) return;
      var thesis = document.getElementById("investor-thesis");
      if (thesis && data.one_liner) thesis.textContent = data.one_liner;
      var equation = document.getElementById("investor-equation");
      if (equation && data.equation) equation.textContent = "Packet = " + data.equation;
      function set(id, text) {
        var node = document.getElementById(id);
        if (node && text) node.textContent = text;
      }
      set("investor-open", data.letter_open);
      set("investor-letter-close", data.letter_close);
      var letterBody = document.getElementById("investor-letter-body");
      if (letterBody && data.letter_body) {
        letterBody.textContent = "";
        String(data.letter_body).split(/\n\n+/).forEach(function (chunk) {
          if (!chunk.trim()) return;
          var p = document.createElement("p");
          p.textContent = chunk.trim();
          letterBody.appendChild(p);
        });
      }
      if (data.executive_summary) {
        set("investor-exec-lede", data.executive_summary.lede);
        var exec = document.getElementById("investor-exec");
        if (exec && data.executive_summary.items && data.executive_summary.items.length) {
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
        } else {
          set("investor-exec-job", data.executive_summary.job_c);
          set("investor-exec-proof", data.executive_summary.proof);
          set("investor-exec-skus", data.executive_summary.skus);
          set("investor-exec-tiles", data.executive_summary.tiles);
          set("investor-exec-microsoft", data.executive_summary.microsoft);
          set("investor-exec-must", data.executive_summary.must_have);
          set("investor-exec-opens", data.executive_summary.opens);
          set("investor-exec-ask", data.executive_summary.ask);
        }
      }
      set("investor-tuesday", data.tuesday);
      set("investor-problem", data.problem);
      set("investor-solution", data.solution);
      set("investor-model", data.model);
      set("investor-ask", data.ask);
      set("investor-seat", data.seat_b);
      set("investor-stack", data.stack);
      set("investor-plane", data.control_plane);
      if (data.kpis) {
        set("investor-rev", "$" + (data.kpis.recognized_revenue || 0));
        set("investor-cust", String(data.kpis.named_customers || 0));
        set("investor-l1", String(data.kpis.signed_l1 || 0));
      }
      if (data.upsell_note) set("investor-upsell", data.upsell_note);
      var desks = document.getElementById("investor-desks");
      if (desks && data.industry && data.industry.length) {
        desks.textContent = "";
        data.industry.forEach(function (item) {
          var li = document.createElement("li");
          var price = item.included
            ? "included with " + item.requires_sku
            : "$" + item.min.toLocaleString() + "–$" + item.max.toLocaleString();
          li.textContent = item.id + " — " + price + ". Not a SKU.";
          desks.appendChild(li);
        });
      }
      var ffs = document.getElementById("investor-ffs");
      if (ffs && data.fee_for_service && data.fee_for_service.length) {
        ffs.textContent = "";
        data.fee_for_service.forEach(function (item) {
          var li = document.createElement("li");
          var rate = item.billable
            ? "$" + Number(item.rate_usd_per_day || 0).toLocaleString() + "/day"
            : "inside L1";
          li.textContent = item.id + " — " + rate + ". Not a SKU.";
          ffs.appendChild(li);
        });
      }
      if (data.year_one_if_all_three) {
        set(
          "investor-year",
          "$" +
            Math.round(data.year_one_if_all_three.min / 1000) +
            "–" +
            Math.round(data.year_one_if_all_three.max / 1000) +
            "k list"
        );
      }
    })
    .catch(function () {
      /* investor.json is optional when opened as a file */
    });

  fetch("ip.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data || data.live || data.live_pin_ok || data.sku || data.patent_claimed || data.uncopyable) return;
      var thesis = document.getElementById("ip-thesis");
      if (thesis && data.thesis) thesis.textContent = data.thesis;
      var equation = document.getElementById("ip-equation");
      if (equation && data.equation) equation.textContent = "Insulation = " + data.equation;
      var why = document.getElementById("ip-why");
      if (why && data.why_microsoft_is_not_the_failsafe) why.textContent = data.why_microsoft_is_not_the_failsafe;
      var ultimate = document.getElementById("ip-ultimate");
      if (ultimate && data.why_ultimate_plane) ultimate.textContent = data.why_ultimate_plane;
      var others = document.getElementById("ip-others");
      if (others && data.others && data.others.length) {
        others.textContent = "Same conflict for " + data.others.join(", ") + ".";
      }
      function fill(id, items, line) {
        var root = document.getElementById(id);
        if (!root || !items || !items.length) return;
        root.textContent = "";
        items.forEach(function (item) {
          var li = document.createElement("li");
          li.textContent = line(item);
          root.appendChild(li);
        });
      }
      fill("ip-pins", data.what_the_build_pins || [], function (item) {
        return item;
      });
      fill("ip-layers", data.layers || [], function (item) {
        return item.id + " — " + item.does;
      });
      fill("ip-copy", data.what_they_can_copy || [], function (item) {
        return item;
      });
      fill("ip-refuse", data.refuse || [], function (item) {
        return item;
      });
    })
    .catch(function () {
      /* ip.json is optional when opened as a file */
    });

  fetch("client-org.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data || data.live || data.live_pin_ok || data.sku || data.replaces_org_chart) return;
      var thesis = document.getElementById("client-org-thesis");
      if (thesis && data.thesis) thesis.textContent = data.thesis;
      var seats = document.getElementById("client-org-seats");
      if (seats && data.seats && data.seats.seat_a && data.seats.seat_b) {
        seats.textContent =
          "Seat A: " +
          data.seats.seat_a.role +
          " (usually " +
          data.seats.seat_a.usually +
          "). Seat B: " +
          data.seats.seat_b.role +
          " (usually " +
          data.seats.seat_b.usually +
          "). One title cannot be both seats. Invented heads: refused.";
      }
      var root = document.getElementById("client-org-depts");
      if (root && data.departments && data.departments.length) {
        root.textContent = "";
        data.departments.forEach(function (item) {
          var li = document.createElement("li");
          li.setAttribute("data-id", item.id);
          li.textContent =
            item.name +
            " — " +
            item.role +
            ". Department AI is a seat: false. " +
            (item.note || "");
          root.appendChild(li);
        });
      }
    })
    .catch(function () {
      /* client-org.json is optional when opened as a file */
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
      var upgrades = document.getElementById("review-upgrades");
      if (upgrades && data.expert_review && data.expert_review.upgrades) {
        upgrades.textContent = "";
        data.expert_review.upgrades.forEach(function (item) {
          var li = document.createElement("li");
          var who = item.who || "";
          var done = item.done ? "done" : "open";
          li.textContent =
            item.n +
            ". [" +
            who +
            " · " +
            done +
            "] " +
            (item.title || "") +
            " — " +
            (item.do || "");
          upgrades.appendChild(li);
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
      var invited = (data.contacts && data.contacts.invited) || {};
      var orgLede = document.getElementById("org-lede");
      if (orgLede && invited.name) {
        var mailbox = invited.email || "mailbox not recorded";
        orgLede.textContent =
          "Sole owner James Hodnett. The Cloud Agent operates. It is not a dual seat " +
          "and not an Inception contact. " +
          invited.name +
          (invited.agreed ? " agreed. " : " is invited. ") +
          "Mailbox " +
          mailbox +
          (invited.recorded ? " recorded. " : " not recorded. ") +
          "Entra oid and click still open.";
      }
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

  function paintStackWalk(walk) {
    if (!walk) return;
    function set(id, text) {
      var node = document.getElementById(id);
      if (node && text) node.textContent = text;
    }
    set("stack-walk-thesis", walk.thesis);
    set("stack-walk-impl", walk.implementation);
    if (walk.cannot && walk.cannot.length) {
      set(
        "stack-walk-cannot",
        "This Cloud Agent cannot " + walk.cannot.join(", ") + "."
      );
    }
    function paintHops(rootId, items) {
      var root = document.getElementById(rootId);
      if (!root || !items || !items.length) return;
      root.textContent = "";
      items.forEach(function (item) {
        var li = document.createElement("li");
        var url = String(item.url || "");
        var label = item.url_label || item.name || "";
        var body =
          (item.status ? item.status + ". " : "") +
          (item.in_tree || item.owner || "");
        if (url.indexOf("https://") === 0 && url.indexOf("2ad041b8") === -1) {
          var a = document.createElement("a");
          a.setAttribute("href", url);
          a.textContent = label;
          li.appendChild(a);
          li.appendChild(document.createTextNode(body ? " — " + body : ""));
        } else {
          li.textContent = label + (body ? " — " + body : "");
        }
        root.appendChild(li);
      });
    }
    paintHops("stack-walk-path", walk.path);
    paintHops("stack-walk-complements", walk.complements);
  }

  fetch("stack.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data || data.live) return;
      paintCards("stack-cards", data.connections);
      paintCards("complement-cards", data.complements);
      paintStackWalk(data.walk);
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

  var lastBuyer = null;

  function fillBuyer(data) {
    if (!data) return;
    lastBuyer = data;
    var write = document.getElementById("buyer-write");
    var incident = document.getElementById("buyer-incident");
    var proof = document.getElementById("buyer-proof");
    var door = document.getElementById("buyer-door");
    if (write && data.write_that_must_not_happen) write.textContent = data.write_that_must_not_happen;
    if (incident && data.incident) incident.textContent = data.incident;
    if (proof && data.proof_day) proof.textContent = data.proof_day;
    if (door && data.door) door.textContent = data.door;
    var already = document.getElementById("buyer-already");
    if (already && (data.already_have || data.still_lack)) {
      already.textContent =
        (data.already_have || "") +
        " " +
        (data.still_lack || "") +
        " A Teams vote, a PIM activation, or Copilot asking a human is not dual admit.";
    }
    var walk = document.getElementById("buyer-walk");
    if (walk && data.proof_close) {
      walk.textContent =
        "Walk in: " +
        (data.proof_close.walk_in || "two existing treasury seats") +
        " Walk out: " +
        ((data.proof_close.walk_out || []).join(" and ") || "sealed DecisionRecord") +
        ". " +
        ((data.no_means && data.no_means.fail_closed) || "If either person is missing, the write does not land.");
    }
    var sale = document.getElementById("buyer-sale");
    if (sale && (data.sale || (data.proof_close && data.proof_close.sale))) {
      sale.textContent = data.sale || data.proof_close.sale;
    }
    if (data.accountable && data.accountable.lede) {
      var duty = document.getElementById("buyer-duty");
      if (duty) duty.textContent = data.accountable.lede;
    }
    if (data.accountable && data.accountable.items) {
      var acc = document.getElementById("accountable");
      if (acc) {
        acc.textContent = "";
        data.accountable.items.forEach(function (item) {
          var art = document.createElement("article");
          var h = document.createElement("h3");
          h.textContent = item.name || "";
          var p = document.createElement("p");
          p.textContent = item.note || "";
          art.appendChild(h);
          art.appendChild(p);
          acc.appendChild(art);
        });
      }
    }
    if (data.protect && data.protect.lede) {
      var protLede = document.getElementById("buyer-protect-lede");
      if (protLede) protLede.textContent = data.protect.lede;
    }
    if (data.protect && data.protect.items) {
      var prot = document.getElementById("protect");
      if (prot) {
        prot.textContent = "";
        data.protect.items.forEach(function (item) {
          var art = document.createElement("article");
          var h = document.createElement("h3");
          h.textContent = item.name || "";
          var p = document.createElement("p");
          p.textContent = item.note || "";
          art.appendChild(h);
          art.appendChild(p);
          prot.appendChild(art);
        });
      }
    }
    if (data.memory && data.memory.lede) {
      var memLede = document.getElementById("buyer-memory-lede");
      if (memLede) memLede.textContent = data.memory.lede;
    }
    if (data.memory && data.memory.items) {
      var memBand = document.getElementById("memory");
      if (memBand) {
        memBand.textContent = "";
        data.memory.items.forEach(function (item) {
          var art = document.createElement("article");
          var h = document.createElement("h3");
          h.textContent = item.name || "";
          var p = document.createElement("p");
          p.textContent = item.note || "";
          art.appendChild(h);
          art.appendChild(p);
          memBand.appendChild(art);
        });
      }
    }
    if (data.integrate && data.integrate.lede) {
      var intLede = document.getElementById("buyer-integrate-lede");
      if (intLede) intLede.textContent = data.integrate.lede;
    }
    if (data.integrate && data.integrate.items) {
      paintIntegrate("integrate", data.integrate);
    }
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
    paintSuccess(data.success);
    paintPublicFace(data);
  }

  function paintNamedCards(rootId, items, titleKey, noteKey) {
    var root = document.getElementById(rootId);
    if (!root || !items || !items.length) return;
    root.textContent = "";
    items.forEach(function (item) {
      var art = document.createElement("article");
      if (item.id) art.setAttribute("data-id", item.id);
      var h = document.createElement("h3");
      h.textContent = item[titleKey] || item.name || item.hear || "";
      var p = document.createElement("p");
      p.textContent = item[noteKey] || item.note || item.answer || "";
      art.appendChild(h);
      art.appendChild(p);
      root.appendChild(art);
    });
  }

  function paintPublicFace(data) {
    if (!data || data.live || data.live_pin_ok || data.launch) return;
    var glance = data.first_glance || {};
    var lede = document.getElementById("hero-contrast-lede");
    if (lede && glance.lede) lede.textContent = glance.lede;
    var fold = document.getElementById("hero-fold-lede");
    if (fold && (data.already_have || data.still_lack)) {
      fold.textContent = ((data.already_have || "") + " " + (data.still_lack || "")).trim();
    }
    var kicker = document.getElementById("hero-rail-kicker");
    if (kicker && glance.rail_kicker) kicker.textContent = glance.rail_kicker;
    var rail = document.getElementById("hero-write-rail");
    if (rail && glance.write_rail && glance.write_rail.length) {
      rail.textContent = "";
      glance.write_rail.forEach(function (item) {
        var li = document.createElement("li");
        if (item.id) li.setAttribute("data-step", item.id);
        var b = document.createElement("b");
        b.textContent = item.name || "";
        var span = document.createElement("span");
        span.textContent = item.note || "";
        li.appendChild(b);
        li.appendChild(span);
        rail.appendChild(li);
      });
    }
    var contrast = document.getElementById("hero-contrast");
    if (contrast && glance.job_c && data.not_the_gate && data.not_the_gate.length) {
      contrast.textContent = "";
      var pin = document.createElement("article");
      pin.setAttribute("data-pin", "job-c");
      pin.setAttribute("data-lane", "gate");
      var ph = document.createElement("h3");
      ph.textContent = "Job C";
      var pp = document.createElement("p");
      pp.textContent = glance.job_c;
      pin.appendChild(ph);
      pin.appendChild(pp);
      contrast.appendChild(pin);
      data.not_the_gate.forEach(function (item) {
        var art = document.createElement("article");
        art.setAttribute("data-lane", "copy");
        var h = document.createElement("h3");
        h.textContent = item.name || "";
        var p = document.createElement("p");
        p.textContent = item.note || "";
        art.appendChild(h);
        art.appendChild(p);
        contrast.appendChild(art);
      });
    }
    var skus = document.getElementById("hero-skus");
    if (skus && data.skus && data.skus.length === 3) {
      skus.textContent = "";
      data.skus.forEach(function (item) {
        if (!item || !item.id) return;
        var li = document.createElement("li");
        li.setAttribute("data-sku", item.id);
        var b = document.createElement("b");
        b.textContent = item.id;
        var kind = document.createElement("span");
        kind.textContent = item.kind || "";
        var p = document.createElement("p");
        var price = item.price_usd || {};
        var band =
          typeof price.min === "number" && typeof price.max === "number"
            ? " $" + price.min.toLocaleString() + "–$" + price.max.toLocaleString()
            : "";
        p.textContent =
          (item.one_line || "") +
          band +
          (item.term ? " · " + item.term : "") +
          ". Not LIVE_PIN_OK.";
        li.appendChild(b);
        li.appendChild(kind);
        li.appendChild(p);
        skus.appendChild(li);
      });
    }
  }

  function paintSuccess(success) {
    if (!success || success.live || success.live_pin_ok || success.sku) return;
    function set(id, text) {
      var node = document.getElementById(id);
      if (node && text) node.textContent = text;
    }
    set("success-thesis", success.thesis);
    if (success.bake_off) {
      set("success-bake-lede", success.bake_off.lede);
      paintNamedCards("they-win", success.bake_off.they_win, "name", "note");
      paintNamedCards("we-win", success.bake_off.we_win, "name", "note");
    }
    if (success.qualify) {
      set("qualify-lede", success.qualify.lede);
      replacePlain("qualify-must", success.qualify.must);
      replacePlain("qualify-walk", success.qualify.walk_away);
    }
    paintNamedCards("objections", success.objections, "hear", "answer");
    if (success.ciso) {
      set("ciso-lede", success.ciso.lede);
      replacePlain("ciso-holds", success.ciso.holds);
      replacePlain("ciso-not", success.ciso.does_not);
    }
    if (success.seat_b) {
      set(
        "seat-b-lede",
        (success.seat_b.lede || "") +
          " " +
          (success.seat_b.name || "") +
          " · " +
          (success.seat_b.mailbox || "") +
          "."
      );
      replacePlain("seat-b-is", success.seat_b.is);
      replacePlain("seat-b-not", success.seat_b.is_not);
    }
    if (success.continuity) {
      set(
        "continuity",
        (success.continuity.lede || "") + " " + (success.continuity.note || "")
      );
    }
    paintHumanControl(success.human_control);
    paintExecutiveRisk(success.executive_risk);
    paintMarketPosition(success.market_position);
    paintWhatWasMissing(success.what_was_missing);
    paintManagedFace(success.managed_face);
    paintClientTwin(success.client_twin);
    paintCloseBench(success.close_bench);
    paintOperatingCompany(success.operating_company);
    paintBrand(success.brand);
    paintClientUniverse(success.client_universe);
    paintIndustryDrawer(success.industry_drawer);
  }

  function paintHumanControl(control) {
    if (!control || control.live || control.live_pin_ok || control.sku || control.fear_brand || control.cms) {
      return;
    }
    function set(id, text) {
      var node = document.getElementById(id);
      if (node && text) node.textContent = text;
    }
    set("control-lede", control.lede);
    set("control-ours", control.ours);
    set("control-not", control.not_ours);
    set("control-site", control.site);
    set("control-social", control.social);
    set("control-note", control.note);
    replacePlain("control-loss", control.loss);
    replacePlain("control-restore", control.restore);
  }

  function paintExecutiveRisk(risk) {
    if (!risk || risk.live || risk.live_pin_ok || risk.sku || risk.fear_brand || risk.cms || risk.counsel || risk.certified || risk.sox_opinion || risk.d_and_o) {
      return;
    }
    function set(id, text) {
      var node = document.getElementById(id);
      if (node && text) node.textContent = text;
    }
    set("risk-lede", risk.lede);
    set("risk-personal", risk.personal);
    set("risk-business", risk.business);
    set("risk-compliance", risk.compliance);
    set("risk-non", risk.non_compliance);
    set("risk-site", risk.site);
    set("risk-note", risk.note);
    replacePlain("risk-also", risk.also);
  }

  function paintMarketPosition(market) {
    if (!market || market.live || market.live_pin_ok || market.sku || market.forecast || market.priced_round || market.tam || market.launch || market.category_leader) {
      return;
    }
    function set(id, text) {
      var node = document.getElementById(id);
      if (node && text) node.textContent = text;
    }
    set("market-lede", market.lede);
    set("market-now", market.now);
    set("market-future", market.future);
    set("market-not", market.not_the_future);
    set("market-site", market.site);
    set("market-note", market.note);
    replacePlain("market-also", market.also);
  }

  function paintWhatWasMissing(missing) {
    if (!missing || missing.live || missing.live_pin_ok || missing.sku || missing.cms || missing.fourth_sku || missing.launch || missing.forecast) {
      return;
    }
    function set(id, text) {
      var node = document.getElementById(id);
      if (node && text) node.textContent = text;
    }
    set("have-lede", missing.lede);
    set("have-site", missing.site);
    set("have-note", missing.note);
    replacePlain("have-already", missing.already_have);
    replacePlain("have-missing", missing.been_missing);
    replacePlain("have-capabilities", missing.capabilities);
    replacePlain("have-tools", missing.tools_around);
    replacePlain("have-refuse", missing.refuse_to_become);
  }

  function paintManagedFace(face) {
    if (!face || face.live || face.live_pin_ok || face.sku || face.cms || face.dynamic || face.launch || face.fourth_sku) {
      return;
    }
    function set(id, text) {
      var node = document.getElementById(id);
      if (node && text) node.textContent = text;
    }
    set("class-lede", face.lede);
    set("class-product", face.product);
    set("class-demo", face.demo);
    set("class-managed", face.managed);
    set("class-note", face.note);
    set("product-lede", face.product);
  }

  function paintClientTwin(twin) {
    if (
      !twin ||
      twin.live ||
      twin.live_pin_ok ||
      twin.sku ||
      twin.fourth_sku ||
      twin.assigned ||
      twin.launch ||
      twin.production ||
      twin.named_client
    ) {
      return;
    }
    function set(id, text) {
      var node = document.getElementById(id);
      if (node && text) node.textContent = text;
    }
    set("path-lede", twin.lede);
    set("path-enhance", twin.enhance);
    set("path-deploy", twin.deploy);
    set("path-site", twin.site);
    set("path-note", twin.note);
    set("class-path", twin.glance || twin.lede);
    set("path-assigned", twin.assigned ? "Yes" : "No");
    set("path-named", twin.named_client || "None");
    replacePlain("path-stages", twin.stages);
    replacePlain("path-is", twin.is);
    replacePlain("path-not", twin.is_not);
  }

  function paintCloseBench(bench) {
    if (
      !bench ||
      bench.live ||
      bench.live_pin_ok ||
      bench.sku ||
      bench.fourth_sku ||
      bench.assigned ||
      bench.launch ||
      bench.production ||
      bench.named_client ||
      bench.cms ||
      bench.dynamic
    ) {
      return;
    }
    function set(id, text) {
      var node = document.getElementById(id);
      if (node && text) node.textContent = text;
    }
    set("path-lede", bench.lede);
    set("class-path", bench.glance || bench.lede);
    var planes = bench.planes || [];
    planes.forEach(function (plane) {
      if (!plane || !plane.id) return;
      set("path-plane-" + plane.id, plane.note);
    });
  }

  function paintOperatingCompany(firm) {
    if (
      !firm ||
      firm.live ||
      firm.live_pin_ok ||
      firm.sku ||
      firm.fourth_sku ||
      firm.crm ||
      firm.hubspot ||
      firm.salesforce ||
      firm.assigned ||
      firm.launch ||
      firm.production ||
      firm.named_client ||
      firm.named_contractor ||
      firm.sales_team_claimed ||
      firm.payouts_booked ||
      firm.cms ||
      firm.dynamic
    ) {
      return;
    }
    function set(id, text) {
      var node = document.getElementById(id);
      if (node && text) node.textContent = text;
    }
    set("firm-lede", firm.lede);
    set("class-firm", firm.glance || firm.lede);
    set("firm-site", firm.site);
    set("firm-note", firm.note);
    var cap = firm.capacity || {};
    if (cap.live === 0) set("firm-live", "0");
    if (cap.pipeline === 0) set("firm-pipeline", "0");
    set("firm-ics", "0");
    set("firm-payouts", "0");
    set("firm-launch", "No");
    (firm.rails || []).forEach(function (rail) {
      if (!rail || !rail.id) return;
      set("firm-rail-" + rail.id, rail.note);
    });
    var day = firm.day || {};
    if (!day.launch && !day.live_pin_ok && !day.sku) {
      (day.stages || []).forEach(function (stage) {
        if (!stage || !stage.id) return;
        set("firm-day-" + stage.id, stage.note);
      });
    }
    var roles = document.getElementById("firm-roles");
    if (roles && firm.roles && firm.roles.length) {
      roles.textContent = "";
      firm.roles.forEach(function (role) {
        if (!role) return;
        var li = document.createElement("li");
        var name = document.createElement("b");
        name.textContent = role.name || role.id || "";
        li.appendChild(name);
        var note = document.createElement("span");
        note.textContent = role.note || "";
        li.appendChild(note);
        roles.appendChild(li);
      });
    }
    var comp = firm.comp || {};
    if (!comp.booked && !comp.paid_count && !comp.from_this_plane && !comp.payroll_provider) {
      set("firm-comp-note", comp.note);
      var compList = document.getElementById("firm-comp");
      if (compList && (comp.closer || comp.bd || comp.residual || comp.hours)) {
        compList.textContent = "";
        [
          ["Closer", comp.closer],
          ["BD", comp.bd],
          ["Residual", comp.residual],
          ["Hours", comp.hours]
        ].forEach(function (row) {
          if (!row[1]) return;
          var li = document.createElement("li");
          li.textContent = row[0] + " — " + row[1];
          compList.appendChild(li);
        });
      }
    }
    var gates = firm.gates || {};
    if (!gates.launch && !gates.authorized_release && !gates.live_pin_ok && gates.gold_is_not_launch) {
      var gateList = document.getElementById("firm-gates");
      if (gateList && gates.items && gates.items.length) {
        gateList.textContent = "";
        gates.items.forEach(function (item) {
          if (!item) return;
          var li = document.createElement("li");
          li.setAttribute("data-ready", item.ready ? "yes" : "no");
          if (item.held) li.setAttribute("data-held", "yes");
          var name = document.createElement("b");
          name.textContent = item.name || item.id || "";
          li.appendChild(name);
          var note = document.createElement("span");
          var prefix = item.ready ? "" : item.held ? "Held. " : "Open. ";
          note.textContent = prefix + (item.note || "");
          li.appendChild(note);
          gateList.appendChild(li);
        });
      }
    }
    if (firm.needs && firm.needs.length) {
      set("firm-needs", firm.needs.join(". ") + ".");
    }
    var book = firm.service || {};
    if (!book.live && !book.padm && !book.ffs_hours && !book.hours_mint_sku && !book.hours_attach_udual && !book.shared_twin) {
      if (book.note) set("firm-service-status", book.note);
    }
    var run = firm.microsoft_run || {};
    if (
      !run.live &&
      !run.live_pin_ok &&
      !run.sku &&
      !run.crm &&
      !run.wired_claimed &&
      !run.microsoft_is_the_product &&
      !run.ninth_complement &&
      !run.roster_is_sku
    ) {
      set("firm-ms-lede", run.lede);
      var dayMap = document.getElementById("firm-ms-day");
      if (dayMap && run.day_map && run.day_map.length) {
        dayMap.textContent = "";
        run.day_map.forEach(function (item) {
          if (!item) return;
          var li = document.createElement("li");
          li.setAttribute("data-wired", item.wired ? "yes" : "no");
          var name = document.createElement("b");
          name.textContent = item.name || item.id || "";
          li.appendChild(name);
          var note = document.createElement("span");
          note.textContent = item.note || "";
          li.appendChild(note);
          dayMap.appendChild(li);
          set("firm-day-on-" + item.id, item.note);
        });
      }
      var spine = document.getElementById("firm-ms-spine");
      if (spine && run.spine && run.spine.length) {
        spine.textContent = "";
        run.spine.forEach(function (item) {
          if (!item) return;
          var li = document.createElement("li");
          li.setAttribute("data-wired", item.wired ? "yes" : "no");
          li.setAttribute("data-class", item.class || "required");
          var name = document.createElement("b");
          name.textContent = item.name || item.id || "";
          li.appendChild(name);
          var note = document.createElement("span");
          var meta = [item.job, item.day, item.status]
            .filter(Boolean)
            .join(" · ")
            .replace(/_/g, " ");
          note.textContent = (meta ? meta + ". " : "") + (item.note || "");
          li.appendChild(note);
          spine.appendChild(li);
        });
      }
      if (run.note) set("firm-ms-status", run.note);
      var opens = document.getElementById("firm-ms-opens");
      if (opens && run.owner_only && run.owner_only.length) {
        opens.textContent = "";
        run.owner_only.forEach(function (item) {
          var li = document.createElement("li");
          li.textContent = item;
          opens.appendChild(li);
        });
      }
    }
  }

  function paintBrand(brand) {
    if (
      !brand ||
      brand.sku ||
      brand.cms ||
      brand.fear_brand ||
      brand.live ||
      brand.live_pin_ok ||
      brand.launch ||
      brand.trademark_filed ||
      brand.microsoft_is_the_product
    ) {
      return;
    }
    function set(id, text) {
      var node = document.getElementById(id);
      if (node && text) node.textContent = text;
    }
    set("brand-lede", brand.lede);
    set("brand-status", (brand.site || "") + " " + (brand.note || ""));
    var voice = brand.voice || {};
    if (voice.ours || voice.not_ours) {
      set("brand-voice", [voice.ours, voice.not_ours].filter(Boolean).join(" "));
    }
    var list = document.getElementById("brand-surfaces");
    if (list && brand.surfaces && brand.surfaces.length) {
      list.textContent = "";
      brand.surfaces.forEach(function (item) {
        if (!item) return;
        var li = document.createElement("li");
        li.setAttribute("data-surface", item.id || "");
        var name = document.createElement("b");
        name.textContent = item.mark || item.id || "";
        li.appendChild(name);
        var note = document.createElement("span");
        note.textContent = item.note || "";
        li.appendChild(note);
        list.appendChild(li);
      });
    }
  }

  function paintClientUniverse(universe) {
    if (
      !universe ||
      universe.sku ||
      universe.cms ||
      universe.fear_brand ||
      universe.live ||
      universe.live_pin_ok ||
      universe.launch ||
      universe.assigned ||
      universe.named_client ||
      universe.mfa_admits ||
      universe.certified ||
      universe.forecast ||
      universe.wells_are_live ||
      universe.day_is_live ||
      universe.day_invented
    ) {
      return;
    }
    function set(id, text) {
      var node = document.getElementById(id);
      if (node && text) node.textContent = text;
    }
    set("universe-lede", universe.lede);
    set("universe-glance", universe.glance);
    set("universe-status", (universe.site || "") + " " + (universe.note || ""));
    var wells = universe.wells || {};
    set("universe-mark", wells.client_mark ? String(wells.client_mark) : "unnamed");
    set("universe-assigned", wells.assigned ? "yes" : "no");
    set("universe-first", String(wells.first_record || 0));
    set("universe-second", String(wells.second_record || 0));
    set("universe-maps", wells.maps_claimed ? "claimed" : "claimed=false");
    set("universe-packs", String(wells.packs_attached || 0));
    function rail(item) {
      var li = document.createElement("li");
      li.setAttribute("data-surface", item.id || "");
      var name = document.createElement("b");
      name.textContent = item.name || item.id || "";
      var href = String(item.href || "");
      if (href && (href.charAt(0) === "#" || href.indexOf("identify.html") === 0)) {
        var a = document.createElement("a");
        a.setAttribute("href", href);
        a.appendChild(name);
        li.appendChild(a);
      } else {
        li.appendChild(name);
      }
      var note = document.createElement("span");
      note.textContent = item.note || "";
      li.appendChild(note);
      return li;
    }
    var groupsRoot = document.getElementById("universe-groups");
    var byId = {};
    (universe.surfaces || []).forEach(function (item) {
      if (item && item.id) byId[item.id] = item;
    });
    var dayRoot = document.getElementById("universe-day");
    if (dayRoot && universe.day && universe.day.lanes && !universe.day.live && !universe.day.invented) {
      dayRoot.textContent = "";
      universe.day.lanes.forEach(function (lane) {
        if (!lane) return;
        var section = document.createElement("section");
        section.setAttribute("data-lane", lane.id || "");
        var title = document.createElement("h3");
        title.textContent = lane.name || lane.id || "";
        section.appendChild(title);
        var list = document.createElement("ol");
        (lane.items || []).forEach(function (item) {
          if (item) list.appendChild(rail(item));
        });
        section.appendChild(list);
        dayRoot.appendChild(section);
      });
    }
    var spine = document.getElementById("universe-spine");
    var states = universe.spine_states || {};
    if (spine) {
      Object.keys(states).forEach(function (id) {
        var node = spine.querySelector('[data-rail="' + id + '"]');
        if (node) node.setAttribute("data-state", states[id]);
      });
    }
    if (groupsRoot && universe.groups && universe.groups.length) {
      groupsRoot.textContent = "";
      universe.groups.forEach(function (group) {
        if (!group) return;
        var section = document.createElement("section");
        section.setAttribute("data-group", group.id || "");
        var title = document.createElement("h4");
        title.textContent = group.name || group.id || "";
        section.appendChild(title);
        var list = document.createElement("ol");
        list.className = "brand-surfaces universe-surfaces";
        (group.rails || []).forEach(function (railId) {
          var item = byId[railId];
          if (item) list.appendChild(rail(item));
        });
        section.appendChild(list);
        groupsRoot.appendChild(section);
      });
    }
  }

  function paintIndustryDrawer(drawer) {
    if (
      !drawer ||
      drawer.sku ||
      drawer.cms ||
      drawer.fear_brand ||
      drawer.certified ||
      drawer.live ||
      drawer.live_pin_ok ||
      drawer.launch ||
      drawer.named_vertical ||
      drawer.filing ||
      drawer.drawer_is_live ||
      drawer.drawer_invented ||
      drawer.crypto_product ||
      drawer.seventeen_a4 ||
      (drawer.rooms && (
        drawer.rooms.live ||
        drawer.rooms.crypto_product ||
        drawer.rooms.seventeen_a4 ||
        drawer.rooms.assigned ||
        drawer.rooms.named_vertical ||
        drawer.rooms.rooms_are_live ||
        drawer.rooms.wells_are_live ||
        drawer.rooms.operable === false ||
        drawer.rooms.fully_operable === false ||
        drawer.rooms.every_refuse_clicks === false ||
        drawer.rooms.complete === false
      )) ||
      drawer.fully_operable === false ||
      drawer.every_refuse_clicks === false ||
      drawer.complete === false ||
      drawer.honest_control === false ||
      (drawer.control && (
        drawer.control.live ||
        drawer.control.claimed ||
        drawer.control.genius_closed ||
        drawer.control.clarity_closed ||
        drawer.control.governess ||
        drawer.control.dno ||
        drawer.control.policy_sku ||
        drawer.control.fear_brand ||
        drawer.control.control_is_live ||
        drawer.control.honest === false ||
        drawer.control.every_refuse_clicks === false
      ))
    ) {
      return;
    }
    function set(id, text) {
      var node = document.getElementById(id);
      if (node && text) node.textContent = text;
    }
    set("industry-lede", drawer.lede);
    set("industry-glance", drawer.glance);
    set("industry-status", drawer.site || "");
    set("class-industry", drawer.glance);
    function refuseButton(item, attr) {
      var name = document.createElement("b");
      name.textContent = item.name || item.id || "";
      var btn = document.createElement("button");
      btn.setAttribute("type", "button");
      btn.className = "ghost room-refuse";
      btn.setAttribute("data-room-refuse", item.id || "");
      if (item.refuse_text) btn.setAttribute("data-refuse-text", item.refuse_text);
      btn.setAttribute("aria-pressed", "false");
      btn.appendChild(name);
      return btn;
    }
    function rail(item) {
      var li = document.createElement("li");
      if (item.id) li.setAttribute("data-day", item.id);
      if (item.refuse) {
        li.appendChild(refuseButton(item));
      } else {
        var name = document.createElement("b");
        name.textContent = item.name || item.id || "";
        var href = String(item.href || "");
        if (href && (href.charAt(0) === "#" || href.indexOf("identify.html") === 0 || href.indexOf("app.html") === 0)) {
          var a = document.createElement("a");
          a.setAttribute("href", href);
          a.appendChild(name);
          li.appendChild(a);
        } else {
          li.appendChild(name);
        }
      }
      var note = document.createElement("span");
      note.textContent = item.note || "";
      li.appendChild(note);
      return li;
    }
    var dayRoot = document.getElementById("industry-day");
    if (dayRoot && drawer.lanes && drawer.lanes.length) {
      dayRoot.textContent = "";
      drawer.lanes.forEach(function (lane) {
        if (!lane) return;
        var section = document.createElement("section");
        section.setAttribute("data-lane", lane.id || "");
        var title = document.createElement("h3");
        title.textContent = lane.name || lane.id || "";
        section.appendChild(title);
        var list = document.createElement("ol");
        (lane.items || []).forEach(function (item) {
          if (item) list.appendChild(rail(item));
        });
        section.appendChild(list);
        dayRoot.appendChild(section);
      });
    }
    var papers = document.getElementById("industry-papers");
    if (papers && drawer.papers && drawer.papers.length) {
      papers.textContent = "";
      drawer.papers.forEach(function (item) {
        if (!item) return;
        var li = rail(item);
        li.setAttribute("data-paper", item.id || "");
        papers.appendChild(li);
      });
    }
    var areas = document.getElementById("industry-areas");
    if (areas && drawer.areas && drawer.areas.length) {
      areas.textContent = "";
      drawer.areas.forEach(function (item) {
        if (!item) return;
        var li = rail(item);
        li.setAttribute("data-area", item.id || "");
        areas.appendChild(li);
      });
    }
    var roomsRoot = document.getElementById("industry-rooms");
    var rooms = drawer.rooms || {};
    var wells = rooms.wells || {};
    set("industry-assigned", rooms.assigned ? "yes" : "no");
    set("industry-named", rooms.named_vertical || wells.named ? String(wells.named || "yes") : "no");
    set("industry-first", String(wells.room_1 || 0));
    set("industry-second", String(wells.room_2 || 0));
    set("industry-maps", "claimed=false");
    set("industry-crypto", rooms.crypto_product ? "yes" : "no");
    set("industry-seventeen", rooms.seventeen_a4 ? "yes" : "no");
    var control = drawer.control || {};
    set("industry-control-honest", control.honest === false ? "no" : "yes");
    set("industry-genius", control.genius_closed ? "yes" : "no");
    set("industry-clarity", control.clarity_closed ? "yes" : "no");
    var controlRoot = document.getElementById("industry-control");
    if (controlRoot && control.lanes && control.lanes.length) {
      controlRoot.textContent = "";
      control.lanes.forEach(function (lane) {
        if (!lane) return;
        var section = document.createElement("section");
        section.setAttribute("data-lane", lane.id || "");
        var title = document.createElement("h3");
        title.textContent = lane.name || lane.id || "";
        section.appendChild(title);
        var list = document.createElement("ol");
        (lane.items || []).forEach(function (item) {
          if (!item) return;
          var li = rail(item);
          li.setAttribute("data-control", item.id || "");
          list.appendChild(li);
        });
        section.appendChild(list);
        controlRoot.appendChild(section);
      });
    }
    function roomRail(item) {
      var li = document.createElement("li");
      if (item.id) li.setAttribute("data-room", item.id);
      var name = document.createElement("b");
      name.textContent = item.name || item.id || "";
      if (item.refuse) {
        li.appendChild(refuseButton(item));
      } else {
        var href = String(item.href || "");
        if (href && (href.charAt(0) === "#" || href.indexOf("identify.html") === 0 || href.indexOf("app.html") === 0)) {
          var a = document.createElement("a");
          a.setAttribute("href", href);
          a.appendChild(name);
          li.appendChild(a);
        } else {
          li.appendChild(name);
        }
      }
      var note = document.createElement("span");
      note.textContent = item.note || "";
      li.appendChild(note);
      return li;
    }
    if (roomsRoot && rooms.room_1 && rooms.room_2) {
      roomsRoot.textContent = "";
      [
        { id: "room_1", name: "Room 1 · books", items: rooms.room_1 },
        { id: "room_2", name: "Room 2 · refuse", items: rooms.room_2 }
      ].forEach(function (lane) {
        var section = document.createElement("section");
        section.setAttribute("data-room", lane.id);
        var title = document.createElement("h3");
        title.textContent = lane.name;
        section.appendChild(title);
        var list = document.createElement("ol");
        (lane.items || []).forEach(function (item) {
          if (item) list.appendChild(roomRail(item));
        });
        section.appendChild(list);
        roomsRoot.appendChild(section);
      });
    }
    var spine = document.getElementById("industry-room-spine");
    var states = rooms.spine_states || {};
    if (spine) {
      Object.keys(states).forEach(function (id) {
        var node = spine.querySelector('[data-spine="' + id + '"]');
        if (node) node.setAttribute("data-state", states[id]);
      });
    }
  }

  function replacePlain(id, items) {
    var node = document.getElementById(id);
    if (!node || !items || !items.length) return;
    node.textContent = "";
    items.forEach(function (item) {
      var li = document.createElement("li");
      li.textContent = item;
      node.appendChild(li);
    });
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

  function downloadProofDayBrief(statusId) {
    var page = lastBuyer || buyerPayload();
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
      bake_off: (page.success && page.success.bake_off) || null,
      qualify: (page.success && page.success.qualify) || null,
      walk_away:
        (page.success && page.success.qualify && page.success.qualify.walk_away) || [],
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
    var status = document.getElementById(statusId);
    if (status) {
      status.hidden = false;
      status.textContent = "Brief downloaded. Forward it. There is no contact inbox on this page.";
    }
  }

  var ask = document.getElementById("ask-proof-day");
  if (ask) {
    ask.addEventListener("click", function () {
      downloadProofDayBrief("brief-status");
    });
  }

  fetch("status.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data || data.live || data.live_pin_ok) return;
      function replacePlainList(id, items) {
        var node = document.getElementById(id);
        if (!node) return;
        node.innerHTML = "";
        (items || []).forEach(function (item) {
          var li = document.createElement("li");
          li.textContent = item;
          node.appendChild(li);
        });
      }
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
      if (data.e7_cloudflare) {
        var edge = data.e7_cloudflare;
        if (
          edge.sku ||
          edge.live ||
          edge.live_pin_ok ||
          edge.is_admit_plane ||
          edge.complement ||
          edge.connection
        ) {
          /* refuse to paint a fiction scoreboard */
        } else {
          replacePlainList("e7-cloudflare-already", edge.already);
          if (!edge.missing || !edge.missing.length) {
            replacePlainList("e7-cloudflare-missing", ["None. E7 DNS is full."]);
          } else {
            replacePlainList("e7-cloudflare-missing", edge.missing);
          }
          var edgeStatus = document.getElementById("e7-cloudflare-status");
          if (edgeStatus) {
            edgeStatus.textContent =
              "full=" +
              edge.full +
              " · sku=" +
              edge.sku +
              " · live=" +
              edge.live +
              " · is_admit_plane=" +
              edge.is_admit_plane +
              " · complement=" +
              edge.complement;
          }
          var edgePlan = document.getElementById("e7-cloudflare-plan");
          if (edgePlan) {
            edgePlan.textContent =
              "plan=" +
              (edge.plan || "pro") +
              " · plan_sku=" +
              (edge.plan_sku === true) +
              " · from_this_plane=" +
              (edge.from_this_plane === true);
          }
          if (edge.activate && !edge.activate.from_this_plane) {
            paintIntegrate("e7-cloudflare-activate", {
              items: (edge.activate.now || []).map(function (item) {
                return {
                  url: item.url,
                  url_label: item.url_label,
                  note: item.do,
                };
              }),
            });
            var wait = document.getElementById("e7-cloudflare-wait");
            if (wait && edge.activate.wait && edge.activate.wait.length) {
              wait.textContent =
                "Wait: " +
                edge.activate.wait
                  .map(function (item) {
                    return item.do;
                  })
                  .join(" ");
            }
          }
          var edgeNote = document.getElementById("e7-cloudflare-note");
          if (edgeNote && edge.note) edgeNote.textContent = edge.note;
          var quality = edge.quality || {};
          if (
            quality.sku ||
            quality.live ||
            quality.live_pin_ok ||
            quality.apex_is_institute ||
            quality.ssl_full_claimed ||
            quality.rocket_loader_claimed ||
            (quality.owner_ssl && quality.owner_ssl.from_this_plane) ||
            (edge.twin && (edge.twin.authorized || edge.twin.launch || edge.twin.live || edge.twin.live_pin_ok))
          ) {
            /* refuse to paint a fiction quality board */
          } else {
            replacePlainList("e7-cloudflare-verified", quality.verified);
            replacePlainList("e7-cloudflare-owner-recorded", quality.owner_recorded);
            replacePlainList("e7-cloudflare-confirm", quality.confirm);
            replacePlainList("e7-cloudflare-refuse", quality.refuse);
            replacePlainList("e7-cloudflare-quality-wait", quality.wait);
            var qualityNote = document.getElementById("e7-cloudflare-quality");
            if (qualityNote && quality.note) qualityNote.textContent = quality.note;
          }
          var holding = document.getElementById("e7-cloudflare-holding");
          if (holding && edge.holding && !edge.holding.host && !edge.holding.institute && !edge.holding.launch) {
            holding.textContent =
              "holding=" +
              (edge.holding.origin || "ainav-institute.pages.dev") +
              " · host=" +
              (edge.holding.host === true) +
              " · institute=" +
              (edge.holding.institute === true) +
              " · launch=" +
              (edge.holding.launch === true) +
              " · " +
              (edge.holding.note || "Empty Pages is not the Institute. Leave the zone as-is.");
          }
          var twinNode = document.getElementById("institute-twin");
          var twin = edge.twin || {};
          if (
            twinNode &&
            twin.lede &&
            !twin.sku &&
            !twin.live &&
            !twin.live_pin_ok &&
            !twin.launch &&
            !twin.authorized &&
            !twin.from_this_plane
          ) {
            twinNode.textContent = twin.lede + " " + (twin.note || "");
          }
          var site = data.website || {};
          var review = document.getElementById("twin-review-status");
          if (
            review &&
            site.twin_review &&
            !site.authorized_release &&
            !site.launch_ready &&
            !site.pages_is_host
          ) {
            review.textContent =
              "twin_review=" +
              site.twin_review +
              " · review_path=" +
              (site.review_path || "twin.html") +
              " · authorized_release=" +
              (site.authorized_release === true) +
              " · launch_ready=" +
              (site.launch_ready === true);
          }
          var hostStatus = document.getElementById("twin-host-status");
          if (
            hostStatus &&
            site.twin_review &&
            !site.authorized_release &&
            !site.launch_ready
          ) {
            hostStatus.textContent =
              "host=" +
              (site.twin_host || "azure.swa") +
              " · public_edge=" +
              (site.public_edge || "cloudflare") +
              " · authorized_release=false · launch_ready=false · pages_is_host=false";
          }
        }
      }
      if (data.engineering) {
        var eng = data.engineering;
        if (
          eng.sku ||
          eng.live ||
          eng.live_pin_ok ||
          eng.launch ||
          eng.is_admit_plane
        ) {
          /* refuse to paint a fiction scoreboard */
        } else {
          replacePlainList("closed-in-tree", eng.closed_in_tree);
          replacePlainList("cannot-close", eng.cannot_close);
          var goldNote = document.getElementById("gold-ci-note");
          if (goldNote && eng.gold_ci && eng.gold_ci.note) goldNote.textContent = eng.gold_ci.note;
          var goldStatus = document.getElementById("gold-ci-status");
          if (goldStatus && eng.gold_ci) {
            goldStatus.textContent =
              "exists=" +
              eng.gold_ci.exists +
              " · observed_green=" +
              eng.gold_ci.observed_green +
              " · marks_live_pin=" +
              eng.gold_ci.marks_live_pin +
              " · launch=" +
              eng.launch +
              " · sku=" +
              eng.sku;
          }
        }
      }
      if (data.honest_missing && data.honest_missing.length) {
        replacePlainList("honest-missing", data.honest_missing);
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

  function writePathLedger(kind, text) {
    var box = document.getElementById("path-ledger");
    if (!box) return;
    var row = document.createElement("pre");
    row.className = kind === "ok" ? "ok" : "denied";
    row.textContent = text;
    box.insertBefore(row, box.firstChild);
  }

  var pathWalk = document.getElementById("path-walk");
  if (pathWalk) {
    pathWalk.addEventListener("click", function () {
      var status = document.getElementById("path-qualify-status");
      if (status) status.textContent = "Walked cheaper native. Count stays 0. Do not invent a named controller.";
      writePathLedger(
        "ok",
        "walk_preview · cheaper native\nQualify refused Workflow User Groups / Copilot Studio RFI as the product.\nWalk-away ledger recorded=false count=0.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var pathInvent = document.getElementById("path-invent");
  if (pathInvent) {
    pathInvent.addEventListener("click", function () {
      var status = document.getElementById("path-qualify-status");
      if (status) status.textContent = "Refused. Do not invent a named customer.";
      writePathLedger(
        "denied",
        "qualify_denied · invented name\nAcme / Contoso / Fabrikam are not clients.\nNamed client stays none. Assigned stays no.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var pathBrief = document.getElementById("path-copy-brief");
  if (pathBrief) {
    pathBrief.addEventListener("click", function () {
      downloadProofDayBrief("path-proof-status");
      writePathLedger(
        "ok",
        "brief_preview · ainav.proof_day.brief.v1\nForwardable. No inbox. No named customer.\nRemote demo stays #twin.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var pathAssign = document.getElementById("path-assign");
  if (pathAssign) {
    pathAssign.addEventListener("click", function () {
      var a = ((document.getElementById("path-seat-a") || {}).value || "").trim();
      var b = ((document.getElementById("path-seat-b") || {}).value || "").trim();
      var status = document.getElementById("path-close-status");
      if (/acme|contoso|fabrikam|northwind/i.test(a + " " + b)) {
        if (status) status.textContent = "Refused. Do not invent a named customer.";
        writePathLedger(
          "denied",
          "assign_denied · invented name\nSeat titles are not a named client.\nAssigned stays no. Count stays 0.\nlive=false · live_pin_ok=false"
        );
        return;
      }
      if (status) status.textContent = "Refused. Signed L1 is 0. Assigned stays no.";
      writePathLedger(
        "denied",
        "assign_denied · no signed L1\nThe client twin is assigned after qualify or with L1.\nThis plane cannot invent the assignment.\nAssigned=false · named_client=null · count=0\nlive=false · live_pin_ok=false"
      );
    });
  }

  var pathUdual = document.getElementById("path-udual");
  if (pathUdual) {
    pathUdual.addEventListener("click", function () {
      var status = document.getElementById("path-close-status");
      if (status) status.textContent = "Refused. Hours never attach free U-DUAL.";
      writePathLedger(
        "denied",
        "enhance_denied · free U-DUAL\nPaid enhance stays on the assigned sandbox.\nHours deepen the same admit plane. They never mint a SKU.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var pathPromote = document.getElementById("path-promote");
  if (pathPromote) {
    pathPromote.addEventListener("click", function () {
      var status = document.getElementById("path-close-status");
      if (status) status.textContent = "Refused. Production is owner-gated. LIVE_PIN_OK stays false.";
      writePathLedger(
        "denied",
        "promote_denied · production blocked\nInstitute twin is the remote demo. Client twin is a sandbox.\nDo not auto-promote. LIVE_PIN_OK is owner-only.\nlive=false · live_pin_ok=false"
      );
    });
  }

  function writeFirmLedger(kind, text) {
    var box = document.getElementById("firm-ledger");
    if (!box) return;
    var row = document.createElement("pre");
    row.className = kind === "ok" ? "ok" : "denied";
    row.textContent = text;
    box.insertBefore(row, box.firstChild);
  }

  var firmQualify = document.getElementById("firm-qualify");
  if (firmQualify) {
    firmQualify.addEventListener("click", function () {
      window.location.hash = "#success";
    });
  }

  var firmInventLead = document.getElementById("firm-invent-lead");
  if (firmInventLead) {
    firmInventLead.addEventListener("click", function () {
      var status = document.getElementById("firm-pipeline-status");
      if (status) status.textContent = "Refused. Do not invent 500 leads. Pipeline stays 0 of 500.";
      writeFirmLedger(
        "denied",
        "pipeline_denied · invented leads\n500 is capacity. It is not a booked pipeline.\nNamed leads stay 0.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var firmInventLive = document.getElementById("firm-invent-live");
  if (firmInventLive) {
    firmInventLive.addEventListener("click", function () {
      var status = document.getElementById("firm-live-status");
      if (status) status.textContent = "Refused. Do not invent 500 live clients. Live stays 0 of 500.";
      writeFirmLedger(
        "denied",
        "live_denied · invented book\n500 live is capacity. Signed L1 stays 0.\nOne live client would get one segregated sandbox.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var firmHire = document.getElementById("firm-hire");
  if (firmHire) {
    firmHire.addEventListener("click", function () {
      var name = ((document.getElementById("firm-ic-name") || {}).value || "").trim();
      var status = document.getElementById("firm-people-status");
      if (/acme|contoso|fabrikam|northwind/i.test(name) || name) {
        if (status) status.textContent = "Refused. Do not invent a named contractor.";
        writeFirmLedger(
          "denied",
          "hire_denied · invented contractor\nICs are not seats. Named contractors stay 0.\nG12 MSA stays open.\nlive=false · live_pin_ok=false"
        );
        return;
      }
      if (status) status.textContent = "Refused. Named contractors stay 0. ICs are not seats.";
      writeFirmLedger(
        "denied",
        "hire_denied · no named 1099\nRoles exist. Headcount stays uninvented.\nThis plane cannot hire.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var firmPay = document.getElementById("firm-pay");
  if (firmPay) {
    firmPay.addEventListener("click", function () {
      var status = document.getElementById("firm-people-status");
      if (status) status.textContent = "Refused. This plane cannot pay a commission. Payouts stay 0.";
      writeFirmLedger(
        "denied",
        "payout_denied · no recognized receipt\nComp is catalog policy. Booked=false. paid_count=0.\nOwner marks payout after bank receipt.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var firmCrm = document.getElementById("firm-crm");
  if (firmCrm) {
    firmCrm.addEventListener("click", function () {
      var status = document.getElementById("firm-people-status");
      if (status) status.textContent = "Refused. HubSpot is not the firm. This bench is the operating day.";
      writeFirmLedger(
        "denied",
        "crm_denied · HubSpot / Salesforce\nThe product is the admit plane. The firm is this operating day.\nNot a CRM SKU. Gold is not launch.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var firmCalendly = document.getElementById("firm-invent-calendly");
  if (firmCalendly) {
    firmCalendly.addEventListener("click", function () {
      var status = document.getElementById("firm-proof-status");
      if (status) status.textContent = "Refused. Calendly is not the proof. Demo is #twin.";
      writeFirmLedger(
        "denied",
        "proof_denied · Calendly\nNinety minutes stay on the Institute twin.\nGraph is not called.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var firmAssignShared = document.getElementById("firm-assign-shared");
  if (firmAssignShared) {
    firmAssignShared.addEventListener("click", function () {
      var status = document.getElementById("firm-assign-status");
      if (status) status.textContent = "Refused. One live client, one segregated sandbox. Shared twin is a walk-away.";
      writeFirmLedger(
        "denied",
        "assign_denied · shared twin\nAssigned stays 0 until a real L1.\nInstitute twin is not client production.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var firmKeep = document.getElementById("firm-keep");
  if (firmKeep) {
    firmKeep.addEventListener("click", function () {
      var status = document.getElementById("firm-service-status");
      if (status) status.textContent = "Refused. Live book is 0. P-ADM attaches after kit PASS on an assigned twin.";
      writeFirmLedger(
        "denied",
        "service_denied · empty live book\nP-ADM 0. FFS hours 0.\nHours never mint a SKU.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var firmHours = document.getElementById("firm-hours-udual");
  if (firmHours) {
    firmHours.addEventListener("click", function () {
      var status = document.getElementById("firm-service-status");
      if (status) status.textContent = "Refused. Hours never attach free U-DUAL. Hours never mint a SKU.";
      writeFirmLedger(
        "denied",
        "udual_denied · service hours\nFFS deepens the same admit plane.\nU-DUAL stays a paid SKU.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var firmMarkLaunch = document.getElementById("firm-mark-launch");
  if (firmMarkLaunch) {
    firmMarkLaunch.addEventListener("click", function () {
      var status = document.getElementById("firm-launch-status");
      if (status) status.textContent = "Refused. Launch gate closed. Gold is not launch. Owner says launch.";
      writeFirmLedger(
        "denied",
        "launch_denied · gate closed\nSeat B click open. Signed L1 0. LIVE_PIN_OK false.\nGold 99 is the release floor, not launch.\nlaunch=false · live_pin_ok=false"
      );
    });
  }

  var firmMarkPin = document.getElementById("firm-mark-pin");
  if (firmMarkPin) {
    firmMarkPin.addEventListener("click", function () {
      var status = document.getElementById("firm-launch-status");
      if (status) status.textContent = "Refused. LIVE_PIN_OK is owner-only. This plane cannot mark it.";
      writeFirmLedger(
        "denied",
        "pin_denied · LIVE_PIN_OK\nProduction write stays owner-gated.\nDo not auto-promote a sandbox.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var firmWireTeams = document.getElementById("firm-wire-teams");
  if (firmWireTeams) {
    firmWireTeams.addEventListener("click", function () {
      var status = document.getElementById("firm-ms-status");
      if (status) status.textContent = "Refused. Teams team and channel ids stay owner-only. A chat is not a seat.";
      writeFirmLedger(
        "denied",
        "teams_denied · licensed_not_wired\nTEAMS_*_TEAM_ID and TEAMS_*_CHANNEL_ID stay unset.\nNotify is not dual admit.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var firmCloseDataverse = document.getElementById("firm-close-dataverse");
  if (firmCloseDataverse) {
    firmCloseDataverse.addEventListener("click", function () {
      var status = document.getElementById("firm-ms-status");
      if (status) status.textContent = "Refused. US Dataverse stays open. Canada is not United States.";
      writeFirmLedger(
        "denied",
        "dataverse_denied · Canada affinity\nTicket 2609030040009525. DATAVERSE_URL stays unset.\nSales Enterprise is not the firm CRM.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var firmTrashWrites = document.getElementById("firm-trash-writes");
  if (firmTrashWrites) {
    firmTrashWrites.addEventListener("click", function () {
      var status = document.getElementById("firm-ms-status");
      if (status) status.textContent = "Refused. Graph Writes revoke-then-grant is owner-only. This plane cannot grant.";
      writeFirmLedger(
        "denied",
        "graph_denied · Writes still Granted\nTrash Organization.ReadWrite.All and User.ReadWrite.All, then Grant again.\nThis plane cannot invent consent.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var firmMsProduct = document.getElementById("firm-ms-product");
  if (firmMsProduct) {
    firmMsProduct.addEventListener("click", function () {
      var status = document.getElementById("firm-ms-status");
      if (status) status.textContent = "Refused. Microsoft is not the product. Complements stay eight.";
      writeFirmLedger(
        "denied",
        "product_denied · Microsoft is the substrate\nIdentity, notify, SoR, keep, host.\nThe product is the admit plane.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var firmWireDay = document.getElementById("firm-wire-day");
  if (firmWireDay) {
    firmWireDay.addEventListener("click", function () {
      var status = document.getElementById("firm-ms-status");
      if (status) status.textContent = "Refused. The day map is catalog law. Licensed-not-wired stays honest.";
      writeFirmLedger(
        "denied",
        "day_map_denied · catalog law\nEvery stage names its Microsoft substrate.\nAssign sits on Azure host. Not wired.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var firmWireSharepoint = document.getElementById("firm-wire-sharepoint");
  if (firmWireSharepoint) {
    firmWireSharepoint.addEventListener("click", function () {
      var status = document.getElementById("firm-ms-status");
      if (status) status.textContent = "Refused. SHAREPOINT_SITE_ID stays owner-only. This plane cannot invent a SharePoint site.";
      writeFirmLedger(
        "denied",
        "sharepoint_denied · licensed_not_wired\nSHAREPOINT_SITE_ID stays unset.\nKit evidence is not dual admit.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var firmWireSentinel = document.getElementById("firm-wire-sentinel");
  if (firmWireSentinel) {
    firmWireSentinel.addEventListener("click", function () {
      var status = document.getElementById("firm-ms-status");
      if (status) status.textContent = "Refused. Sentinel on the existing LAW stays owner-only. LAW is not Sentinel.";
      writeFirmLedger(
        "denied",
        "sentinel_denied · law_is_not_sentinel\nThe mothership LAW is not Sentinel.\nThis plane cannot enable Sentinel.\nlive=false · live_pin_ok=false"
      );
    });
  }

  function refuseBrand(message, ledger) {
    var status = document.getElementById("brand-status");
    if (status) status.textContent = message;
    writeFirmLedger("denied", ledger);
  }

  var brandRebrand = document.getElementById("brand-rebrand");
  if (brandRebrand) {
    brandRebrand.addEventListener("click", function () {
      refuseBrand(
        "Refused. Lockfile stays job_c. A rebrand of Job C breaks gold.",
        "brand_denied · rebrand Job C\nLockfile product stays job_c.\nrefuse_lockfile_rebrand.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var brandFear = document.getElementById("brand-fear");
  if (brandFear) {
    brandFear.addEventListener("click", function () {
      refuseBrand(
        "Refused. Write-fear names the unauthorized journal. Doom-fear is not a brand.",
        "brand_denied · fear brand\nWrite-fear is the sale.\nAGI theater walks like cheaper native.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var brandMsProduct = document.getElementById("brand-ms-product");
  if (brandMsProduct) {
    brandMsProduct.addEventListener("click", function () {
      refuseBrand(
        "Refused. Microsoft marks name integrations. Microsoft is not the product.",
        "brand_denied · Microsoft is the substrate\nTeams, Sales, and Azure stay their marks.\nThe product is the admit plane.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var brandTeamsName = document.getElementById("brand-teams-name");
  if (brandTeamsName) {
    brandTeamsName.addEventListener("click", function () {
      refuseBrand(
        "Refused. Teams team and channel ids stay unset. This plane cannot invent a live team name.",
        "brand_denied · invent Teams team name\nNotify is not a seat.\nIds stay owner-only.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var brandSandboxProd = document.getElementById("brand-sandbox-prod");
  if (brandSandboxProd) {
    brandSandboxProd.addEventListener("click", function () {
      refuseBrand(
        "Refused. The sandbox is unnamed until signed L1. Lab pin AINAV-L1 is not commercial close.",
        "brand_denied · sandbox as production brand\nClient twin stays unnamed until signed L1.\nNever shared. Not production.\nlive=false · live_pin_ok=false"
      );
    });
  }

  function writeUniverseLedger(text) {
    var box = document.getElementById("universe-ledger");
    if (!box) return;
    var row = document.createElement("pre");
    row.className = "denied";
    row.textContent = text;
    box.insertBefore(row, box.firstChild);
  }

  function refuseUniverse(button, message, ledger) {
    var refuse = document.getElementById("universe-refuse");
    if (refuse) {
      refuse.textContent = message;
      refuse.classList.add("is-live");
    }
    if (button) button.setAttribute("aria-pressed", "true");
    writeUniverseLedger(ledger);
    writeFirmLedger("denied", ledger);
  }

  var universeMfa = document.getElementById("universe-mfa-admit");
  if (universeMfa) {
    universeMfa.addEventListener("click", function () {
      refuseUniverse(
        universeMfa,
        "Refused. MFA identifies. Identify is not admit. Credentialed SWA identify is not seated.",
        "universe_denied · MFA as admit\nMFA and Conditional Access identify.\nThey do not admit.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var universeNamed = document.getElementById("universe-named-client");
  if (universeNamed) {
    universeNamed.addEventListener("click", function () {
      refuseUniverse(
        universeNamed,
        "Refused. The client sandbox stays unnamed until signed L1. This plane cannot invent a named client.",
        "universe_denied · invent a named client\nAssigned stays false.\nNamed client stays false.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var universeSandbox = document.getElementById("universe-sandbox-prod");
  if (universeSandbox) {
    universeSandbox.addEventListener("click", function () {
      refuseUniverse(
        universeSandbox,
        "Refused. The segregated branded sandbox is not production. Lab pin AINAV-L1 is not commercial close.",
        "universe_denied · sandbox as production\nNever shared. Not the Institute twin.\nAssigned after signed L1.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var universeCertify = document.getElementById("universe-certify");
  if (universeCertify) {
    universeCertify.addEventListener("click", function () {
      refuseUniverse(
        universeCertify,
        "Refused. Maps stay claimed=false. Buying L1 does not close regulator clocks. Not a certificate.",
        "universe_denied · certify maps\nNIST, SOX, EU AI Act, ISO 42001 stay maps.\nNot D&O. Not a SOX opinion.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var universeFourth = document.getElementById("universe-fourth-sku");
  if (universeFourth) {
    universeFourth.addEventListener("click", function () {
      refuseUniverse(
        universeFourth,
        "Refused. Three SKUs only. Packs, libraries, and FFS hours are not SKUs.",
        "universe_denied · fourth SKU\nP-ADM keep. Paid U-DUAL deepen.\nHours never mint a SKU.\nlive=false · live_pin_ok=false"
      );
    });
  }

  function writeIndustryLedger(text) {
    var box = document.getElementById("industry-ledger");
    if (!box) return;
    var row = document.createElement("pre");
    row.className = "denied";
    row.textContent = text;
    box.insertBefore(row, box.firstChild);
  }

  function refuseIndustry(button, message, ledger) {
    var refuse = document.getElementById("industry-refuse");
    if (refuse) {
      refuse.textContent = message;
      refuse.classList.add("is-live");
    }
    if (button) button.setAttribute("aria-pressed", "true");
    writeIndustryLedger(ledger);
    writeFirmLedger("denied", ledger);
  }

  var ROOM_2_REFUSE = {
    stablecoin_mint: {
      message: "Refused. Not a stablecoin SKU. Room 2 is refuse.",
      ledger: "industry_denied · stablecoin mint\nOn-chain mint stays Room 2.\nNot a fourth SKU.\nlive=false · live_pin_ok=false"
    },
    rwa_issue: {
      message: "Refused. Not a tokenization SKU. Not an RWA SKU. Room 2 is refuse.",
      ledger: "industry_denied · RWA issuance\nIssuing the token stays Room 2.\nBooked receivable is Room 1.\nlive=false · live_pin_ok=false"
    },
    crypto_ams: {
      message: "Refused. Not a crypto asset-management SKU. Room 2 is refuse.",
      ledger: "industry_denied · crypto AMS\nWallet signing stays Room 2.\nNot a crypto product.\nlive=false · live_pin_ok=false"
    },
    wallet: {
      message: "Refused. Wallet is not a seat. Room 2 is refuse.",
      ledger: "industry_denied · wallet seat\nCustody move and ATS match stay Room 2.\nWallet is not a seat.\nlive=false · live_pin_ok=false"
    },
    seventeen_a4: {
      message: "Refused. Not 17a-4. Not WORM. Immutable is consume-once, not a coin.",
      ledger: "industry_denied · 17a-4 WORM\nRoom 1 is books. Room 2 is refuse.\nNot a crypto ledger.\nlive=false · live_pin_ok=false"
    },
    room_2: {
      message: "Refused. Room 2 is refuse. Not a /crypto route.",
      ledger: "industry_denied · Room 2 spine\nRoom 1 walks to packs.\nRoom 2 stays refused.\nlive=false · live_pin_ok=false"
    },
    grc_product: {
      message: "Refused. Not a GRC product. Maps stay claimed=false.",
      ledger: "industry_denied · healthcare GRC\nMaps stay claimed=false.\nNot a live filing.\nlive=false · live_pin_ok=false"
    },
    cert_mill: {
      message: "Refused. Maps are not filings. Buying L1 is not a certificate.",
      ledger: "industry_denied · certificate mill\nMaps stay claimed=false.\nNot a SOX opinion.\nlive=false · live_pin_ok=false"
    },
    pack_sku: {
      message: "Refused. Packs, libraries, and repositories are not SKUs.",
      ledger: "industry_denied · packs as SKUs\nIncluded is not free. Upsell is not a fourth SKU.\nHours never mint a SKU.\nlive=false · live_pin_ok=false"
    },
    industry_route: {
      message: "Refused. The industry drawer sits on #industry. Not a /industry route.",
      ledger: "industry_denied · /industry route\nFirst glance stays the write rail.\nEncyclopedia stays a drawer.\nlive=false · live_pin_ok=false"
    },
    named_vertical: {
      message: "Refused. This plane cannot invent a named vertical as a fourth SKU.",
      ledger: "industry_denied · invent a named vertical\nSit is Dynamics BC treasury / controller.\nNot a GRC product.\nlive=false · live_pin_ok=false"
    },
    genius_close: {
      message: "Refused. GENIUS is a map. claimed=false. Not a close.",
      ledger: "industry_denied · GENIUS close\nMaps stay claimed=false.\nRoom 2 stays refuse.\nlive=false · live_pin_ok=false"
    },
    clarity_close: {
      message: "Refused. CLARITY is a map. claimed=false. Not a close.",
      ledger: "industry_denied · CLARITY close\nMaps stay claimed=false.\nNot a crypto product.\nlive=false · live_pin_ok=false"
    },
    dno_product: {
      message: "Refused. Not D&O. Not a penalty product. Fiduciary is why two humans bind.",
      ledger: "industry_denied · D&O product\nFiduciary is why two humans bind.\nNot a SOX opinion.\nlive=false · live_pin_ok=false"
    },
    governess_product: {
      message: "Refused. Not AI Governess. The product is Job C.",
      ledger: "industry_denied · AI Governess\nThe product is Job C.\nNot a fourth SKU.\nlive=false · live_pin_ok=false"
    },
    policy_sku: {
      message: "Refused. Company policy is not a SKU. Catalog is the doctrine.",
      ledger: "industry_denied · policy SKU\nCompany policy is not a SKU.\nCatalog is the doctrine.\nlive=false · live_pin_ok=false"
    },
    fear_first_glance: {
      message: "Refused. Fear is not the first glance. First glance stays the write rail.",
      ledger: "industry_denied · fear first glance\nFirst glance stays the write rail.\nFear management is refuse rehearsal.\nlive=false · live_pin_ok=false"
    }
  };

  function bindIndustryRoomRefuses(root) {
    if (!root || root.getAttribute("data-bound")) return;
    root.setAttribute("data-bound", "1");
    root.addEventListener("click", function (ev) {
      var btn = ev.target.closest("button[data-room-refuse], button.room-refuse");
      if (!btn || !root.contains(btn)) return;
      var id = btn.getAttribute("data-room-refuse") || "";
      var pack = ROOM_2_REFUSE[id] || {};
      var message = btn.getAttribute("data-refuse-text") || pack.message;
      if (!message) return;
      ev.preventDefault();
      refuseIndustry(
        btn,
        message,
        pack.ledger || ("industry_denied · " + id + "\nCatalog is the message.\nEvery refuse clicks.\nlive=false · live_pin_ok=false")
      );
    });
  }
  bindIndustryRoomRefuses(document.getElementById("industry-rooms"));
  bindIndustryRoomRefuses(document.getElementById("industry-room-spine"));
  bindIndustryRoomRefuses(document.getElementById("industry-day"));
  bindIndustryRoomRefuses(document.getElementById("industry-control"));

  var industryCertify = document.getElementById("industry-certify");
  if (industryCertify) {
    industryCertify.addEventListener("click", function () {
      refuseIndustry(
        industryCertify,
        "Refused. Maps stay claimed=false. Buying L1 is not a certificate. Not a live filing.",
        "industry_denied · certify maps\nDomestic and international maps stay claimed=false.\nNot a SOX opinion. Not D&O.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var industryPackSku = document.getElementById("industry-pack-sku");
  if (industryPackSku) {
    industryPackSku.addEventListener("click", function () {
      refuseIndustry(
        industryPackSku,
        "Refused. Packs, libraries, and repositories are not SKUs.",
        "industry_denied · packs as SKUs\nIncluded is not free. Upsell is not a fourth SKU.\nHours never mint a SKU.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var industryNamed = document.getElementById("industry-named-vertical");
  if (industryNamed) {
    industryNamed.addEventListener("click", function () {
      refuseIndustry(
        industryNamed,
        "Refused. This plane cannot invent a named vertical as a fourth SKU.",
        "industry_denied · invent a named vertical\nSit is Dynamics BC treasury / controller.\nNot a GRC product.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var industryRoute = document.getElementById("industry-route");
  if (industryRoute) {
    industryRoute.addEventListener("click", function () {
      refuseIndustry(
        industryRoute,
        "Refused. The industry drawer sits on #industry. Not a /industry route.",
        "industry_denied · /industry route\nFirst glance stays the write rail.\nEncyclopedia stays a drawer.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var industryToken = document.getElementById("industry-token-sku");
  if (industryToken) {
    industryToken.addEventListener("click", function () {
      refuseIndustry(
        industryToken,
        "Refused. Not a tokenization SKU. Not a stablecoin SKU. Not an RWA SKU. Not a crypto asset-management SKU. Room 2 is refuse.",
        "industry_denied · token SKU\nRoom 1 is books. Room 2 is refuse.\nNot a crypto product.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var industrySeventeen = document.getElementById("industry-seventeen-a4");
  if (industrySeventeen) {
    industrySeventeen.addEventListener("click", function () {
      refuseIndustry(
        industrySeventeen,
        "Refused. Not 17a-4. Not WORM. Immutable is consume-once, not a coin.",
        "industry_denied · 17a-4 WORM\nRoom 1 is books. Room 2 is refuse.\nNot a crypto ledger.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var industryGenius = document.getElementById("industry-genius-close");
  if (industryGenius) {
    industryGenius.addEventListener("click", function () {
      refuseIndustry(
        industryGenius,
        "Refused. GENIUS is a map. claimed=false. Not a close.",
        "industry_denied · GENIUS close\nMaps stay claimed=false.\nRoom 2 stays refuse.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var industryDno = document.getElementById("industry-dno");
  if (industryDno) {
    industryDno.addEventListener("click", function () {
      refuseIndustry(
        industryDno,
        "Refused. Not D&O. Not a penalty product. Fiduciary is why two humans bind.",
        "industry_denied · D&O product\nFiduciary is why two humans bind.\nNot a SOX opinion.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var industryGoverness = document.getElementById("industry-governess");
  if (industryGoverness) {
    industryGoverness.addEventListener("click", function () {
      refuseIndustry(
        industryGoverness,
        "Refused. Not AI Governess. The product is Job C.",
        "industry_denied · AI Governess\nThe product is Job C.\nNot a fourth SKU.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var industryFear = document.getElementById("industry-fear");
  if (industryFear) {
    industryFear.addEventListener("click", function () {
      refuseIndustry(
        industryFear,
        "Refused. Fear is not the first glance. First glance stays the write rail.",
        "industry_denied · fear first glance\nFirst glance stays the write rail.\nFear management is refuse rehearsal.\nlive=false · live_pin_ok=false"
      );
    });
  }

  var AGENT_REFUSE = {
    agent_as_seat: {
      message: "Refused. An agent is not a seat. Two humans bind.",
      ledger: "agent_denied · agent as seat\nAn agent is not a seat.\nTwo humans bind.\nlive=false · live_pin_ok=false"
    },
    agent365_as_product: {
      message: "Refused. Agent 365 is Microsoft's inventory plane. Not AINav.",
      ledger: "agent_denied · Agent 365 product\nAgent 365 inventories Microsoft agents.\nJob C admits the write.\nlive=false · live_pin_ok=false"
    },
    live_census: {
      message: "Refused. This plane cannot sign in. Inventory stays claimed=false.",
      ledger: "agent_denied · live census\nThis Cloud Agent cannot sign in.\nCensus stays claimed=false.\nlive=false · live_pin_ok=false"
    },
    pin_as_admit: {
      message: "Refused. A pinned agent is not dual admit.",
      ledger: "agent_denied · pin as admit\nA pin is visibility.\nNot dual admit.\nlive=false · live_pin_ok=false"
    },
    tools_as_sku: {
      message: "Refused. Agent Tools are not a SKU. Complements only.",
      ledger: "agent_denied · tools as SKU\nLeave five Available.\nComplements only.\nlive=false · live_pin_ok=false"
    },
    copilot_studio_as_job_c: {
      message: "Refused. Copilot Studio RFI is a human looked. Not Job C.",
      ledger: "agent_denied · Copilot Studio as Job C\nA human looked is not admit.\nWalk it like cheaper native.\nlive=false · live_pin_ok=false"
    }
  };

  function writeAgentLedger(text) {
    var node = document.getElementById("agent-ledger");
    if (!node) return;
    node.textContent = text;
  }

  function refuseAgent(button, message, ledger) {
    var refuse = document.getElementById("agent-refuse");
    if (refuse) {
      refuse.textContent = message;
      refuse.classList.add("is-live");
    }
    if (button) button.setAttribute("aria-pressed", "true");
    writeAgentLedger(ledger);
  }

  function bindAgentRefuses(root) {
    if (!root || root.getAttribute("data-bound")) return;
    root.setAttribute("data-bound", "1");
    root.addEventListener("click", function (ev) {
      var btn = ev.target.closest("button[data-agent-refuse], button.room-refuse");
      if (!btn || !root.contains(btn)) return;
      var id = btn.getAttribute("data-agent-refuse") || "";
      var pack = AGENT_REFUSE[id] || {};
      var message = btn.getAttribute("data-refuse-text") || pack.message;
      if (!message) return;
      ev.preventDefault();
      refuseAgent(
        btn,
        message,
        pack.ledger || ("agent_denied · " + id + "\nAn agent is not a seat.\nCensus stays claimed=false.\nlive=false · live_pin_ok=false")
      );
    });
  }
  bindAgentRefuses(document.getElementById("agents-board"));

  function bindAgentConsole(id, key) {
    var btn = document.getElementById(id);
    if (!btn) return;
    btn.addEventListener("click", function () {
      var pack = AGENT_REFUSE[key] || {};
      refuseAgent(btn, pack.message, pack.ledger);
    });
  }
  bindAgentConsole("agent-census-btn", "live_census");
  bindAgentConsole("agent-365-btn", "agent365_as_product");
  bindAgentConsole("agent-seat-btn", "agent_as_seat");
  bindAgentConsole("agent-pin-btn", "pin_as_admit");

  fetch("agents.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data) return;
      if (data.live || data.inventory_claimed || data.agent_365_is_product || data.is_admit_plane) return;
      var status = document.getElementById("agent-tools-status");
      if (status) {
        status.textContent =
          "honest=true · inventory_claimed=false · agent_365_is_product=false · cloud_agent_can_approve=false · live=false";
      }
    })
    .catch(function () {});

  var ACCESS_REFUSE = {
    ask_admin: {
      message: "Refused. This plane does not need Microsoft admin. James clicks.",
      ledger: "access_denied · Microsoft admin\nThis plane does not need additional access.\nJames clicks.\nlive=false · live_pin_ok=false"
    },
    grok_as_seat: {
      message: "Refused. Grok Build is not a seat. Two humans bind.",
      ledger: "access_denied · Grok Build as a seat\nGrok Build is not a seat.\nTwo humans bind.\nlive=false · live_pin_ok=false"
    },
    grok_as_product: {
      message: "Refused. Grok Build is an operator map. Not AINav.",
      ledger: "access_denied · Grok Build as the product\nGrok Build is an operator map.\nNot AINav.\nlive=false · live_pin_ok=false"
    },
    bot_as_admit: {
      message: "Refused. A Grok bot is not dual admit.",
      ledger: "access_denied · Grok bot as dual admit\nA Grok bot is not dual admit.\nJob C stays two humans.\nlive=false · live_pin_ok=false"
    },
    more_access_as_admit: {
      message: "Refused. More access is not admit.",
      ledger: "access_denied · additional access as admit\nThis plane does not need additional access.\nMore access is not admit.\nlive=false · live_pin_ok=false"
    }
  };

  function writeAccessLedger(text) {
    var node = document.getElementById("access-ledger");
    if (!node) return;
    node.textContent = text;
  }

  function refuseAccess(button, message, ledger) {
    var refuse = document.getElementById("access-refuse");
    if (refuse) {
      refuse.textContent = message;
      refuse.classList.add("is-live");
    }
    if (button) button.setAttribute("aria-pressed", "true");
    writeAccessLedger(ledger);
  }

  function bindAccessRefuses(root) {
    if (!root || root.getAttribute("data-bound")) return;
    root.setAttribute("data-bound", "1");
    root.addEventListener("click", function (ev) {
      var btn = ev.target.closest("button[data-access-refuse], button.room-refuse");
      if (!btn || !root.contains(btn)) return;
      var id = btn.getAttribute("data-access-refuse") || "";
      var pack = ACCESS_REFUSE[id] || {};
      var message = btn.getAttribute("data-refuse-text") || pack.message;
      if (!message) return;
      ev.preventDefault();
      refuseAccess(
        btn,
        message,
        pack.ledger || ("access_denied · " + id + "\nThis plane does not need additional access.\nGrok Build is not a seat.\nlive=false · live_pin_ok=false")
      );
    });
  }
  bindAccessRefuses(document.getElementById("access-board"));

  function bindAccessConsole(id, key) {
    var btn = document.getElementById(id);
    if (!btn) return;
    btn.addEventListener("click", function () {
      var pack = ACCESS_REFUSE[key] || {};
      refuseAccess(btn, pack.message, pack.ledger);
    });
  }
  bindAccessConsole("access-need-more-btn", "more_access_as_admit");
  bindAccessConsole("access-grok-seat-btn", "grok_as_seat");
  bindAccessConsole("access-grok-product-btn", "grok_as_product");
  bindAccessConsole("access-admin-btn", "ask_admin");

  fetch("access.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data) return;
      if (data.live || data.need_more || data.grok_is_product || data.is_admit_plane) return;
      var status = document.getElementById("access-status");
      if (status) {
        status.textContent =
          "honest=true · need_more=false · grok_is_product=false · grok_is_seat=false · live=false";
      }
    })
    .catch(function () {});

  var OPERATOR_REFUSE = {
    swap_operator: {
      message: "Refused. Cursor stays the recorded operator.",
      ledger: "operator_denied · swap\nCursor stays recorded.\nGrok Build stays mapped.\nlive=false · live_pin_ok=false"
    },
    grok_as_recorded: {
      message: "Refused. Grok Build is mapped. Not this recorded operator.",
      ledger: "operator_denied · Grok as recorded\nGrok Build is mapped.\nNot this recorded operator.\nlive=false · live_pin_ok=false"
    },
    bot_as_operator: {
      message: "Refused. A Grok bot is not the operator. Not dual admit.",
      ledger: "operator_denied · Grok bot as operator\nA Grok bot is not the operator.\nNot dual admit.\nlive=false · live_pin_ok=false"
    }
  };

  function writeOperatorLedger(text) {
    var node = document.getElementById("operator-ledger");
    if (!node) return;
    node.textContent = text;
  }

  function refuseOperator(button, message, ledger) {
    var refuse = document.getElementById("operator-refuse");
    if (refuse) {
      refuse.textContent = message;
      refuse.classList.add("is-live");
    }
    if (button) button.setAttribute("aria-pressed", "true");
    writeOperatorLedger(ledger);
  }

  function bindOperatorRefuses(root) {
    if (!root || root.getAttribute("data-bound")) return;
    root.setAttribute("data-bound", "1");
    root.addEventListener("click", function (ev) {
      var btn = ev.target.closest("button[data-operator-refuse]");
      if (!btn || !root.contains(btn)) return;
      var id = btn.getAttribute("data-operator-refuse") || "";
      var pack = OPERATOR_REFUSE[id] || {};
      var message = btn.getAttribute("data-refuse-text") || pack.message;
      if (!message) return;
      ev.preventDefault();
      refuseOperator(
        btn,
        message,
        pack.ledger || ("operator_denied · " + id + "\nCursor stays recorded.\nGrok Build stays mapped.\nlive=false · live_pin_ok=false")
      );
    });
  }
  bindOperatorRefuses(document.getElementById("agent-tools"));

  fetch("operators.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data) return;
      if (data.live || data.swap || data.grok_is_recorded || data.is_admit_plane) return;
      var status = document.getElementById("operator-status");
      if (status) {
        status.textContent =
          "honest=true · swap=false · grok_is_recorded=false · bot_is_operator=false · live=false";
      }
    })
    .catch(function () {});

  var BUILD_REFUSE = {
    full_access_as_admit: {
      message: "Refused. Full access is not admit.",
      ledger: "build_denied · full access\nThis plane does not need full access.\nFull access is not admit.\nlive=false · live_pin_ok=false"
    },
    more_secrets_as_build: {
      message: "Refused. More secrets are not how we build.",
      ledger: "build_denied · more secrets\nMore secrets are not how we build.\nThe twin is enough.\nlive=false · live_pin_ok=false"
    },
    twin_as_launch: {
      message: "Refused. The twin is not launch.",
      ledger: "build_denied · twin as launch\nThe twin is not launch.\nJames says launch.\nlive=false · live_pin_ok=false"
    },
    pack_as_sku: {
      message: "Refused. Packs, modules, and repositories are not SKUs.",
      ledger: "build_denied · pack as SKU\nPacks, modules, and repositories are not SKUs.\nThree SKUs only.\nlive=false · live_pin_ok=false"
    }
  };

  function writeBuildLedger(text) {
    var node = document.getElementById("build-ledger");
    if (!node) return;
    node.textContent = text;
  }

  function refuseBuild(button, message, ledger) {
    var refuse = document.getElementById("build-refuse");
    if (refuse) {
      refuse.textContent = message;
      refuse.classList.add("is-live");
    }
    if (button) button.setAttribute("aria-pressed", "true");
    writeBuildLedger(ledger);
  }

  function bindBuildRefuses(root) {
    if (!root || root.getAttribute("data-build-bound")) return;
    root.setAttribute("data-build-bound", "1");
    root.addEventListener("click", function (ev) {
      var btn = ev.target.closest("button[data-build-refuse]");
      if (!btn || !root.contains(btn)) return;
      var id = btn.getAttribute("data-build-refuse") || "";
      var pack = BUILD_REFUSE[id] || {};
      var message = btn.getAttribute("data-refuse-text") || pack.message;
      if (!message) return;
      ev.preventDefault();
      refuseBuild(
        btn,
        message,
        pack.ledger || ("build_denied · " + id + "\nThis plane does not need full access.\nThe twin is not launch.\nlive=false · live_pin_ok=false")
      );
    });
  }
  bindBuildRefuses(document.getElementById("agent-tools"));

  fetch("build.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data) return;
      if (data.live || data.need_full || data.twin_is_launch || data.is_admit_plane) return;
      var status = document.getElementById("build-status");
      if (status) {
        status.textContent =
          "honest=true · need_full=false · twin_is_launch=false · packs_are_skus=false · live=false";
      }
    })
    .catch(function () {});

  var READY_REFUSE = {
    gold_as_launch: {
      message: "Refused. Gold is not launch.",
      ledger: "ready_denied · gold as launch\nGold is not launch.\nTwin certified is not launch day.\nlive=false · live_pin_ok=false"
    },
    twin_as_launch_day: {
      message: "Refused. Twin certified is not launch day.",
      ledger: "ready_denied · twin as launch day\nTwin certified is not launch day.\nJames says launch.\nlive=false · live_pin_ok=false"
    },
    sim_as_production: {
      message: "Refused. Simulation is not production.",
      ledger: "ready_denied · simulation as production\nSimulation is not production.\nThe twin stays a twin.\nlive=false · live_pin_ok=false"
    },
    update_as_live_pin: {
      message: "Refused. An update is not LIVE_PIN_OK.",
      ledger: "ready_denied · update as live pin\nAn update is not LIVE_PIN_OK.\nRegen is not launch.\nlive=false · live_pin_ok=false"
    },
    close_owner_from_plane: {
      message: "Refused. Owner gaps stay owner-only.",
      ledger: "ready_denied · close owner from plane\nOwner gaps stay owner-only.\nSeat B stays James.\nlive=false · live_pin_ok=false"
    }
  };

  function writeReadyLedger(text) {
    var node = document.getElementById("ready-ledger");
    if (!node) return;
    node.textContent = text;
  }

  function refuseReady(button, message, ledger) {
    var refuse = document.getElementById("ready-refuse");
    if (refuse) {
      refuse.textContent = message;
      refuse.classList.add("is-live");
    }
    if (button) button.setAttribute("aria-pressed", "true");
    writeReadyLedger(ledger);
  }

  function bindReadyRefuses(root) {
    if (!root || root.getAttribute("data-ready-bound")) return;
    root.setAttribute("data-ready-bound", "1");
    root.addEventListener("click", function (ev) {
      var btn = ev.target.closest("button[data-ready-refuse]");
      if (!btn || !root.contains(btn)) return;
      var id = btn.getAttribute("data-ready-refuse") || "";
      var pack = READY_REFUSE[id] || {};
      var message = btn.getAttribute("data-refuse-text") || pack.message;
      if (!message) return;
      ev.preventDefault();
      refuseReady(
        btn,
        message,
        pack.ledger || ("ready_denied · " + id + "\nGold is not launch.\nTwin certified is not launch day.\nlive=false · live_pin_ok=false")
      );
    });
  }
  bindReadyRefuses(document.getElementById("agent-tools"));

  fetch("ready.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data) return;
      if (data.live || data.gold_is_launch || data.twin_is_launch_day || data.is_admit_plane || data.launch_day_certified) return;
      var status = document.getElementById("ready-status");
      if (status) {
        status.textContent =
          "honest=true · gold_is_launch=false · twin_is_launch_day=false · launch_day_certified=false · live=false";
      }
    })
    .catch(function () {});

  var INDUSTRY_REFUSE = {
    industry_pack_as_sku: {
      message: "Refused. Packs are not SKUs.",
      ledger: "industry_denied · pack as sku\nPacks are not SKUs.\nIndustry certify is not launch.\nlive=false · live_pin_ok=false"
    },
    industry_lib_as_sku: {
      message: "Refused. Libraries are not SKUs.",
      ledger: "industry_denied · library as sku\nLibraries are not SKUs.\nIndustry certify is not launch.\nlive=false · live_pin_ok=false"
    },
    industry_repo_as_sku: {
      message: "Refused. Repositories are not SKUs.",
      ledger: "industry_denied · repository as sku\nRepositories are not SKUs.\nIndustry certify is not launch.\nlive=false · live_pin_ok=false"
    },
    named_vertical_as_sku: {
      message: "Refused. A named vertical is not a SKU.",
      ledger: "industry_denied · named vertical as sku\nA named vertical is not a SKU.\nIndustry certify is not launch.\nlive=false · live_pin_ok=false"
    },
    industry_certify_as_launch: {
      message: "Refused. Industry certify is not launch.",
      ledger: "industry_denied · industry certify as launch\nIndustry certify is not launch.\nJames says launch.\nlive=false · live_pin_ok=false"
    }
  };

  function writeIndustryLedger(text) {
    var node = document.getElementById("industry-cert-ledger");
    if (!node) return;
    node.textContent = text;
  }

  function refuseIndustry(button, message, ledger) {
    var refuse = document.getElementById("industry-cert-refuse");
    if (refuse) {
      refuse.textContent = message;
      refuse.classList.add("is-live");
    }
    if (button) button.setAttribute("aria-pressed", "true");
    writeIndustryLedger(ledger);
  }

  function bindIndustryRefuses(root) {
    if (!root || root.getAttribute("data-industry-bound")) return;
    root.setAttribute("data-industry-bound", "1");
    root.addEventListener("click", function (ev) {
      var btn = ev.target.closest("button[data-industry-refuse]");
      if (!btn || !root.contains(btn)) return;
      var id = btn.getAttribute("data-industry-refuse") || "";
      var pack = INDUSTRY_REFUSE[id] || {};
      var message = btn.getAttribute("data-refuse-text") || pack.message;
      if (!message) return;
      ev.preventDefault();
      refuseIndustry(
        btn,
        message,
        pack.ledger || ("industry_denied · " + id + "\nPacks are not SKUs.\nIndustry certify is not launch.\nlive=false · live_pin_ok=false")
      );
    });
  }
  bindIndustryRefuses(document.getElementById("packs"));

  fetch("industry.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data) return;
      if (data.live || data.packs_are_skus || data.industry_certified_launch || data.is_admit_plane || data.certified) return;
      var status = document.getElementById("industry-cert-status");
      if (status) {
        status.textContent =
          "honest=true · packs_are_skus=false · industry_certified_launch=false · certified=false · live=false";
      }
    })
    .catch(function () {});

  var WHOLE_REFUSE = {
    whole_as_launch: {
      message: "Refused. The whole firm is not launch.",
      ledger: "whole_denied · whole as launch\nThe whole firm is not launch.\nA 10/10 review is not launch.\nlive=false · live_pin_ok=false"
    },
    ten_as_launch: {
      message: "Refused. A 10/10 review is not launch.",
      ledger: "whole_denied · 10/10 as launch\nA 10/10 review is not launch.\nThe whole firm is not launch.\nlive=false · live_pin_ok=false"
    },
    stitch_as_sku: {
      message: "Refused. The stitch is not a SKU.",
      ledger: "whole_denied · stitch as sku\nThe stitch is not a SKU.\nThe whole firm is not launch.\nlive=false · live_pin_ok=false"
    },
    website_as_apex: {
      message: "Refused. The twin is not the Institute apex.",
      ledger: "whole_denied · twin as apex\nThe twin is not the Institute apex.\nThe whole firm is not launch.\nlive=false · live_pin_ok=false"
    },
    ci_as_launch: {
      message: "Refused. A green check is not launch.",
      ledger: "whole_denied · green check as launch\nA green check is not launch.\nThe whole firm is not launch.\nlive=false · live_pin_ok=false"
    }
  };

  function writeWholeLedger(text) {
    var node = document.getElementById("whole-ledger");
    if (!node) return;
    node.textContent = text;
  }

  function refuseWhole(button, message, ledger) {
    var refuse = document.getElementById("whole-refuse");
    if (refuse) {
      refuse.textContent = message;
      refuse.classList.add("is-live");
    }
    if (button) button.setAttribute("aria-pressed", "true");
    writeWholeLedger(ledger);
  }

  function bindWholeRefuses(root) {
    if (!root || root.getAttribute("data-whole-bound")) return;
    root.setAttribute("data-whole-bound", "1");
    root.addEventListener("click", function (ev) {
      var btn = ev.target.closest("button[data-whole-refuse]");
      if (!btn || !root.contains(btn)) return;
      var id = btn.getAttribute("data-whole-refuse") || "";
      var pack = WHOLE_REFUSE[id] || {};
      var message = btn.getAttribute("data-refuse-text") || pack.message;
      if (!message) return;
      ev.preventDefault();
      refuseWhole(
        btn,
        message,
        pack.ledger || ("whole_denied · " + id + "\nThe whole firm is not launch.\nA 10/10 review is not launch.\nlive=false · live_pin_ok=false")
      );
    });
  }
  bindWholeRefuses(document.getElementById("whole"));

  var PAGES_REFUSE = {
    power_pages_as_host: {
      message: "Refused. Power Pages is not the Institute host.",
      ledger: "pages_denied · power pages as host\nPower Pages is not the Institute host.\nComplements stay eight.\nlive=false · live_pin_ok=false"
    },
    power_pages_as_sku: {
      message: "Refused. Power Pages is not a SKU.",
      ledger: "pages_denied · power pages as sku\nPower Pages is not a SKU.\nPower Pages is not the Institute host.\nlive=false · live_pin_ok=false"
    },
    power_pages_as_cms: {
      message: "Refused. Power Pages is not the CMS.",
      ledger: "pages_denied · power pages as cms\nPower Pages is not the CMS.\nAzure SWA stays the host.\nlive=false · live_pin_ok=false"
    },
    power_pages_as_apex: {
      message: "Refused. Power Pages is not the Institute apex.",
      ledger: "pages_denied · power pages as apex\nPower Pages is not the Institute apex.\nCloudflare apex stays empty.\nlive=false · live_pin_ok=false"
    },
    power_pages_as_dataverse_close: {
      message: "Refused. Power Pages does not close US Dataverse.",
      ledger: "pages_denied · power pages as dataverse close\nPower Pages does not close US Dataverse.\nCanada is not United States.\nlive=false · live_pin_ok=false"
    }
  };

  function writePagesLedger(text) {
    var node = document.getElementById("pages-ledger");
    if (!node) return;
    node.textContent = text;
  }

  function refusePages(button, message, ledger) {
    var refuse = document.getElementById("pages-refuse");
    if (refuse) {
      refuse.textContent = message;
      refuse.classList.add("is-live");
    }
    if (button) button.setAttribute("aria-pressed", "true");
    writePagesLedger(ledger);
  }

  function bindPagesRefuses(root) {
    if (!root || root.getAttribute("data-pages-bound")) return;
    root.setAttribute("data-pages-bound", "1");
    root.addEventListener("click", function (ev) {
      var btn = ev.target.closest("button[data-pages-refuse]");
      if (!btn || !root.contains(btn)) return;
      var id = btn.getAttribute("data-pages-refuse") || "";
      var pack = PAGES_REFUSE[id] || {};
      var message = btn.getAttribute("data-refuse-text") || pack.message;
      if (!message) return;
      ev.preventDefault();
      refusePages(
        btn,
        message,
        pack.ledger || ("pages_denied · " + id + "\nPower Pages is not the Institute host.\nlive=false · live_pin_ok=false")
      );
    });
  }
  bindPagesRefuses(document.getElementById("pages-consider"));

  var STUDIO_REFUSE = {
    studio_as_job_c: {
      message: "Refused. Copilot Studio is not Job C.",
      ledger: "studio_denied · copilot studio as job c\nCopilot Studio is not Job C.\nA human looked is not dual admit.\nlive=false · live_pin_ok=false"
    },
    studio_as_sku: {
      message: "Refused. Copilot Studio is not a SKU.",
      ledger: "studio_denied · copilot studio as sku\nCopilot Studio is not a SKU.\nL1, P-ADM, U-DUAL only.\nlive=false · live_pin_ok=false"
    },
    studio_as_admit: {
      message: "Refused. Copilot Studio is not the admit plane.",
      ledger: "studio_denied · copilot studio as admit\nCopilot Studio is not the admit plane.\nTwo humans. One hash. Then the write.\nlive=false · live_pin_ok=false"
    },
    studio_as_complement: {
      message: "Refused. Copilot Studio is not a complement.",
      ledger: "studio_denied · copilot studio as complement\nCopilot Studio is not a complement.\nComplements stay eight.\nlive=false · live_pin_ok=false"
    },
    studio_as_seat: {
      message: "Refused. Copilot Studio RFI is not seat B.",
      ledger: "studio_denied · copilot studio as seat b\nCopilot Studio RFI is not seat B.\nMailbox is not a click.\nlive=false · live_pin_ok=false"
    }
  };

  function writeStudioLedger(text) {
    var node = document.getElementById("studio-ledger");
    if (!node) return;
    node.textContent = text;
  }

  function refuseStudio(button, message, ledger) {
    var refuse = document.getElementById("studio-refuse");
    if (refuse) {
      refuse.textContent = message;
      refuse.classList.add("is-live");
    }
    if (button) button.setAttribute("aria-pressed", "true");
    writeStudioLedger(ledger);
  }

  function bindStudioRefuses(root) {
    if (!root || root.getAttribute("data-studio-bound")) return;
    root.setAttribute("data-studio-bound", "1");
    root.addEventListener("click", function (ev) {
      var btn = ev.target.closest("button[data-studio-refuse]");
      if (!btn || !root.contains(btn)) return;
      var id = btn.getAttribute("data-studio-refuse") || "";
      var pack = STUDIO_REFUSE[id] || {};
      var message = btn.getAttribute("data-refuse-text") || pack.message;
      if (!message) return;
      ev.preventDefault();
      refuseStudio(
        btn,
        message,
        pack.ledger || ("studio_denied · " + id + "\nCopilot Studio is not Job C.\nlive=false · live_pin_ok=false")
      );
    });
  }
  bindStudioRefuses(document.getElementById("studio-consider"));

  var CONNECT_REFUSE = {
    connected_as_live: {
      message: "Refused. Connected is not live.",
      ledger: "connect_denied · connected as live\nConnected is not live.\nRead-only is not LIVE_PIN_OK.\nlive=false · live_pin_ok=false"
    },
    licensed_as_wired: {
      message: "Refused. Licensed is not wired.",
      ledger: "connect_denied · licensed as wired\nLicensed is not wired.\nA SKU is not a connection.\nlive=false · live_pin_ok=false"
    },
    available_as_seat: {
      message: "Refused. Available is not a seat.",
      ledger: "connect_denied · available as a seat\nAvailable is not a seat.\nTools are not seats.\nlive=false · live_pin_ok=false"
    },
    graph_read_as_live_pin: {
      message: "Refused. A Graph read is not LIVE_PIN_OK.",
      ledger: "connect_denied · graph read as live pin\nA Graph read is not LIVE_PIN_OK.\nFour Reads are not launch.\nlive=false · live_pin_ok=false"
    },
    cursor_app_as_seat: {
      message: "Refused. A Cursor app is not a seat.",
      ledger: "connect_denied · cursor app as a seat\nA Cursor app is not a seat.\nAzure MCP ready is not authorized.\nlive=false · live_pin_ok=false"
    }
  };

  function writeConnectLedger(text) {
    var node = document.getElementById("connect-ledger");
    if (!node) return;
    node.textContent = text;
  }

  function refuseConnect(button, message, ledger) {
    var refuse = document.getElementById("connect-refuse");
    if (refuse) {
      refuse.textContent = message;
      refuse.classList.add("is-live");
    }
    if (button) button.setAttribute("aria-pressed", "true");
    writeConnectLedger(ledger);
  }

  function bindConnectRefuses(root) {
    if (!root || root.getAttribute("data-connect-bound")) return;
    root.setAttribute("data-connect-bound", "1");
    root.addEventListener("click", function (ev) {
      var btn = ev.target.closest("button[data-connect-refuse]");
      if (!btn || !root.contains(btn)) return;
      var id = btn.getAttribute("data-connect-refuse") || "";
      var pack = CONNECT_REFUSE[id] || {};
      var message = btn.getAttribute("data-refuse-text") || pack.message;
      if (!message) return;
      ev.preventDefault();
      refuseConnect(
        btn,
        message,
        pack.ledger || ("connect_denied · " + id + "\nConnected is not live.\nlive=false · live_pin_ok=false")
      );
    });
  }
  bindConnectRefuses(document.getElementById("connect-consider"));

  var OPERATE_REFUSE = {
    close_gaps_as_this_plane: {
      message: "Refused. Closing all gaps is not this plane.",
      ledger: "operate_denied · closing all gaps as this plane\nClosing all gaps is not this plane.\nSeat B click stays owner-only.\nlive=false · live_pin_ok=false"
    },
    outlook_as_click: {
      message: "Refused. Outlook mail is not a click.",
      ledger: "operate_denied · outlook mail as a click\nOutlook mail is not a click.\nMailbox is not seat B.\nlive=false · live_pin_ok=false"
    },
    grok_login_as_this_plane: {
      message: "Refused. grok login is not this plane.",
      ledger: "operate_denied · grok login as this plane\ngrok login is not this plane.\nGrok Build stays mapped.\nlive=false · live_pin_ok=false"
    },
    operate_sim_as_production: {
      message: "Refused. An operate sim is not production.",
      ledger: "operate_denied · operate sim as production\nAn operate sim is not production.\nLab oids are not named seats.\nlive=false · live_pin_ok=false"
    },
    polish_ten_as_launch: {
      message: "Refused. A 10/10 polish is not launch.",
      ledger: "operate_denied · 10/10 polish as launch\nA 10/10 polish is not launch.\nOwner says launch.\nlive=false · live_pin_ok=false"
    }
  };

  function writeOperateLedger(text) {
    var node = document.getElementById("operate-ledger");
    if (!node) return;
    node.textContent = text;
  }

  function refuseOperate(button, message, ledger) {
    var refuse = document.getElementById("operate-refuse");
    if (refuse) {
      refuse.textContent = message;
      refuse.classList.add("is-live");
    }
    if (button) button.setAttribute("aria-pressed", "true");
    writeOperateLedger(ledger);
  }

  function bindOperateRefuses(root) {
    if (!root || root.getAttribute("data-operate-bound")) return;
    root.setAttribute("data-operate-bound", "1");
    root.addEventListener("click", function (ev) {
      var btn = ev.target.closest("button[data-operate-refuse]");
      if (!btn || !root.contains(btn)) return;
      var id = btn.getAttribute("data-operate-refuse") || "";
      var pack = OPERATE_REFUSE[id] || {};
      var message = btn.getAttribute("data-refuse-text") || pack.message;
      if (!message) return;
      ev.preventDefault();
      refuseOperate(
        btn,
        message,
        pack.ledger || ("operate_denied · " + id + "\nClosing all gaps is not this plane.\nlive=false · live_pin_ok=false")
      );
    });
  }
  bindOperateRefuses(document.getElementById("operate-consider"));

  fetch("connect.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data) return;
      if (data.live || data.connected_is_live || data.licensed_is_wired || data.available_is_seat || data.certified) return;
      var status = document.getElementById("connect-status");
      if (status) {
        status.textContent =
          "honest=true · recorded=true · connected_is_live=false · licensed_is_wired=false · available_is_seat=false · live=false";
      }
    })
    .catch(function () {});

  fetch("operate.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data) return;
      if (data.live || data.close_gaps_is_this_plane || data.outlook_is_click || data.grok_login_is_this_plane || data.operate_sim_is_production || data.polish_ten_is_launch || data.certified) return;
      var status = document.getElementById("operate-status");
      if (status) {
        status.textContent =
          "honest=true · recorded=true · close_gaps_is_this_plane=false · outlook_is_click=false · grok_login_is_this_plane=false · live=false";
      }
    })
    .catch(function () {});

  fetch("studio.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data) return;
      if (data.live || data.is_job_c || data.is_sku || data.is_admit_plane || data.certified) return;
      var status = document.getElementById("studio-status");
      if (status) {
        status.textContent =
          "honest=true · considered=true · is_job_c=false · is_sku=false · is_admit_plane=false · live=false";
      }
    })
    .catch(function () {});

  fetch("pages.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data) return;
      if (data.live || data.is_host || data.is_sku || data.cms || data.certified) return;
      var status = document.getElementById("pages-status");
      if (status) {
        status.textContent =
          "honest=true · considered=true · is_host=false · is_sku=false · cms=false · live=false";
      }
    })
    .catch(function () {});

  fetch("whole.json")
    .then(function (res) {
      return res.ok ? res.json() : null;
    })
    .then(function (data) {
      if (!data) return;
      if (data.live || data.whole_is_launch || data.ten_is_launch || data.stitch_is_sku || data.certified) return;
      var status = document.getElementById("whole-status");
      if (status) {
        status.textContent =
          "honest=true · whole_is_launch=false · ten_is_launch=false · stitch_is_sku=false · live=false";
      }
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
})();
