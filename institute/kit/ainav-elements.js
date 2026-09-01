(function () {
  "use strict";

  class AinavRail extends HTMLElement {
    connectedCallback() {
      if (this.getAttribute("data-ready") === "true") return;
      this.setAttribute("data-ready", "true");
      if (!this.querySelector("ol")) {
        this.innerHTML =
          '<ol class="write-rail" aria-label="Job C write path">' +
          '<li data-step="seat_a"><b>Seat A</b><span>Treasury admits</span></li>' +
          '<li data-step="seat_b"><b>Seat B</b><span>Controller admits</span></li>' +
          '<li data-step="hash"><b>One hash</b><span>Consume once</span></li>' +
          '<li data-step="write"><b>Then the write</b><span>Fail-closed SoR</span></li>' +
          "</ol>";
      }
    }
  }

  class AinavHonest extends HTMLElement {
    connectedCallback() {
      if (this.getAttribute("data-ready") === "true") return;
      this.setAttribute("data-ready", "true");
      if (!this.querySelector("article")) {
        this.innerHTML =
          '<article><h2>Not a priced round</h2><p>Recognized revenue $0. Named customers 0. Signed L1 0.</p></article>' +
          '<article><h2>Not a claimed program</h2><p>Startups first. Inception second. Qualify, not claimed.</p></article>' +
          '<article><h2>Not LIVE_PIN_OK</h2><p>Identify is not admit. The Cloud Agent is not a seat.</p></article>';
      }
    }
  }

  if (!customElements.get("ainav-rail")) customElements.define("ainav-rail", AinavRail);
  if (!customElements.get("ainav-honest")) customElements.define("ainav-honest", AinavHonest);
})();
