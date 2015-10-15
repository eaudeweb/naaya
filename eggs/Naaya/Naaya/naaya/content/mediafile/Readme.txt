NyMediaFile
===========
- A video file container, that display them using an HTML5 video player
FlowPlayer (https://flowplayer.org/).

1 Features
==========
- Upload and play almost any video format in all browsers that support
  HTML5;
- Store video files outside ZODB;
- Subtitles for every site language;
- Download video file.

2 Getting started
=================
- Login into your Naaya site and navigate to an existing Folder, or add one.
  Add a new Media File. If all the required tools correctly installed, you'll
  be able to upload almost all known video formats
  (see http://en.wikipedia.org/wiki/FFmpeg for more details), if not, you'll
  be able to upload only mp4 video files.

- After the file was successfully uploaded, you can add subtitles in edit form
  for every language that site supports. The subtitle format must be SubRip
  (see http://en.wikipedia.org/wiki/Subrip for more details). You can easily
  create SubRip subtitles for your movies using Subtitle Workshop
  (see http://www.urusoft.net/products.php?cat=sw&lang=1 for more details).

- As playing video files on web requires video conversion on server side, the
  video will not be available until the conversion is complete, therefore a
  message will annotate this.

- If any error occurs in video conversion process, a generic message will
  annotate this. For more details about errors occurred check the conversion
  log file located in the same directory as original video file.
