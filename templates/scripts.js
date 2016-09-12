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

    var tech_clicked = false;
    $('body').on('click', '#tech', function(){
        if(tech_clicked) return;
        $('#tech option').each(function(){
            var re = /:(#.*)$/i;
            if (re.test($(this).text())) {
                var match = $(this).text().match(re);
                $(this).css('background-color',match[1]);
                $(this).text($(this).text().replace(match[0],''));
            }
        });
        tech_clicked = true;
    });
});