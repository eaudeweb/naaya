$(document).ready(function(){
    $('.collapsible-trigger').next('ul.collapsible').slideUp();
    $('.collapsible-trigger.hide').fadeOut();

    $('.collapsible-trigger.show').click(function(e){
        e.preventDefault();
        $this = $(this);
        $this.next().next('ul.collapsible').slideDown();
        $this.fadeOut(100, function(){
            $('.collapsible-trigger.hide').fadeIn();
        });
    });

    $('.collapsible-trigger.hide').click(function(e){
        e.preventDefault();
        $this = $(this);
        $this.next('ul.collapsible').slideUp();
        $this.fadeOut(100, function(){
            $('.collapsible-trigger.show').fadeIn();
        });
    });
});