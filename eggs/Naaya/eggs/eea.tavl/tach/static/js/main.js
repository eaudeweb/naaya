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
    var closetext = $(this).data('closetext');
    var close = $(this).data('close');

    if(close) {
      closeContainer(parent.find('.add-container'));
      $(this).text($(this).data('opentext'));
      $(this).data('close', '');
      return
    }
    $(this).text($(this).data('closetext'));
    $(this).data('close', true);
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

    var parent = $(this).parents('.answers-container');
    var add = parent.find('.add');
    add.text(add.data('opentext'));
    add.data('close', '');
    closeContainer($(this).parents('.add-container'));

  });

  $('.add-container').on('submit', 'form', function (e) {

    e.preventDefault();
    var parent = $(this).parents('.answers-container');
    var target = $(this).data('target');
    var multiple = $(this).data('multiple');
    var add = parent.find('.add');

    $.post($(this).attr('action'), $(this).serialize(), function (data) {
      if(data.status == 'success') {
        $(target).append(data.html);
        closeContainer(parent.find('.add-container'));
        add.text(add.data('opentext'));
        add.data('close', '');
        if(!multiple) {
          parent.find('.add').remove();
        }
      } else {
        var form_data = parent.find('.add-container form').data();
        parent.find('.add-container').html(data.html);
        parent.find('.add-container form').data(form_data);
      }
    });
  });

  $('.answers-container').on('click', '.preview', function () {

    var parents = $(this).parents('.preview-container');
    $.get($(this).data('href'), function (data) {
      parents.find('.answer').hide();
      parents.find('.hide-answer').show();
      parents.append(data);
      parents.find('.view-table').slideDown('fast');
    });

  });

  $('.answers-container').on('click', '.hide-answer', function () {

    var parents = $(this).parents('.preview-container');
    parents.find('.view-table').slideUp('fast', function () {
      parents.find('.hide-answer').hide()
      $(this).remove();
      parents.find('.answer').slideDown('fast');
    });

  });



});