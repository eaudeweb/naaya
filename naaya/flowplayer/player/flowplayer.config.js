/** Configure flowplayer
 * @param site Absolute url to site;
 * @param container DOM element id were player will be inserted;
 * @param movie URL to Flash Video File to be played;
 * @param subtitle URL to subtitle file.
 * @return nothing.
 */
var flowplayer_config = function(site, container, movie, subtitle, image,
        autoPlay, autoHide){
  if(!window.flowplayer){
    // flowplayer js not loaded
    return;
  }

  if (!autoPlay || autoPlay == 'false') { // default value for autoPlay
      var autoPlay = false;
  }
  if (autoHide == 'false') {
      var autoHide = false;
  }
  else {
        var autoHide = true;
  }

  var player_url = site + '/flowplayer.swf';
//  var audio_url = site + '/flowplayer.audio.swf';
  var controls_url = site + '/flowplayer.controls.swf';
  container = container || 'player';

  // Config
  if (image){
	var config = {
		playlist: [
			{
				url: image,
				scaling: 'scale' //'orig' as an alternative
			},
			{
				url: movie,
				autoPlay: autoPlay,
				coverImage: { url: image, scaling: 'scale' }
			}
		],
		plugins: {
            controls: { autoHide: autoHide, fullscreen: autoHide, height: 30}
		}
	};
  }
  else{
	var config = {
		playlist: [
			{
				url: movie,
				autoPlay: autoPlay,
				autoBuffering: true
			}
		],
		plugins: {
            controls: {autoHide: autoHide, fullscreen: autoHide, height: 30}
		}
	};
  }

  // Subtitle
  if(subtitle){
    jQuery.get(subtitle, {}, function(data){
      if(data){
		if (image){
			config.playlist[1].captionUrl = subtitle;
		}
		else{
			config.playlist[0].captionUrl = subtitle;
		}
        var captions_url = site + '/flowplayer.captions.swf';
        var content_url = site + '/flowplayer.content.swf';
        if(captions_url && content_url){
          // Captions plugin
          config.plugins.captions = {
            url: captions_url,
            captionTarget: 'content',
            button: {
              width: 45,
              height: 15,
              right: 5,
              bottom: 30,
              label: 'Subtitle'
            }
          };

          // Content plugin
          config.plugins.content = {
            url: content_url,
            bottom: 40,
            height:40,
            backgroundColor: 'transparent',
            backgroundGradient: 'low',
            borderRadius: 4,
            border: 0,
            textDecoration: 'outline',
            style: {
              body: {
                fontSize: 14,
                fontFamily: 'Arial',
                textAlign: 'center',
                color: '#ffffff'
              }
            }
          };
        }
      }
      flowplayer(container, player_url, config);
    });
  }else{
    flowplayer(container, player_url, config);
  }
};
