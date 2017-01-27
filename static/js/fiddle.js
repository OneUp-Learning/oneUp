$(function(){
	$("#specChall").css("display","none");
	$(".selectChallenges").click(function(){
      if ($('input[name=assignChallenges]:checked').val() == "2") {
          $("#specChall").slideDown("fast"); //Slide Down Effect
          $.cookie('showTop', 'expanded'); //Add cookie 'ShowTop'
      }
      if ($('input[name=assignChallenges]:checked').val() == "1"){ 
          $("#specChall").slideUp("fast");  
          $.cookie('showTop', 'collapsed'); //Add cookie 'ShowTop'
      }
   });
      var showTop = $.cookie('showTop');
      if (showTop == 'expanded') {
      $("#specChall").show("fast");
      $('input[name=assignChallenges]:checked');
    } else {
      $("#specChall").hide("fast");
      $('input[name=assignChallenges]:checked');
    }
});