$(function () {

  var closeContainer = function (container) {
    container.html('');
    container.hide();
  }

  $('.add').on('click', function () {

    var parent = $(this).parents('.answers-container');
    var target = $(this).data('target');

    $.get($(this).data('href'), function (data) {
      parent.find('.add-container').html(data);
      parent.find('.add-container').find('form').data('target', target);
      parent.find('.add-container').show();
    });

  });

  $('.add-container').on('click', '.cancel', function () {

    closeContainer($(this).parents('.add-container'));

  });


  $('.add-container').on('submit', 'form', function (e) {

    e.preventDefault();
    var parent = $(this).parents('.answers-container');
    var target = $(this).data('target');
    console.log(target);

    $.post($(this).attr('action'), $(this).serialize(), function (data) {
      if(data.status == 'success') {
        console.log(target, $(target));
        $(target).append(data.html);
        closeContainer(parent);
      } else {
        parent.find('.add-container').html(data.html);
      }

    });


  });

});