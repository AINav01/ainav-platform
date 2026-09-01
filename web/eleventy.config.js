module.exports = function (eleventyConfig) {
  return {
    dir: {
      input: "eleventy",
      output: "../institute/compiled",
    },
    pathPrefix: "/compiled/",
  };
};
