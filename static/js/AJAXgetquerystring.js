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

function submit_form(uniqid) {
	var query = getquerystring(uniqid);
	alert(query);
	
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange =
		function() {
			//if (xhttp.readyState == 4 && xhttp.status == 200) {
				document.getElementById(uniqid+"div").innerHTML = xhttp.responseText;
			//}
	    };
	xhttp.open("POST","doDynamicQuestion",true);
	xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
	
	xhttp.send(query);
}
