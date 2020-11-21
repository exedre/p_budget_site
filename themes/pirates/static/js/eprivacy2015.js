// JavaScript Document
window.onload = function ()
{
    var EPlinkCount = 0;
jQuery("a").each(function(){
    if (jQuery(this).attr("href") && jQuery(this).attr("href") !== "#") {
        EPlinkCount++;
    }
    })
console.log("there are " + EPlinkCount + " links on this page ");
var EPcountHTML = '
<div id="countdiv" style="display:none;margin:0;padding:0;position:fixed; bottom:30px;right:30px; z-index:10000;">
 <img src="/images/adv/linkEP2015.png">
 <div onclick="jQuery(\'#countdiv\').fadeOut(\'slow\');" id ="closeMe" style="margin:0;padding:0;cursor:pointer;position:absolute; z-index:10001;right:0px; top:0px;width: 40px;height:40px;"></div>
 <div id="savethelink" style="margin:0;padding:0;position:absolute; bottom:30px;left:0px; width: 100%; height:40%; cursor:pointer;" onclick=\'window.open("http://www.eventbrite.com/e/biglietti-e-privacy-2015-la-trasparenza-e-la-privacy-16856755008?aff=wgt");\'></div>
 <div id="linkcount" style="margin:0;padding:0;position:absolute; top:91px;right:158px; font-weight:bold; font-size:30px; color:white; font-family:Arial; z-index:10000;">0</div>
</div>;
jQuery(document.body).append(EPcountHTML)';
jQuery("#countdiv").fadeIn("slow");
jQuery({countNum: jQuery('#linkcount').text()}).animate({countNum: EPlinkCount}, {
  duration: 8000,
  easing:'linear',
  step: function() {
    jQuery('#linkcount').text(Math.floor(this.countNum));
  },
  complete: function() {
    jQuery('#linkcount').text(this.countNum);
  }
});
}
