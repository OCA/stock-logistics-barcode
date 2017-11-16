jQuery(document).ready(function($) {
    if ($(document).height() - 20 > $('.container').height()) {
        $('.block-bottom').css({
            position: "relative",
            bottom: 0,
            marginBottom: 15,
            left: 0,
            right: 0
        });
    }
});

$(document).ready(function() {
    $('#kpad-result').focus();
    $('.kpad-row .kpad-nmbr').click(function() {
        $('#kpad-result').val($('#kpad-result').val() + $(this).data('key'));
        $('#kpad-result').focus();
    });
    $('.kpad-row .kpad-del').click(function() {
        $('#kpad-result').val($('#kpad-result').val().substring(0, $('#kpad-result').val().length - 1));
        $('#kpad-result').focus();
    });
    $('.kpad-row .kpad-dot').click(function() {
        $('#kpad-result').val($('#kpad-result').val() + $(this).data('key'));
        $('#kpad-result').focus();
    });
});
