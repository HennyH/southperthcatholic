module.exports = function(config) {

    config.addPassthroughCopy("./src/favicon.ico");
    config.addPassthroughCopy("./src/site.js");
    config.addPassthroughCopy("./src/style.css");
    config.addPassthroughCopy("./assets/**");

    return {
        dir: {
            input: "src",
            output: "docs"
        }
    }
}