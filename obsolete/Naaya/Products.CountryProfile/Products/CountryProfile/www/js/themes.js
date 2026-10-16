$(document).ready(function(){
    $(".select-combo").change(function(){
        var self = $(this),
            val = self.val(),
            target = $(self.attr('target')),
            target_from = $(target.attr('from')),
            target_url = target.attr('src'),
            data = {};

        if (target_from.length){
            data[target_from.attr('name')] = target_from.val();
            var from_from = $(target_from.attr("from"));
            if (from_from.length){
                data[from_from.attr('name')] = from_from.val();
            }
        }
        $.getJSON(target_url, data, function(data){
            target.empty();
            $.each(data, function(){
                target.append($("<option>").val(this.val).html(this.label));
            });
            target.trigger("change");
        });
    });
});
