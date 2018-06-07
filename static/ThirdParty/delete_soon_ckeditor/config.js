/**
 * @license Copyright (c) 2003-2017, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here.
	// For complete reference see:
	// http://docs.ckeditor.com/#!/api/CKEDITOR.config

	// The toolbar groups arrangement, optimized for two toolbar rows.
	config.toolbarGroups = [
		{ name: 'clipboard', groups: [ 'clipboard', 'undo' ] },
		{ name: 'insert', groups: [ 'insert' ] },
		{ name: 'pbckcode', groups: [ 'pbckcode' ] },
		{ name: 'links', groups: [ 'links' ] },
		{ name: 'forms', groups: [ 'forms' ] },
		{ name: 'tools', groups: [ 'tools' ] },
		'/',
		{ name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
		{ name: 'paragraph', groups: [ 'list', 'indent', 'blocks', 'align', 'bidi', 'paragraph' ] },
		{ name: 'editing', groups: [ 'find', 'selection', 'spellchecker', 'editing' ] },
		{ name: 'document', groups: [ 'document', 'mode', 'doctools' ] },
		'/',
		{ name: 'styles', groups: [ 'styles' ] },
		{ name: 'colors', groups: [ 'colors' ] },
		{ name: 'others', groups: [ 'others' ] },
		{ name: 'about', groups: [ 'about' ] }
	];


	config.removeButtons = 'DocProps,PasteCode,CodeSnippet,About';

	// Remove some buttons provided by the standard plugins, which are
	// not needed in the Standard(s) toolbar.
	// config.removeButtons = 'Underline,Subscript,Superscript';   // Commented out by DD

	// Set the most common block elements.
	config.format_tags = 'p;h1;h2;h3;pre';

	// Simplify the dialog windows.
	config.removeDialogTabs = 'image:advanced;link:advanced';

	
	// Add line height in 'em' rather that integer numbers      # Added by DD
	config.line_height="0.8em;1em;1.1em;1.2em;1.3em;1.4em;1.5em" ;
	
	config.filebrowserImageBrowseUrl = '';
	
	  // PBCKCODE CUSTOMIZATION
	  config.pbckcode = {
	    // An optional class to your pre tag.
	    cls: '',

	    // The syntax highlighter you will use in the output view
	    highlighter: 'PRETTIFY',

	    // An array of the available modes for you plugin.
	    // The key corresponds to the string shown in the select tag.
	    // The value correspond to the loaded file for ACE Editor.
	    modes: [['HTML', 'html'], ['CSS', 'css'], ['PHP', 'php'], ['JS', 'javascript'], ['Java', 'java'],['Python', 'python'] ],

	    // The theme of the ACE Editor of the plugin.
	    theme: 'textmate',

	    // Tab indentation (in spaces)
	    tab_size: '4'
	  };
	
	// increase the area of the CKEditor	# Added by DD  - seems this is not needed since without it a scrollbar appears when more text is inserted
	//config.extraPlugins = 'autogrow';
	//config.autoGrow_minHeight = 200;
	//config.autoGrow_maxHeight = 600;
	//config.autoGrow_bottomSpace = 50;
	
};