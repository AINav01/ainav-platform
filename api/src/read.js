"use strict";

function readCatalog(request) {
  const method = String(request.method || "GET").toUpperCase();
  if (method !== "GET") {
    return {
      status: 405,
      jsonBody: {
        kind: "ainav.institute.api.v1",
        ok: false,
        writes_sor: false,
        reason_code: "API_READ_ONLY",
        note: "The Institute Function is read-only. It cannot write a SoR, invent a seat, or mark LIVE_PIN_OK.",
      },
    };
  }
  return {
    status: 200,
    jsonBody: {
      kind: "ainav.institute.api.v1",
      ok: true,
      writes_sor: false,
      cms: false,
      live: false,
      live_pin_ok: false,
      auth_is_admit: false,
      hrefs: {
        kit: "/kit.json",
        schema: "/schema.json",
        search: "/search.json",
        programs: "/programs.json",
        investor: "/investor.json",
        business: "/plane-business.json",
        finance: "/finance.json",
        floor: "/control-plane.json",
      },
      note: "Read catalog JSON from the static host. This Function is not Job C.",
    },
  };
}

module.exports = { readCatalog };
