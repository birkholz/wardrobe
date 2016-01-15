$(document).ready(function () {
    $('#tile-container').imagesLoaded(function () {
        $('#tile-container').isotope({
            itemSelector: '.tile',
            getSortData: {
                name: function ($elem) {
                    return $elem.attr('data-name');
                },
                price: function ($elem) {
                    var price = $elem.find('.value').text();
                    price = parseFloat(price.replace('$', ''));
                    return price;
                },
                company: function ($elem) {
                    var name = $elem.find('.top_left').text();
                    return name;
                }
            },
            onLayout: function () {
                $('#tile-container').height('+=10');
            }
        });
    });

    $('.tile').on('click', function () {
        if ($('body').hasClass('outfit') || $('body').hasClass('worn'))  $(this).toggleClass('selected');
    });

    $('#cat-select').on('change', function () {
        filterTiles();
    });

    $('#sort-select').on('change', function () {
        $('#tile-container').isotope({sortBy: $(this).val()});
    });

    $('#asc').on('click', function (e) {
        $('#tile-container').isotope({sortAscending: true});
        $('#desc').removeClass('active');
        $(this).addClass('active');
        e.preventDefault();
        return false;
    });

    $('#desc').on('click', function (e) {
        $('#tile-container').isotope({sortAscending: false});
        $('#asc').removeClass('active');
        $(this).addClass('active');
        e.preventDefault();
        return false;
    });

    $('#tile-search').on('keyup', function () {
        filterTiles();
    });

    $('#save-button').on('click', function () {
        $('.alert-danger').hide();
        var items = getSelectedItems();
        var name = $('#outfit-name').val();
        var image_url = $('#image-url').val();
        if (name == '') $('#no-name-error').show().alert();
        else if (items.length == 0) $('#no-items-error').show().alert();
        else if ($('#drop-zone .tile').length == 1) $('#one-item-error').show().alert();
        else saveOutfit(name, image_url, items);
    });
    $('#save-worn-button').on('click', function () {
        $('.alert-danger').hide();
        var item_ids = getSelectedItems(),
            date = $('#id_date').val();
        if (date == '') $('#no-date-error').show().alert();
        else if (item_ids.length == 0) $('#no-items-error').show().alert();
        else if ($('#drop-zone .tile').length == 1) $('#one-item-error').show().alert();
        else {
            $.ajax({
                url: '/worn/',
                type: 'POST',
                data: {'date': date, 'item_ids': item_ids},
                success: function () {
                    window.location.href = '/wear_history/';
                },
                error: function () {
                    $('#server-errror').show().alert();
                }
            })
        }
    });
});

function saveOutfit(name, image_url, items) {
    $('#save-button').html('Saving...').addClass('disabled').attr('disabled', 'disabled');
    var url = "/outfit/create/",
        success_url = '/outfits/';
    if ($('body').hasClass('edit')) url = window.location.href;
    if (getURLParameter('first') != "null") success_url = '/outfits/?first=true';
    $.ajax({
        type: "POST",
        url: url,
        data: {'name': name, 'items': items, 'image-url': image_url},
        success: function (outfit_id) {
            window.location.href = success_url;
        },
        error: function () {
            $('#server-errror').show().alert();
        }
    });
}

function getSelectedItems() {
    var items = "";
    $('.tile.selected').each(function () {
        if (items != "") items += ',';
        items += $(this).attr('data-id');
    });
    return items;
}

function filterTiles() {
    var search = $('#tile-search').val().toLowerCase(),
        cat = $('#cat-select').val();
    if (search == '' && cat == 'all') $('#tile-container').isotope({filter: '.tile'});
    else if (search != '' && cat == 'all') {
        $('.tile').removeClass('match');
        $.each($('.tile'), function (index, item) {
            if ($(item).attr('data-name').toLowerCase().indexOf(search) !== -1) $(item).addClass('match');
            else if ($(item).attr('data-company').toLowerCase().indexOf(search) !== -1) $(item).addClass('match');
            else if ($(item).attr('data-color').toLowerCase().indexOf(search) !== -1) $(item).addClass('match');
        });
        $("#tile-container").isotope({filter: '.match'});
    }
    else if (search == '' && cat != 'all') {
        $('.tile').removeClass('match');
        $.each($('.tile'), function (index, item) {
            if (cat == 'owned') {
                var owned = $(item).attr('data-owned');
                if (owned == 'True') $(item).addClass('match');
            }
            else if (cat == 'wanted') {
                var owned = $(item).attr('data-owned');
                if (owned == 'False') $(item).addClass('match');
            }
            else {
                var cats = $(item).attr('data-cat');
                if (cats.indexOf(',') !== -1) cats = cats.split(',');
                if (cats.indexOf(cat) !== -1) $(item).addClass('match');
            }
        });
        $("#tile-container").isotope({filter: '.match'});
    }
    else {
        $('.tile').removeClass('match');
        $.each($('.tile'), function (index, item) {
            if ($(item).attr('data-name').toLowerCase().indexOf(search) !== -1) $(item).addClass('match');
        });
        $('#tile-container').isotope({filter: '.match[data-cat=' + cat + ']'});
    }
}