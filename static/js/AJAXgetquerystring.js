var simpleTypes =
{
		"TEXT"     	:true,
		"TEXTAREA" 	:true,
		"PASSWORD" 	:true,
		"BUTTON"   	:true,
		"RESET"    	:true,
		"SUBMIT"	:true,
		"FILE"		:true,
		"IMAGE"		:true,
		"HIDDEN"	:true
};

function getquerystring(formName) {
    var form = document.forms[formName];
	var qstr = "";

    function GetElemValue(name, value) {
        qstr += (qstr.length > 0 ? "&" : "")
                + escape(name).replace(/\+/g, "%2B") + "="
                + escape(value ? value : "").replace(/\+/g, "%2B");
    }

	var elemArray = form.elements;
    for (var i = 0; i < elemArray.length; i++) {
        var element = elemArray[i];
        var elemType = element.type.toUpperCase();
        var elemName = element.name;
        console.log(elemType)
        if (elemName) {
            if (elemType in simpleTypes) {
                GetElemValue(elemName, element.value);
            } else if (elemType == "CHECKBOX" && element.checked) {
                GetElemValue(elemName, 
                    element.value ? element.value : "On");
            } else if (elemType == "RADIO" && element.checked) {
                GetElemValue(elemName, element.value);
            } else if (elemType.indexOf("SELECT") != -1) {
                for (var j = 0; j < element.options.length; j++) {
                    var option = element.options[j];
                    if (option.selected) {
                        GetElemValue(elemName,
                            option.value ? option.value : option.text);
                    }
                }
            }
        }
    }

    return qstr;

}

function nothing() {
    return;
}

function submit_form(uniqid,part,extra_stuff_fun) {
	var query = getquerystring(uniqid+'-'+part);
	
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange =
		function() {
				document.getElementById(uniqid+"-"+(part+1)+"-results").innerHTML = xhttp.responseText;
				extra_stuff_fun();
	    };
	xhttp.open("POST","doDynamicQuestion",true);
	xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	
	xhttp.send(query);
}

var aceEditors = {}
function makeNewEditors() {
    var allEditorDivs = document.getElementsByClassName("ace-editor");
    var len = allEditorDivs.length;
    for (var i = 0; i<len; i++) {
        var editorDiv = allEditorDivs[i];
        if (aceEditors[editorDiv.id] == undefined) {
            aceEditors[editorDiv.id] = ace.edit(editorDiv.id);
            var thiseditor = aceEditors[editorDiv.id]
		    thiseditor.setTheme("ace/theme/chrome");
		    thiseditor.getSession().setMode("ace/mode/"+editorDiv.title); // We're putting language mode in title. Yes, this is an abuse of the field, but it shouldn't hurt anything.				    
		}
    }
}

function makeNewReadOnlyEditors() {
	var allEditorDivs = document.getElementsByClassName("ace-editor-readonly");
	var len = allEditorDivs.length;
	for (var i = 0; i<len; i++) {
		var editorDiv = allEditorDivs[i];
		var thiseditor = ace.edit(editorDiv.id);
		thiseditor.setTheme("ace/theme/chrome");
		thiseditor.getSession().setMode("ace/mode/lua");
		thiseditor.setReadOnly(true);
		if (editorDiv.title != "None") {
			var Range = ace.require('ace/range').Range;
			thiseditor.session.addMarker(new Range(editorDiv.title-1, 0, editorDiv.title-1, 1), "lineHighlight", "fullLine");
		}
		//We're putting which line to highlight in the title.  There's probably a better way to do this than abusing this field, but it doesn't get used for anything
		//so it shouldn't hurt anything.
	}
}

function makeAllEditors() {
	makeNewEditors();
	makeNewReadOnlyEditors();
}

function copyAJAXEditorsToHidden(formid) {
    var form = document.getElementById(formid);
    var formEditorDivs = form.getElementsByClassName("ace-editor");
    var len = formEditorDivs.length;
    for (var i = 0; i<len; i++) {
        var editorDiv = formEditorDivs[i];
        var myeditor = aceEditors[editorDiv.id];
        var hidden = document.getElementById(editorDiv.id+"-hidden");
        hidden.value = myeditor.getValue();
    }
}