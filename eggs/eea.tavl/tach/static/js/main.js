$(function () {

  var closeContainer = function (container) {
    container.slideUp('fast', function () {
      container.html('');
    });
  }

  $('.add').on('click', function () {

    var parent = $(this).parents('.answers-container');
    var target = $(this).data('target');
    var multiple = $(this).data('multiple');

    $.get($(this).data('href'), function (data) {
      var add_container = parent.find('.add-container');
      add_container.html(data);
      var form =  add_container.find('form');
      form.data('target', target);
      form.data('multiple', multiple);
      add_container.slideDown('fast');
    });

  });

  $('.add-container').on('click', '.cancel', function () {

    closeContainer($(this).parents('.add-container'));

  });


  $('.add-container').on('submit', 'form', function (e) {

    e.preventDefault();
    var parent = $(this).parents('.answers-container');
    var target = $(this).data('target');
    var multiple = $(this).data('multiple');

    $.post($(this).attr('action'), $(this).serialize(), function (data) {
      if(data.status == 'success') {
        $(target).append(data.html);
        closeContainer(parent.find('.add-container'));
        if(!multiple) {
          parent.find('.add').remove();
        }
      } else {
        parent.find('.add-container').html(data.html);
      }
    });
  });
});