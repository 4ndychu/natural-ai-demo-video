// NAVI polish step: renders NAVI's raw browser frames through Recordly's own export renderer.
//
// Recordly (https://github.com/webadderallorg/Recordly), Copyright (C) 2026 webadderall, AGPL-3.0.
// Every file under ../recordly/ is Recordly's, copied unedited at the commit in ../recordly/PINNED.json.
// This file only feeds Recordly's code its input: the frames, the cursor log and (for Recordly style)
// the zooms that Recordly's own auto-zoom button would add. Settings come from Recordly's own defaults.
import { FrameRenderer } from "@/lib/exporter/modernFrameRenderer";
import { normalizeProjectEditor } from "@/components/video-editor/projectPersistence";
import { DEFAULT_EDITOR_PREFERENCES } from "@/components/video-editor/editorPreferences";
import { buildExportRenderOptions } from "@/components/video-editor/export/buildExportRenderOptions";
import { buildInteractionZoomSuggestions } from "@/components/video-editor/timeline/zoomSuggestionUtils";
import { DEFAULT_ZOOM_BLOCK_DURATION_MS } from "@/components/video-editor/timeline/core/constants";
import { clampFocusToDepth, DEFAULT_AUTO_ZOOM_DEPTH } from "@/components/video-editor/types";
import { DESKTOP_WALLPAPER } from "@/lib/desktopWallpaper";
import { DEFAULT_WALLPAPER_PATH } from "@/lib/wallpapers";

type Job = {
  style: "casual" | "recordly";
  width: number; height: number;            // output size
  videoWidth: number; videoHeight: number;  // raw frame size
  totalMs: number;
  telemetry: any[];                         // Recordly CursorTelemetryPoint[], 0..1 of the frame
  zoomRegions?: any[];                      // only to reproduce an old test; normally Recordly picks them
};

let renderer: any, job: Job;

// A fresh Recordly install: the editor's appearance comes from DEFAULT_EDITOR_PREFERENCES, which are
// normalizeProjectEditor({}) plus app-level settings (useAppearanceState.ts). The timeline of a new project
// comes from normalizeProjectEditor({}).
function freshRecordly() {
  const project = normalizeProjectEditor({} as any) as any;
  const prefs = DEFAULT_EDITOR_PREFERENCES as any;
  const appearance = {
    ...project, ...prefs,
    // useAppearanceState: "desktop-wallpaper" shows the default wallpaper until the OS answers (it never does here)
    wallpaper: prefs.wallpaper === DESKTOP_WALLPAPER ? DEFAULT_WALLPAPER_PATH : prefs.wallpaper,
    resolvedWebcamVideoUrl: null,
  };
  return { project, appearance };
}

// What Recordly's "auto zoom" button adds (useTimelineZoomActions.handleSuggestZooms + useZoomRegionCommands.handleZoomSuggested).
function recordlyAutoZooms(telemetry: any[], totalMs: number, clipRegions: any[]) {
  const result = buildInteractionZoomSuggestions({
    cursorTelemetry: telemetry, clipRegions, totalMs,
    defaultDurationMs: Math.min(DEFAULT_ZOOM_BLOCK_DURATION_MS, totalMs), reservedSpans: [],
  });
  return result.suggestions.map((s: any, i: number) => ({
    id: `zoom-${i + 1}`, startMs: Math.round(s.start), endMs: Math.round(s.end), depth: DEFAULT_AUTO_ZOOM_DEPTH,
    focus: clampFocusToDepth(s.focus, DEFAULT_AUTO_ZOOM_DEPTH), focusSpace: "source", mode: "auto",
  }));
}

async function init(j: Job) {
  job = j;
  const { project, appearance } = freshRecordly();
  const clipRegions = project.clipRegions ?? [];
  const zoomRegions = j.zoomRegions ?? (j.style === "recordly" ? recordlyAutoZooms(j.telemetry, j.totalMs, clipRegions) : []);
  const opts: any = buildExportRenderOptions({
    appearance, timeline: project, effectiveSpeedRegions: [], effectiveZoomRegions: zoomRegions,
    effectiveCursorTelemetry: j.telemetry, effectiveShowCursor: appearance.showCursor,
    previewWidth: j.width, previewHeight: j.height, shadowIntensity: appearance.shadowIntensity, onProgress: () => {},
  } as any);
  // The same fields, in the same order, that Recordly's modernExportPrepare.ts passes to its FrameRenderer.
  renderer = new FrameRenderer({
    timelineEffects: opts.clipRegions !== undefined, width: j.width, height: j.height, preferredRenderBackend: "webgl",
    wallpaper: opts.wallpaper, zoomRegions: opts.zoomRegions, showShadow: opts.showShadow, shadowIntensity: opts.shadowIntensity,
    backgroundBlur: opts.backgroundBlur, zoomMotionBlur: opts.zoomMotionBlur, zoomMotionBlurTuning: opts.zoomMotionBlurTuning,
    connectZooms: opts.connectZooms, zoomInDurationMs: opts.zoomInDurationMs, zoomInOverlapMs: opts.zoomInOverlapMs,
    zoomOutDurationMs: opts.zoomOutDurationMs, connectedZoomGapMs: opts.connectedZoomGapMs,
    connectedZoomDurationMs: opts.connectedZoomDurationMs, zoomInEasing: opts.zoomInEasing, zoomOutEasing: opts.zoomOutEasing,
    connectedZoomEasing: opts.connectedZoomEasing, borderRadius: opts.borderRadius, padding: opts.padding,
    cropRegion: opts.cropRegion, webcam: opts.webcam, webcamUrl: opts.webcamUrl, videoWidth: j.videoWidth, videoHeight: j.videoHeight,
    annotationRegions: opts.annotationRegions, autoCaptions: opts.autoCaptions, autoCaptionSettings: opts.autoCaptionSettings,
    speedRegions: opts.speedRegions, previewWidth: opts.previewWidth, previewHeight: opts.previewHeight,
    cursorTelemetry: opts.cursorTelemetry, showCursor: opts.showCursor, cursorStyle: opts.cursorStyle, cursorSize: opts.cursorSize,
    cursorSmoothing: opts.cursorSmoothing, cursorSpringStiffnessMultiplier: opts.cursorSpringStiffnessMultiplier,
    cursorSpringDampingMultiplier: opts.cursorSpringDampingMultiplier, cursorSpringMassMultiplier: opts.cursorSpringMassMultiplier,
    cameraSpringStiffnessMultiplier: opts.cameraSpringStiffnessMultiplier, cameraSpringDampingMultiplier: opts.cameraSpringDampingMultiplier,
    cameraSpringMassMultiplier: opts.cameraSpringMassMultiplier, cursorMotionBlur: opts.cursorMotionBlur,
    cursorClickEffect: opts.cursorClickEffect, cursorClickEffectColor: opts.cursorClickEffectColor,
    cursorClickEffectScale: opts.cursorClickEffectScale, cursorClickEffectOpacity: opts.cursorClickEffectOpacity,
    cursorClickEffectDurationMs: opts.cursorClickEffectDurationMs, cursorClickBounce: opts.cursorClickBounce,
    cursorClickBounceDuration: opts.cursorClickBounceDuration, cursorSway: opts.cursorSway, cursorIdleHide: opts.cursorIdleHide,
    zoomSmoothness: opts.zoomSmoothness, zoomClassicMode: opts.zoomClassicMode,
  });
  await renderer.initialize();
  const settings = Object.fromEntries(["cursorStyle", "cursorSize", "cursorSway", "cursorIdleHide", "cursorClickEffect", "cursorClickBounce",
    "zoomMotionBlur", "zoomInDurationMs", "zoomOutDurationMs", "borderRadius", "padding", "wallpaper", "shadowIntensity"].map((k) => [k, opts[k]]));
  return { settings, zoomRegions, backend: renderer.getRendererBackend?.() };
}

// Raw frames are change-driven: frame i is shown until frame i+1 arrives.
// postBlur: NAVI's privacy frame scan (scripts/privacy): boxes in raw-frame pixels, blurred in the raw frame
// itself before Recordly draws it, so a zoom can never show what's under them.
type Box = { t0: number; t1: number; box: [number, number, number, number] };
let frames: Array<[number, string]> = [], current = -1, bitmap: ImageBitmap | null = null, postBlur: Box[] = [];
function setFrames(f: Array<[number, string]>, blur: Box[] = []) { frames = f; postBlur = blur; }
async function blurBoxes(src: ImageBitmap, boxes: Box[]) {
  const c = new OffscreenCanvas(src.width, src.height), g = c.getContext("2d")!;
  g.drawImage(src, 0, 0);
  for (const { box: [x, y, w, h] } of boxes) {
    g.save(); g.beginPath(); g.rect(x, y, w, h); g.clip();
    g.filter = `blur(${Math.max(12, Math.round(h * 0.45))}px)`;
    g.drawImage(src, 0, 0); g.drawImage(src, 0, 0);  // twice: no faint copy of the text survives at the edges
    g.restore();
  }
  src.close();
  return createImageBitmap(c);
}
async function sourceAt(ms: number) {
  let lo = 0, hi = frames.length - 1, idx = 0;
  while (lo <= hi) { const m = (lo + hi) >> 1; if (frames[m][0] * 1000 <= ms) { idx = m; lo = m + 1; } else hi = m - 1; }
  if (idx !== current) {
    const blob = await (await fetch(frames[idx][1])).blob();
    let next = await createImageBitmap(blob);
    const t = frames[idx][0], boxes = postBlur.filter((b) => b.t0 <= t + 1e-6 && t < b.t1 - 1e-6);
    if (boxes.length) next = await blurBoxes(next, boxes);
    bitmap?.close(); bitmap = next; current = idx;
  }
  return bitmap!;
}

async function frame(ms: number, quality = 0.92): Promise<string> {
  const us = Math.round(ms * 1000);
  const vf = new VideoFrame(await sourceAt(ms), { timestamp: us });
  try { await renderer.renderFrame(vf, us, us, undefined, us); } finally { vf.close(); }
  const canvas: HTMLCanvasElement = renderer.getCanvas();
  const blob: Blob = await new Promise((r) => canvas.toBlob((b) => r(b!), "image/jpeg", quality));
  const buf = new Uint8Array(await blob.arrayBuffer());
  let s = ""; for (let i = 0; i < buf.length; i += 0x8000) s += String.fromCharCode(...buf.subarray(i, i + 0x8000));
  return btoa(s);
}

async function frames_(fromMs: number, stepMs: number, count: number) {
  const out: string[] = [];
  for (let i = 0; i < count; i++) out.push(await frame(fromMs + i * stepMs));
  return out;
}

(window as any).navi = { init, setFrames, frames: frames_ };
