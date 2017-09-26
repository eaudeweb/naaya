(function(B, _) {

    var isDocPage = function () {return $(".doc-content").length > 0;};

    // http://www.colourlovers.com/palette/462628/Blazin_Jell-O_Rainbo
    // http://www.colourlovers.com/palette/254301/[Chic]_-_Mellow
    var colors = [
        "#11644D", // Gemma
        "#5A2E2E", // Mellow Meadow
        "#EC5E0C", // Orange Jell
        "#F78F1E", // Yellow Jell-O
        "#272D4D", // Green Jell
        "#6D2243", // Blazin Blue Jell
    ];
    var defaultColor = "#333";

    var AuthorModel = B.Model.extend({
        defaults: {name: null, color: null}
   });
    var AuthorCollection = B.Collection.extend({
        model: AuthorModel
   });

    window.authors = new AuthorCollection(); // collection of authors

    var SidebarView = B.View.extend({
        id: "sidebar-port",

        className: "sidebar",

        selector: "#middle_port",

        initialize: function () {
            this.render();
       },

        render: function () {
            var authorLists = this.make("ul", {"class": "doc-author-list"});
            var self = this;

            this.collection.each(function (m) {
                $(authorLists).append(self.make("li", {
                        "class": "author",
                        style: "color:" + m.get("color")
                   }, self.make("span", {}, m.get("name")))
                );
           });

            this.$el.html(authorLists);
            $(this.selector).after(this.$el);
       }
   });

    var DocumentView = B.View.extend({
        /* Fetch all authors and create a collection */
        el: "#middle_port",

        events: {
            "mouseover .doc-content": "hoverAuthor",
            "mouseout .doc-content": "unhoveAuthor"
       },

        initialize: function () {
            this.fetchAuthors();
            this.render();
       },

        render: function () {

           // find text for each author and color it
            authors.each(function (m) {
                $(".doc-author:contains(" + m.get("name") + ")")
                    .parents(".doc-date").prev(".doc-content")
                    .css("color", m.get("color"));
           });

            this.$el.find(".doc-date").hide();
            this.$el.addClass("sidebar-fix");

            new SidebarView({collection: authors});
       },

        fetchAuthors: function () {
            /* Fetch all authors from document and added them to collection */
            var color_list = _.clone(colors);
            var author_list = [];
            this.$el.find(".doc-author").each(function () {
                var color = color_list.shift() || defaultColor;
                var name = $(this).text();
                if(!_.include(author_list, name)) {
                    authors.add({name: name, color: color});
                    author_list.push(name);
               }
           });
       },

        hoverAuthor: function (e) {
            var author = $(e.currentTarget).next(".doc-date").find(".doc-author")
                                           .text();
            $(".doc-author-list").find("li:contains(" + author + ")")
                                 .addClass("hover");
       },

        unhoveAuthor: function () {
            $(".doc-author-list").find("li").removeClass("hover");
       }

   });

    $(function() {
        // only do the magic if on a document page
        isDocPage() && new DocumentView();
   });

}(Backbone, _));
