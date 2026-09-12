const { app } = require("@azure/functions");
const { readCatalog } = require("./read");

app.http("read", {
  methods: ["GET", "POST", "PUT", "PATCH", "DELETE"],
  authLevel: "anonymous",
  route: "read",
  handler: readCatalog,
});
