const path = require('path');
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  mode: "development", // "production" | "development" | "none"  // Chosen mode tells webpack to use its built-in optimizations accordingly.
  context: __dirname, // string (absolute path!)
  // the home directory for webpack
  // the entry and module.rules.loader option
  //   is resolved relative to this directory
  entry: {
      "chat-app": "./src/chat-app.js", // string | object | array  // defaults to ./src
  },
  // Here the application starts executing
  // and webpack starts bundling
  output: {
    // options related to how webpack emits results
    path: path.resolve(__dirname, "../static/chat/frontend"), // string
    // the target directory for all output files
    // must be an absolute path (use the Node.js path module)
    filename: "[name].js", // string    // the filename template for entry chunks
 },
 plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
  ],
  module: {
    // configuration regarding modules
    rules: [
      // rules for modules (configure loaders, parser options, etc.)
      {
        test: /\.jsx?$/,
        use: ['babel-loader'],
        // these are matching conditions, each accepting a regular expression or string
        // test and include have the same behavior, both must be matched
        exclude: '/node_modules/'
        // exclude must not be matched (takes preference over test and include)
        // Best practices:
        // - Use RegExp only in test and for filename matching
        // - Use arrays of absolute paths in include and exclude
        // - Try to avoid exclude and prefer include
       
      },
      {
        test: /\.css$/,
        exclude: '/node_modules/',
        use: [ 'style-loader', 'css-loader' ]
      }
    ]
},
  resolve: {

    // directories where to look for modules
    extensions: [".js", "*", ".jsx", ".css"],
    // extensions that are used
 },
}