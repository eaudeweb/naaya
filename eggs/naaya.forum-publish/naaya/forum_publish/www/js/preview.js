(function(B, _) {

    var isPreviewPage = function () {return $(".forum-topic-container").length > 0};

    var ForumPublishView = B.View.extend({
        el: "#middle_port",

        events: {
            "click #forum-preview-save": "save",
            "click #forum-preview-clear": "clear",
            "click .preview-remove": "remove"
        },

        initialize: function () {
            this.topic = $("input[name=topic]").val();
            this.base_url = $("input[name=base_url]").val();
        },

        save: function (e) {
            var target = $(e.currentTarget);
            $("#forum-preview-container").find(".preview-actions").remove();
            var content = $("#forum-preview-container").html();
            var url = _.string.sprintf("%s/forum_publish_save", this.base_url);
            $.post(url, {"topic": this.topic, "content": content}, function (data) {
                document.location = data.url;
            }, "json");
        },

        clear: function () {
            var self = this;
            if(!confirm("Are you sure you want to clear this document?")) {
                return;
            }
            var url = _.string.sprintf("%s/forum_publish_clear_objects",
                                       this.base_url);
            $.get(url, {"topic": this.topic}, function (data) {
                self._handleClear();
            });
        },

        remove: function (e) {
            if(!confirm("Are you sure you want to remove this post?")) {
                return;
            }
            var target = $(e.currentTarget);
            var url = _.string.sprintf("%s/forum_publish_remove_object",
                                       this.base_url);
            var id = target.data("id");
            var topic = this.topic;

            $.post(url, {"id": id, "topic": topic}, function () {
                target.parents(".forum-topic-container").slideUp("slow");
            });
        },

        _handleClear: function () {
            var self = this;
            $(".forum-topic-container").slideUp("slow", function () {
                 window.location = _.string.sprintf("%s/%s", self.base_url,
                                                    self.topic);
            });
        }
    });

    $(function () {
        isPreviewPage && new ForumPublishView();
    });

})(Backbone, _);

