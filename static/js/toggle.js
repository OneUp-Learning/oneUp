$(function(){
	$('#instructorCategories').find('ul').hide();
$('#instructorCategories').find('span').click(function(e){
    $(this).parent().children('ul').toggle();
});
});
