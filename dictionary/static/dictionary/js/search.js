/**
 * Created by MBK on 22/01/16.
 */
$(document).ready(function(e){
    $('.search-panel .dropdown-menu').find('a').click(function(e) {
		e.preventDefault();
		var param = $(this).attr("href").replace("#","");
		var concept = $(this).text();
		$('.search-panel span#search_concept').text(concept);
		$('.input-group #search_param').val(param);
	});
});

$(window).scroll(function() {
    if ($(".navbar").offset().top > 10) {
        $(".navbar-fixed-top").addClass("top-nav-collapse");
    } else {
        $(".navbar-fixed-top").removeClass("top-nav-collapse");
    }
});

// Closes the Responsive Menu on Menu Item Click
$('.navbar-collapse ul li a').click(function() {
    $('.navbar-toggle:visible').click();
});

$(function() {
  $("#index-search-box").autocomplete({
    source: function(request, response) {
        $.getJSON(
            '/data/headword_search/',
            { 'term': request.term },
            function(data) {
                response(data.entries);
            }
        )
    },
    focus: function( event, ui ) {
        $( "#index-search-box" ).val( ui.item.label );
        return false;
    },
    select: function( event, ui ) {
        $("#index-search-box").val( ui.item.label );
        $("#search_slug").val( ui.item.id );
        $("#search_param").val( 'headwords' );
        $('#header-search-form').submit();
        return false;
    },
    minLength: 2
  });
});

jQuery.curCSS = function(element, prop, val) {
    return jQuery(element).css(prop, val);
};

document.addEventListener("touchstart", function(){}, true);