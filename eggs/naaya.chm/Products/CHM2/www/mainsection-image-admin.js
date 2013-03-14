$(function () {
	$('#main_section_image').show();
    var upload_button = $("#picture_upload_button"),
        url_input = $("#upload_picture_url"),
        image_holder = $("#main_section_picture");

    var img_height = $("#height").val(),
        img_width = $("#width").val();

    var jcrop_api, ajax_uploader;
    var image_ext_test = /^(jpg|png|jpeg|gif)$/i;

    var setupUploadButton = function () {
        ajax_uploader = new AjaxUpload(upload_button, {
            action: "upload_maintopic_temp_image",
            name: "upload_file",
            responseType: "json",

            onSubmit : function (file, ext) {
                if (!ext && image_ext_test.test(ext)) {
                    // extension is not allowed
                    alert("Error: invalid file extension");
                    // cancel upload
                    return false;
                };

                image_holder.empty();
                upload_button.text("Uploading...");
                ajax_uploader.disable();
            },

            onComplete: function (file, response) {
                handleSectionImage(response);
                ajax_uploader.enable();
            }
        });
    };

    var setCoords = function (c) {
        // c.x, c.y, c.x2, c.y2, c.w, c.h
        $("#x1").val(c.x);
        $("#y1").val(c.y);
        $("#x2").val(c.x2);
        $("#y2").val(c.y2);
    };

    var doCrop = function () {
        $("img", image_holder).Jcrop({
            allowMove: true,
            onSelect: setCoords,
            bgColor: "black",
            bgOpacity: .4,
            setSelect: [$("#x2").val(),
                        $("#y2").val(),
                        $("#x1").val(),
                        $("#y1").val()],
            aspectRatio: img_width/img_height
        }, function () {
            jcrop_api = this;
        });
    };

    var getSectionImage = function () {
        $.get("load_current_maintopic_image", {
            "name": $(this).val(),
            "timestamp": new Date().getTime()
        }, handleSectionImage);
    };

    var handleSectionImage = function (data) {
        if(data.error) {
            return;
        }

        upload_button.text(gettext('Replace image'));
        url_input.val(data.url);
        image_holder.html($("<img />").attr("src", data.url));

        setCoords(data);
        doCrop();
    };

    var changeDimension = function (e) {
        if(e.keyCode == 13 || e.type == "focusout") {
            e.preventDefault();
            var val = $(this).val();

            if($(this).attr("id") == "width") {
                if(img_width === val) {return;}
                img_width = val;
            } else {
                if(img_height === val) {return;}
                img_height = $(this).val();
            }

            jcrop_api.destroy();
            doCrop();
        }
    };

    // events
    $("#main-section-image-selection-box").on("change", getSectionImage)
                                          .change();
    $("#width, #height").on("focusout keydown", changeDimension);
    setupUploadButton();
});

