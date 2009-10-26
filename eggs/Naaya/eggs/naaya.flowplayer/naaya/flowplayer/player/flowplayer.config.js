/** Configure flowplayer
 * @param site Absolute url to site;
 * @param container DOM element id were player will be inserted;
 * @param movie URL to Flash Video File to be played;
 * @param subtitle URL to subtitle file.
 * @return nothing.
 */
var flowplayer_config = function(site, container, movie, subtitle){
  if(!window.flowplayer){
    // flowplayer js not loaded
    return;
  }

  var player_url = site + '/flowplayer.swf';
  container = container || 'player';

  // Config
  var config = {
    clip: {
      autoPlay: false,
      autoBuffering: false,
      url: movie
    },
    plugins: {}
  };

  // Subtitle
  if(subtitle){
    jQuery.get(subtitle, {}, function(data){
      if(data){
        config.clip.captionUrl = subtitle;
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
