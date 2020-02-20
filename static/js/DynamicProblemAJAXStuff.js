ace_editors = {}
function makeNewEditors() {
	console.log("makeNewEditors called");
    var allEditorDivs = document.getElementsByClassName("ace-editor");
    var len = allEditorDivs.length;
    console.log(len);
    for (var i = 0; i<len; i++) {
        var editorDiv = allEditorDivs[i];
        if (ace_editors[editorDiv.id] == undefined) {
        	ace_editors[editorDiv.id] = ace.edit(editorDiv.id);
            var thiseditor = ace_editors[editorDiv.id]
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
			data[name] = ace_editors[allAceEditors[i].id].getValue();
		}
	}
	return data;
}

function disableInputsInside(element) {
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
		if (e.tagName == "BUTTON") {
			e.disabled = true;
		}
	}
}

function disableDiv(name) {
	var darkLayer = document.getElementById(name+"-darkLayer");
	if (darkLayer) {
		darkLayer.style.display="";
	}
	var element = document.getElementById(name+"-exact");
	disableInputsInside(element);
}

function nothing() {
    return;
}

function senddynamicquestion(idprefix, callback = nothing, display = true) {
	dynamicProblemPartSubmittedAtLeastOnce[idprefix]=true;
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
			if (display) {
				$("#"+idprefix+'-results').html(result);
				makeAllEditors();
			}
			callback();
		}
	});
}

function shownextpart(idprefix) {
	document.getElementById(idprefix+"-exact").style.display = "block";
	document.getElementById(idprefix+"-partial_success_message").style.display = "none";
	idParts = idprefix.split("-");
	previousNum = parseInt(idParts[1])-1;
	previousId = idParts[0]+"-"+previousNum;
	disableDiv(previousId);
	dynamicProblemPartExists.push(idprefix);
}

var dynamicProblemPartExists = []
var dynamicProblemPartSubmittedAtLeastOnce = {}

function unsubmittedExist() {
	var i = 0;
	for (var i = 0; i < dynamicProblemPartExists.length; i++) {
		if (!(dynamicProblemPartSubmittedAtLeastOnce.hasOwnProperty(dynamicProblemPartExists[i]))) {
			console.log(dynamicProblemPartExists[i]);
			senddynamicquestion(dynamicProblemPartExists[i]);
		}
	}
}

function submitAllUnsubmitted() {
	var allUnsubmitted = [];
	var i = 0;
	for (var i = 0; i < dynamicProblemPartExists.length; i++) {
		if (!(dynamicProblemPartSubmittedAtLeastOnce.hasOwnProperty(dynamicProblemPartExists[i]))) {
			allUnsubmitted.push(dynamicProblemPartExists[i]);
		}
	}
	function submitUnsubmittedOrWholeForm() {
		if (allUnsubmitted.length == 0) {
			formSubmit();
		} else {
			next = allUnsubmitted.pop();
			senddynamicquestion(next,submitUnsubmittedOrWholeForm,false);
		}
	}
	if (allUnsubmitted.length == 0) {
		return true;
	} else {
		submitUnsubmittedOrWholeForm();
		return false;
	} 
}
