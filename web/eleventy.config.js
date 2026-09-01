module.exports = function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy({ "../institute/styles.css": "styles.css" });
  return {
    dir: {
      input: "eleventy",
      output: "../institute/compiled",
    },
    pathPrefix: "/compiled/",
  };
};
