 // Hides and displays the skill points field on each the problem forms.
 // If a skill is selected, it will display the skill points field.
 $(document).on('change','#SelectSkill',function(){
               if($('#SelectSkill option:selected').val() == ""){
	         		$("#SkillPoints").hide();
	         		$("#SP").prop("required", false);
          		}
          		else
          		{
          			$("#SkillPoints").show();
          			$("#SP").prop('required', true);
          		}
          
 });
 $(document).ready(function(){
 	$("#SkillPoints").hide();
 	$("#SP").prop('required',false);
 });