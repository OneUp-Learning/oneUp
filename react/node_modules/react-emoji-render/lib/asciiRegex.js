"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});

exports.default = function () {
  return new RegExp("(" + edgeCases + ")?(" + names + ")((?!(" + edgeCases + "))[a-z0-9_\\-\\+]+:)?", "g");
};

var _asciiAliases = require("../data/asciiAliases");

var _asciiAliases2 = _interopRequireDefault(_asciiAliases);

var _lodash = require("lodash.flatten");

var _lodash2 = _interopRequireDefault(_lodash);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function quoteRE(str) {
  return str.replace(/[.?*+^$[\]\\(){}|-]/g, "\\$&");
}

var names = (0, _lodash2.default)(Object.keys(_asciiAliases2.default).map(function (name) {
  return _asciiAliases2.default[name].map(function (alias) {
    return quoteRE(alias);
  });
})).join("|");

var edgeCases = ["http", "https"].join("|");

// Regex reads as following:
//
// Match ascii aliases with optional edge cases before it (to know if parsing is needed)
// Additionally, after the ascii alias:
//    - Forbid edge cases
//    - Allow characters included in normal aliases (to check later cases like :s and :smile:)