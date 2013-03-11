$(function () {

  var closeContainer = function (container) {
    container.find('form').slideUp('fast', function () {
      container.html('');
    });
  }

  var blink = function (objs, scroll_to_it){
    if (scroll_to_it == undefined)
      scroll_to_it = false;
    var htimes = [0, 3000];
    //var htimes = [0, 500, 1000, 1500, 2000, 2500];
    var effect = function(){objs.addClass('hover');};
    var noEffect = function(){objs.removeClass('hover');};

    var i;
    for(i =0; i<htimes.length; i++){
      if (i%2)
        window.setTimeout(noEffect, htimes[i]);
      else
        window.setTimeout(effect, htimes[i]);
    }

    // Scroll to element if not in window port:
    if (scroll_to_it){
      var top = jQuery(window).scrollTop();
      var bottom = top + jQuery(window).height();
      var x = jQuery(objs[0]).offset()['top'];
      if (x > bottom || x < top){
        jQuery("html,body").animate({'scrollTop': (x - (bottom - top)/2)}, 1000);
      }
    }
  }

  $('.add').on('click', function () {

    var parent = $(this).parents('.answers-container');
    var target = $(this).data('target');
    var multiple = $(this).data('multiple');
    var opentext = $(this).data('opentext');
    var closetext = $(this).data('closetext');
    var close = $(this).data('close');

    if(close) {
      closeContainer(parent.find('.add-container'));
      $(this).text(opentext);
      $(this).data('close', '');
      return
    }
    $(this).text($(this).data('closetext'));
    $(this).data('close', true);
    $.get($(this).data('href'), function (data) {
      var add_container = parent.find('.add-container');
      add_container.html(data);
      var form = add_container.find('form');
      form.data('target', target);
      form.data('multiple', multiple);
      form.slideDown('fast', function () {
        $(this).find('input:first').focus();
      });

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
        blink(parent, true);
      } else {
        var form_data = parent.find('.add-container form').data();
        parent.find('.add-container').html(data.html);
        parent.find('.add-container form').show();
        parent.find('.add-container form').data(form_data);
      }
    });
  });

  $('.answers-container').on('click', '.preview', function () {

    var parents = $(this).parents('.preview-container');
    $.get($(this).data('href'), function (data) {
      parents.find('.answer').hide();
      parents.find('.options').show();
      parents.append(data);
      parents.find('.view-answer').slideDown('fast');
    });

  });

  $('.answers-container').on('click', '.hide-answer', function () {

    var parents = $(this).parents('.preview-container');
    var edit = parents.find('.edit-answer');
    var opentext = edit.data('closetext');

    parents.find('.view-answer').slideUp('fast', function () {
      parents.find('.options').hide()
      $(this).remove();
      parents.find('.answer').slideDown('fast');
    });

    parents.find('form').slideUp('fast', function () {
      $(this).remove();
    });

    edit.text(opentext);
    edit.data('close', '');

  });

  $('.answers-container').on('click', '.edit-answer', function () {

    var parents = $(this).parents('.preview-container');
    var href = $(this).data('href');
    var opentext = $(this).data('opentext');
    var closetext = $(this).data('closetext');
    var close = $(this).data('close');

    if(close) {
      parents.find('form').slideUp('fast', function () {
        $(this).remove();
      });
      parents.find('.view-answer').slideDown('fast');
      $(this).text(opentext);
      $(this).data('close', '');
      return
    }

    $(this).text(closetext);
    $(this).data('close', true);

    $.get(href, function (data) {
      parents.find('.view-answer').slideUp('fast', function () {
        parents.append(data);
        parents.find('form').slideDown('fast');
        parents.find('input:first').focus();
      });
    });

  });


  $('.answers-container').on('click', '.cancel', function () {

    var parents = $(this).parents('.preview-container');
    var edit = parents.find('.edit-answer');
    var opentext = edit.data('opentext');

    parents.find('form').slideUp('fast', function () {
      $(this).remove();
      parents.find('.view-answer').slideDown('fast');
    });

    edit.text(opentext);
    edit.data('close', '');

  });

  $('.answers-container').on('submit', '.edit-form', function (e) {

    e.preventDefault();
    var parents = $(this).parents('.preview-container');
    var upper = parents.parent();

    $.post($(this).attr('action'), $(this).serialize(), function (data) {
      if(data.status == 'success') {
        parents.slideDown('fast', function () {
          $(this).remove();
          upper.append(data.html);
        });
      } else {
        parents.find('form').remove();
        parents.append(data.html);
        parents.find('form').show();
      }
    });

  });

});