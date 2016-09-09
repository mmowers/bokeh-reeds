$(document).ready(function(){
    $('body').on('click', '#modelid_scenarios_heading', function(){
        $('#modelid_scenarios').toggle();
    });
    $('body').on('click', '#modelid_scenarios input', function(){
        var label = $(this).parent().text()
        var checked = $(this).is(':checked');
        var index = $('#modelid_scenarios input').index($(this));
        $( '.bk-plot-layout:eq('+index+')').toggle();
    });
});