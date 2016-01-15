function getURLParameter(name) {
    return decodeURI(
        (RegExp(name + '=' + '(.+?)(&|$)').exec(location.search) || [, null])[1]
    );
}
$(document).ready(function () {
    $('.hover-dropdown').on('mouseenter', function () {
        if ($(window).width() > 768) $(this).addClass("open");
    }).on('mouseleave', function () {
        if ($(window).width() > 768) $(this).removeClass("open");
    });
    $(window).resize(function () {
        if ($(window).width() < 768) $('.hover-dropdown').addClass('open');
        else $('.hover-dropdown').removeClass('open');
    });
    $('.navbar-toggle').on('click', function () {
        setTimeout(function () {
            if (!$(this).hasClass('collapsed')) $('.hover-dropdown').addClass('open');
        }, 50);
    });
    $('.tile:not(.outfit_tile)').on('click', '.glyphicon-remove', function (e) {
        e.stopPropagation();
        var item_id = $(this).attr('data-id');
        var $tile = $('.tile[data-id=' + item_id + ']');
        var item_name = $tile.find('.name').text();
        var cf = confirm('Are you sure you want to delete "' + item_name + '"?');
        if (cf) {
            $.ajax({
                url: "/item/" + item_id + '/delete/',
                success: function () {
                    var $tc = $tile.closest('#tile-container'),
                        $dz = $tile.closest('#drop-zone');
                    $tile.remove();
                    if ($tc)
                        $tc.isotope('reloadItems').isotope({sortBy: 'name'});
                    else if ($dz)
                        $dz.isotope('reloadItems').isotope({sortBy: 'name'});
                },
                error: function () {
                    alert('An error has occurred.');
                }
            });
        }
        return false;
    });
    $(document).on('click', '.tile .glyphicon-edit', function (e) {
        e.stopPropagation();
        window.location.href = $(this).attr('href');
        return false;
    });
    $(document).on('click', '.tile .view_pictures_button', function (e) {
        e.stopPropagation();
        $(this).find('a').first().trigger('click');
        return false;
    });
    $(document).on('mouseenter', '.tile .glyphicon', function () {
        $(this).addClass('icon-white');
    }).on('mouseleave', '.tile .glyphicon', function () {
        $(this).removeClass('icon-white')
    });
    $('.sysmsg .close').on('click', function () {
        var $alert = $(this).closest('.alert');
        var msg_id = $(this).attr('data-msg-id');
        $.ajax({
            url: '/sysmsg/' + msg_id + '/read/',
            success: function () {
                $alert.remove();
            },
            error: function () {
                alert('An error has occurred.');
            }
        });
    });
    $('.outfit-delete').on('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var name = $(this).attr('data-name');
        var cf = confirm('Are you sure you want to delete "' + name + '"?');
        if (cf) window.location.href = $(this).attr('href');
        return false;
    });
});