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
  $("#header-search-box").autocomplete({
    source: function(request, response) {
        $.getJSON(
            '/search_headwords/',
            { 'term': request.term },
            function(data) {
                parsed = $.parseJSON(data);
                response(parsed.headwords);
            }
        )
    },
    minLength: 2
  });
});

//$(document).ready(function () {
//     $('a[href*="#"]').on('click', function (e) {
//         e.preventDefault();
//
//         var target = this.hash,
//             $target = $(target);
//
//         $('html, body').stop().animate({
//             'scrollTop': $target.offset().top - 100
//         }, 900, 'swing', function () {
//             window.location.hash = target;
//         });
//     });
// });
//
//$(document).ready(function() {
//    var h = scrollY || pageYOffset;
//    console.log(h);
//    if (scroll > 0) {
//        $('html, body').animate({ scrollTop: h + 80 }, 50);
//    }
//});