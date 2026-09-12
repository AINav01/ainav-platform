module.exports = {
  ci: {
    collect: {
      url: [
        "http://127.0.0.1:8765/app.html",
        "http://127.0.0.1:8765/kit.html",
        "http://127.0.0.1:8765/index.html",
      ],
      startServerCommand: "python3 -m http.server 8765 --directory ../institute",
      numberOfRuns: 1,
    },
    assert: {
      assertions: {
        "categories:performance": ["warn", { minScore: 0.8 }],
        "categories:accessibility": ["error", { minScore: 0.9 }],
      },
    },
    upload: {
      target: "filesystem",
      outputDir: ".lighthouseci",
    },
  },
};
