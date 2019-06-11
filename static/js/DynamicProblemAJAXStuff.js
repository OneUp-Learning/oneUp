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

function getDynamicProblemPartData(idprefix) {
	var dynamicProblemPartDiv = document.getElementById(idprefix+"-exact");
	var allInputs = dynamicProblemPartDiv.getElementsByTagName("input");
	var data = {}
	for (var i=0; i<allInputs.length; i++) {
		if (allInputs[i].name.startsWith(idprefix)) {
			var name = allInputs[i].name.substr(idprefix.length+1);
			data[name] = allInputs[i].value;
		}
	}
	var allAceEditors = dynamicProblemPartDiv.getElementsByClassName("ace-editor");
	for (var i=0; i<allAceEditors.length; i++) {
		if (allAceEditors[i].id.startsWith(idprefix)) {
			var name = allAceEditors[i].id.substr(idprefix.length+1);
			data[name] = aceEditors[allAceEditors[i].id].getValue();
		}
	}
	return data;
}

function disableDiv(name) {
	var darkLayer = document.getElementById(name+"-darkLayer");
	darkLayer.style.display="";
	var element = document.getElementById(name+"-exact");
	var descendents = element.getElementsByTagName("*");
	var i, e;
	for (i = 0; i < descendents.length; i++) {
		e = descendents[i];
		if ((e.tagName == "INPUT") || (e.tagName == "TEXTAREA") || (e.tagName == "BUTTON") || (e.tagName == "SELECT") ||
			(e.tagName == "OPTION") || (e.tagName == "OPTGROUP") || (e.tagName == "FIELDSET")) {
			e.disabled = "disabled";
		}
		if ((e.tagName == "INPUT") && (e.type.toUpperCase() == "SUBMIT")) {
			e.value = "Submitted";
		}
		
	}
}

function senddynamicquestion(idprefix) {
	var idParts = idprefix.split("-");
	var uniqid = idParts[0];
	var partNum = parseInt(idParts[1]);
	var data = getDynamicProblemPartData(idprefix);
	data['_attemptId'] = attemptId;
	data['_inChallenge'] = inChallenge;
	data['_inTryOut'] = inTryOut;
	data['_partNum'] = partNum+1;
	data['_uniqid'] = uniqid;
	$.ajax({
		url: "doDynamicQuestion",
		type: "POST",
		data: data,
		dataType: 'html',
		success: function(result,textStatus, jqXHR) {
			$("#"+idprefix+'-results').html(result);
			makeAllEditors();
		}
	});
}

function shownextpart(idprefix) {
	document.getElementById(idprefix+"-exact").style.display = "block";
	document.getElementById(idprefix+"-partial_success_message").style.display = "none";
}


