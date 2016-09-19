$(document).ready(function(){
    $('body').on('click', '#modelid_scenarios_heading', function(){
        $('#modelid_scenarios').toggle();
    });
    $('body').on('click', '#modelid_set_axis_ranges_heading', function(){
        $('#modelid_set_x_min').toggle();
        $('#modelid_set_x_max').toggle();
        $('#modelid_set_y_min').toggle();
        $('#modelid_set_y_max').toggle();
    });
    $('body').on('click', '#modelid_techs_heading', function(){
        $('#modelid_techs').toggle();
    });
    $('body').on('click', '.legend-header', function(){
        $(this).next('.legend-body').toggle();
    });
    $('body').on('click', '#modelid_scenarios input', function(){
        var label = $(this).parent().text()
        var checked = $(this).is(':checked');
        var index = $('#modelid_scenarios input').index($(this));
        $( '.bk-plot-layout:eq('+index+')').toggle();
    });
});