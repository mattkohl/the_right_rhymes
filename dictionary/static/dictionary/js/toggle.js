/**
 * Created by MBK on 14/01/16.
 */
jQuery(document).ready(function(){
	jQuery(".toggle").click(function(){
		jQuery(this).parent().next(".examples").slideToggle("fast");
		return false;
	});
});

jQuery(document).ready(function(){
	jQuery("ul.footer-tags li.highlight").click(function(){
		jQuery(this).siblings(".hidden").slideToggle("slow");
		return false;
	});
});