(function(B, _, rangy) {

    /* B => Backbone */
    // regular expression that replaces multiple spaces with one space
    var matchSpaces = /\s{2,}/g;
    // regular expression that matches date and author from
    // '17 Feb 2012 17:15:50, <a href="#">admin</a>'
    var matchDateAndAUthor = /^([^,]+),\s*<[aA] href="#">([^<]*)<\/[aA]>/;

    var isForumPage = function () {return $(".forum_topic").length > 0;};
    var sidebarExists = function () {return $("#sidebar-port").length > 0};

    // Dictionary that will contain all text translated in user language
    var translation_dictonary = {};

    var gettext = function (msg) {
        return translation_dictonary[msg] || msg;
   };

    // dispatcher that will handle custom events
    var dispatcher = _.clone(B.Events);

    var MessageModel = B.Model.extend({
        defaults: {content: null, author: null, date: null, id: null}
   });

    var PublishButtonView = B.View.extend({
        /* View that handles the render for the publish button. */
        tagName: "a",

        className: "btn-publish",

        selector: ".message_top_buttons",

        initialize: function () {this.render();},

        render: function () {
            this.$el.text(gettext("Publish")); // how can we do i18n
            $(this.selector).append(this.$el);
       }
   });

    var BoardView = B.View.extend({
        /* Renders the publish button and adds the events for publishing a
           selected text. */
        el: "#middle_port",

        events: {"mousedown .btn-publish": "publish"},

        dialogOptions: {
            modal: true,
            buttons: {
                Ok: function() {$(this).dialog("close");}
           }
       },

        initialize: function () {
            this.getTranslation(this.render);
            dispatcher.on("publish/message", this.publishMessage, this);
       },

        render: function () {
            new PublishButtonView();
       },

        publish: function (e) {
            e.preventDefault();
            // fetch selected text with html tags
            var selection = rangy.getSelection();
            var message = $.trim(selection.toHtml().replace(matchSpaces, " "));

            message = this._processMessage(e, selection, message);

            var authorAndDate = this._getAuthorAndDate($(e.currentTarget));
            var id = this._getId($(e.currentTarget));
            var date = authorAndDate[1], author = authorAndDate[2];
            var topic = _.string.strRightBack(document.location.pathname, "/");

            if(!$.trim(message)) {
                this.notice(gettext("Please select a range"));
                return;
           }
            if(!this._checkIfSelectionInContainer(e, selection)) {
                this.notice(gettext("Please select a range in the same container"));
                return;
           }
            var context = {"message": message, "author": author, "date": date,
                           "id": id, "topic": topic};
            dispatcher.trigger("publish/message", context);
        },

        _processMessage: function(e, selection, message) {
            var content = $(selection.anchorNode)
                .parents(".forum_message")
                .find(".forum_message_description")
                .html();

            // strip down to text without tags and spaces
            var message_without_html = _.string.stripTags(message);
            message_without_html = _.string.clean(message_without_html);
            content = $.trim(content);
            content = _.string.stripTags(content);
            content = _.string.clean(content);

            // message doesn't need processing
            if(content == message_without_html) {
                return message
            } else if(_.string.startsWith(content, message_without_html)) {
                // add ... at end
                message = _.string.sprintf("%s...", message);
            } else if(_.string.endsWith(content, message_without_html)) {
                // add ... at start
                message = _.string.sprintf("...%s", message);
            } else {
                // add ... at start and end
                message = _.string.sprintf("...%s...", message);
            }
            return message;
        },

        _checkIfSelectionInContainer: function(e, selection) {
            /* Check to see if selected text is in the same container with
               publish button */
            var anchorN = $(selection.anchorNode)
                .parents(".forum_message_description")[0];
            var focusN = $(selection.focusNode)
                .parents(".forum_message_description")[0];
            var parents = $(e.currentTarget)
                .parents(".forum_message").find(".forum_message_description")[0];
            return (parents === anchorN) && (parents === focusN);
       },

        _getAuthorAndDate: function (self) {
            /* Get author and date
               '17 Feb 2012 17:15:50, <a href="#">admin</a>' */
             var authorAndDate = self
                .parents(".forum_message")
                .find(".forum_message_author").html();
            // remove spaces
            authorAndDate = $.trim(authorAndDate.replace(matchSpaces, " "));
            // match regular expression and fetch author and date
            return authorAndDate.match(matchDateAndAUthor);
       },

       _getId: function (self) {
            var id = self.parents(".forum_message")
                         .children("a:first").attr("name");
            return id;
       },

        notice: function(message) {
            /* Creates an jquery UI dialog and displays a message. */
            var dialog = this.make("div", {title: gettext("Alert")}, message);
            $(dialog).dialog(this.dialogOptions);
       },

        publishMessage: function(context) {
            var model = new MessageModel({
                "id": context.id,
                "content": context.message,
                "author": context.author,
                "date": context.date,
                "topic": context.topic
            });
            if(!sidebarExists()) {
                this.$el.addClass("sidebar-fix", "fast");
                new SidebarView();
            }
            new MessageView({model: model});
       },

        getTranslation: function (callback) {
            /* Get i18n translation and after render the view */
            var url = $("base").attr("href") + "../forum_publish_translations";
            $.get(url, function (data) {
                translation_dictonary = data;
                $.isFunction(callback) && callback();
           }, "json");
       }
   });

    var SidebarView = B.View.extend({
        /* Renders a sidebar if it doesn't exist with default content. */
        id: "sidebar-port",

        selector: "#middle_port",

        className: "sidebar",

        events: {
            "click .publish": "publish",
            "click .cancel": "cancel"
       },

        initialize: function () {
            this.render();
            // bind custom event for checking id sidebar is empty
            dispatcher.on("message/remove", this.checkIfSidebarEmpty, this);
       },

        render: function () {
            var publishButtons = this._renderPublishButtons();
            var self = this;

            this.$el.hide();
            this.$el.html(this.make("p", {"class": "empty"},
                gettext("No published text")
            ));
            this.$el.append(this.make("p", {"class": "title"},
                gettext("Message publish list")));
            this.$el.append(this.make("ul", {id: "message-published-list"}));
            this.$el.append(publishButtons);

            $(this.selector).after(this.$el);
            this.$el.delay(100).effect("slide", {direction: "right"}, "fast");
       },

        _renderPublishButtons: function () {
            var publishButtons = this.make("div", {"class": "publish-buttons"});
            $(publishButtons)
                .append(this.make("a", {"class": "publish"}, gettext("Publish")))
                .append(this.make("a", {"class": "cancel"}, gettext("Cancel")));
            return publishButtons;
       },

        checkIfSidebarEmpty: function () {
            /* Checks if any message_published div exists in sidebar */
            var $empty = this.$el.find(".empty");
            var $title = this.$el.find(".title");
            var $publish = this.$el.find(".publish");

            if(this.$el.find(".message-published").length == 0) {
                $empty.show();
                $title.hide();
                $publish.hide();
           } else {
                $empty.hide()
                $title.show();
                $publish.show();
           }
       },

        publish: function (e) {
            /* Serialize and publish form */
            var form = this.$el.find(":input");
            var url = $("base").attr("href") + "../forum_publish_save_object";

            $.post(url, form.serialize(), function(data) {
                if(data.status == "success") {
                    document.location = data.url;
               }
           }, "json");
       },

        cancel: function () {
            this.$el.effect("slide", {direction: "right", mode: "hide"},
                "fast", function () {$(this).remove(); });
            $(this.selector).delay(100).removeClass("sidebar-fix", "fast");
       }
   });

    var MessageView = B.View.extend({
        /* Renders a published message and bind events for it */
        tagName: "li",

        className: "message-published",

        selector: "#message-published-list",

        events: {"click .remove": "remove"},

        initialize: function () {
            this.author = this.options.author;
            this.render();
            dispatcher.trigger("message/remove");
       },

        render: function () {
            var context = {
                "id": this.model.get("id"),
                "author": this.model.get("author"),
                "date": this.model.get("date"),
                "topic": this.model.get("topic")
            };

            var content = this.model.get("content");
            var messageHtml = this.make("textarea",
                {readonly: "readonly", rows: 5, cols: 5, name: "content"},
                content);
            var contextHtml = this.make("input",
                {"type": "hidden", "value": $.toJSON(context), "name": "context"})
            var removeHtml = this.make("a", {"class": "remove"}, gettext("Remove"));

            this.$el.hide();
            this.$el.append(messageHtml, [contextHtml, removeHtml]);
            $(this.selector).append(this.$el);
            $(this.selector).find("li:last").slideDown("fast");
       },

        remove: function () {
            this.$el.slideUp("fast", function () {
                $(this).remove();
                dispatcher.trigger("message/remove");
           });
       }
   });

    $(function () {
        // only do the magic if on a forum page
        isForumPage() && new BoardView();
   });

}(Backbone, _, rangy));
