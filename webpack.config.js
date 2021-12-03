const path = require("path");

module.exports = {
  entry: "./js/icons.js",
  output: {
    filename: "icons.js",
    path: path.resolve(__dirname, "./static")
  }
};
