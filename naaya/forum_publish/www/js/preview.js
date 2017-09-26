(function(B, _) {

    var isPreviewPage = function () {return $(".forum-topic-container").length > 0};

    var ForumPublishView = B.View.extend({
        el: "#middle_port",

        events: {
            "click #forum-preview-save": "dialog",
            "click #forum-preview-clear": "clear",
            "click .preview-remove": "remove"
        },

        initialize: function () {
            this.topic = $("input[name=topic]").val();
            this.base_url = $("input[name=base_url]").val();
            this.append = false;

            var documents = [];
            $("#doc-name").find("option").each(function () {
                documents.push($(this).text());
            });
            this.documents = documents;
        },

        dialog: function (e) {
            var self = this;
            $("#forum-preview-save-dialog").find("select").combobox();
            $("#forum-preview-save-dialog")
                .find(".ui-autocomplete-input")
                .on("keydown", _.bind(this.keydown, this))
                .on("keyup focus", _.bind(this.change, this));

            $("#forum-preview-save-dialog").dialog({
                modal: true,
                height: 180,
                width: 500,

                buttons: {
                    "Save new document": function () {
                        var file = "";

                        if(self.append) {
                            file = $("#forum-preview-save-dialog")
                                       .find("select")
                                       .val();
                        } else {
                            file = $.trim($("#forum-preview-save-dialog")
                                    .find(".ui-autocomplete-input")
                                    .val());
                        }
                        file && self.save(file);
                    }
                }

            });
        },

        save: function (file) {
            $("#forum-preview-container").find(".preview-actions").remove();
            var content = $("#forum-preview-container").html();
            var url = _.string.sprintf("%s/forum_publish_save", this.base_url);
            $.post(url, {
                "topic": this.topic,
                "content": content,
                "filename": file
            }, function (data) {
                document.location = data.url;
            }, "json");
        },

        clear: function () {
            var self = this;
            if(!confirm("Are you sure you want to clear this document?")) {
                return;
            }
            var url = _.string.sprintf("%s/forum_publish_clear_preview",
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
            var timestamp = target.data("timestamp");
            var topic = this.topic;

            $.post(url, {"timestamp": timestamp, "topic": topic}, function () {
                target.parents(".forum-topic-container").slideUp("slow");
            });
        },

        change: function (e) {
            var that = $(e.currentTarget);
            var button = $(".ui-dialog-buttonpane").find("button span");
            var val = $.trim(that.val());

            if(_.include(this.documents, val) && val !== "") {
                button.text("Append to selected document");
                this.append = true;
            } else {
                button.text("Save new document");
                this.append = false;
            }
        },

        keydown: function (e) {
            if(e.keyCode == 13) {
                e.preventDefault();
            }
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

