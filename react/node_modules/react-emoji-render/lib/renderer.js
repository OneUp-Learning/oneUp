"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

exports.toArray = toArray;
exports.default = Emoji;

var _react = require("react");

var _react2 = _interopRequireDefault(_react);

var _propTypes = require("prop-types");

var _propTypes2 = _interopRequireDefault(_propTypes);

var _classnames2 = require("classnames");

var _classnames3 = _interopRequireDefault(_classnames2);

var _stringReplaceToArray = require("string-replace-to-array");

var _stringReplaceToArray2 = _interopRequireDefault(_stringReplaceToArray);

var _emojiRegex = require("emoji-regex");

var _emojiRegex2 = _interopRequireDefault(_emojiRegex);

var _asciiRegex = require("./asciiRegex");

var _asciiRegex2 = _interopRequireDefault(_asciiRegex);

var _normalizeProtocol = require("./normalizeProtocol");

var _normalizeProtocol2 = _interopRequireDefault(_normalizeProtocol);

var _unicodeToCodepoint = require("./unicodeToCodepoint");

var _unicodeToCodepoint2 = _interopRequireDefault(_unicodeToCodepoint);

var _aliases = require("../data/aliases");

var _aliases2 = _interopRequireDefault(_aliases);

var _asciiAliases = require("../data/asciiAliases");

var _asciiAliases2 = _interopRequireDefault(_asciiAliases);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _objectWithoutProperties(obj, keys) { var target = {}; for (var i in obj) { if (keys.indexOf(i) >= 0) continue; if (!Object.prototype.hasOwnProperty.call(obj, i)) continue; target[i] = obj[i]; } return target; }

var asciiAliasesRegex = (0, _asciiRegex2.default)();
var unicodeEmojiRegex = (0, _emojiRegex2.default)();
var aliasesRegex = /:([\w\-\_\+]+):/g;

// using em's we can ensure size matches surrounding font
var style = {
  width: "1em",
  height: "1em",
  margin: "0 .05em 0 .1em",
  verticalAlign: "-0.1em"
};

function toArray(text) {
  var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

  var protocol = (0, _normalizeProtocol2.default)(options.protocol);

  function replaceUnicodeEmoji(match, i) {
    if (!options.baseUrl) {
      return _react2.default.createElement(
        "span",
        { key: i, style: style, className: options.className },
        match
      );
    }

    var separator = options.size ? "/" : "";
    var codepoint = (0, _unicodeToCodepoint2.default)(match);
    var src = "" + protocol + options.baseUrl + options.size + separator + codepoint + "." + options.ext;

    return _react2.default.createElement("img", _extends({
      key: i,
      alt: match,
      src: src,
      style: style,
      className: options.className
    }, options.props));
  }

  function replaceAsciiAliases() {
    var asciiAliasKeys = Object.keys(_asciiAliases2.default);

    for (var _len = arguments.length, match = Array(_len), _key = 0; _key < _len; _key++) {
      match[_key] = arguments[_key];
    }

    for (var i in asciiAliasKeys) {
      var alias = asciiAliasKeys[i];
      var data = _asciiAliases2.default[alias];
      var aliasFound = match[2];

      if (data.includes(aliasFound)) {
        var isEdgeCase = match[1];
        var fullMatchContent = match[0].slice(1, -1); // remove ":" at the beginning and end
        var validAsciiAlias = !_aliases2.default[fullMatchContent]; // ":" + fullMatchContent + ":" alias doesn't exist

        if (!isEdgeCase && validAsciiAlias) {
          return ":" + alias + ":";
        }

        // return the original word to replace its value in aliasesRegex
        return match[0];
      }
    }
  }

  function replaceAliases() {
    for (var _len2 = arguments.length, match = Array(_len2), _key2 = 0; _key2 < _len2; _key2++) {
      match[_key2] = arguments[_key2];
    }

    return _aliases2.default[match[1]] || match[0];
  }

  return (0, _stringReplaceToArray2.default)(text.replace(asciiAliasesRegex, replaceAsciiAliases).replace(aliasesRegex, replaceAliases), unicodeEmojiRegex, replaceUnicodeEmoji);
}

function Emoji(_ref) {
  var text = _ref.text,
      onlyEmojiClassName = _ref.onlyEmojiClassName,
      _ref$options = _ref.options,
      options = _ref$options === undefined ? {} : _ref$options,
      className = _ref.className,
      rest = _objectWithoutProperties(_ref, ["text", "onlyEmojiClassName", "options", "className"]);

  function isOnlyEmoji(output) {
    if (output.length > 3) return false;

    for (var i = 0; i < output.length; i++) {
      if (typeof output[i] === "string") return false;
    }

    return true;
  }

  var output = toArray(text, options);
  var classes = (0, _classnames3.default)(className, _defineProperty({}, onlyEmojiClassName, isOnlyEmoji(output)));

  return _react2.default.createElement(
    "span",
    _extends({}, rest, { className: classes }),
    output
  );
}

Emoji.propTypes = {
  text: _propTypes2.default.string,
  props: _propTypes2.default.object,
  onlyEmojiClassName: _propTypes2.default.string,
  options: _propTypes2.default.shape({
    baseUrl: _propTypes2.default.string,
    size: _propTypes2.default.string,
    ext: _propTypes2.default.string,
    className: _propTypes2.default.string
  })
};