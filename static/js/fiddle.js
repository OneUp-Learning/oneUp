$(document).ready(function(){
	$("#specChall").css("display","none");
	$("#specAct").css("display","none");
	if ($('input[name=assignChallenges]:checked').val() == "2") {
        $("#specChall").slideDown("fast"); //Slide Down Effect
    }
	$(".selectChallenges").click(function(){
      if ($('input[name=assignChallenges]:checked').val() == "2") {
          $("#specChall").slideDown("fast"); //Slide Down Effect
      }
      if ($('input[name=assignChallenges]:checked').val() == "1"){ 
          $("#specChall").slideUp("fast");  
      }
	 });
    if ($('input[name=assignActivities]:checked').val() == "2") {
          $("#specAct").slideDown("fast"); //Slide Down Effect
      }
  	$(".selectActivities").click(function(){
        if ($('input[name=assignActivities]:checked').val() == "2") {
            $("#specAct").slideDown("fast"); //Slide Down Effect
        }
        if ($('input[name=assignActivities]:checked').val() == "1"){ 
            $("#specAct").slideUp("fast");  
        }
  	});
 
});