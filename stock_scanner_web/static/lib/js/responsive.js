jQuery(document).ready(function($) {
    if ($(document).height() - 20 > $('.container').height()) {
        $('.block-bottom').css({ position: "relative", bottom: 0, marginBottom: 15, left: 0, right: 0});
    }
});
