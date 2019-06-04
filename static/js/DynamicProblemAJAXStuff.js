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
	var dynamicProblemPartDiv = document.getElementByID(idprefix+"-exact");
	var allInputs = dynamicProblemPartDiv.getElementsByTagName("input");
	var data = {}
	for (var i=0; i<allInputs.length; i++) {
		if (allInputs[i].name.startswith(idprefix)) {
			var name = allInputs[i].name.substr(idprefix.length);
			data[name] = allInputs[i].value;
			
	}
	var allAceEditors = dynamicProblemPartDiv.getElementsByClassName("ace-editor");
	for (var i=-; i<allAceEditors.length; i++) {
		if (allAceEditors[i].id.startswith(idprefix)) {
			var name = allAceEditors[i].id.substr(idprefix.length);
			data[name] = aceEditors[allAceEditors[i].id].getValue();
		}
	}
	return data;
}

function senddynamicquestion(button) {
	var idprefix = button.name;
	var nextpartidprefix = uniqid + "-" + toString(partnum+1);
	var data = getDynamicProblemPartData(idprefix);
	data['__attemptId'] = attemptId;
	data['__inChallenge'] = inChallenge;
	data['__partNum'] = partnum;
	data['__inTryOut'] = inTryOut;
	$.ajax({
		url: "doDynamicQuestion",
		type: "POST",
		data: data,
		dataType: 'html',
		success: function(result,textStatus, jqXHR) {
			$("#"+idprefix+'-results').hmtl(result);
		}
	});
}



