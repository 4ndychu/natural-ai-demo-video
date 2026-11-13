// web-demuxer is only used by Recordly for video wallpapers and webcam clips. NAVI uses neither, so the
// package isn't installed; this stands in for it at build time. Recordly's files are not changed.
export class WebDemuxer {
  constructor() { throw new Error("web-demuxer isn't installed in NAVI (video wallpapers and webcams aren't used)"); }
}
export default WebDemuxer;
