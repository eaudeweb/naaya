/** Configure flowplayer
 * @param containerid DOM element id were player will be inserted;
 * @param movie URL to Flash Video File to be played;
 * @param subtitle URL to subtitle file.
 * @return nothing.
 */
var flowplayer_config = function(containerid, movie, subtitle, image, autoPlay){
  if(!window.flowplayer){
    // flowplayer js not loaded
    return;
  }

  if (!autoPlay || autoPlay == 'false') { // default value for autoPlay
      var autoplay = false;
  }
  else{
      var autoplay = true;
  }

  containerid = containerid || 'player';
  container = document.getElementById(containerid);

  // Config
  config= {
    clip: {
        sources: [{type: "video/mp4", src: movie}],
        subtitles: [{
            "default": true,
            kind: "subtitles",
            srclang: "en",
            label: "Subtitles ON",
            src: subtitle
        }]
    },
    splash: image,
  };
  flowplayer(container, config);
};

