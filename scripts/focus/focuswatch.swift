// NAVI focus watcher: proves NAVI never takes over the Mac.
//
// Logs, one JSON line each, every time an app comes to the front, and every on-screen window owned by NAVI's browser.
// NAVI's browser is known by where it lives on disk (Playwright's browsers in ms-playwright, or anything inside the
// NAVI folder), never by its name, so the user's own Chrome and its helpers never count. Window owners need no
// Screen Recording permission.
//
//   navi-focuswatch <seconds> [--give-back-at <s>]...
//
// --give-back-at puts the app that was in front at the start back in front at that second (what the user does when
// they click back into their own app), so a test can see whether anything jumps in front again afterwards.
import AppKit
import CoreGraphics
import Foundation

let args = CommandLine.arguments
guard args.count >= 2, let duration = Double(args[1]) else {
  FileHandle.standardError.write("usage: navi-focuswatch <seconds> [--give-back-at <s>]...\n".data(using: .utf8)!)
  exit(2)
}
var giveBack: [Double] = []
var i = 2
while i < args.count {
  if args[i] == "--give-back-at", i + 1 < args.count, let s = Double(args[i + 1]) { giveBack.append(s); i += 2 } else { i += 1 }
}

let t0 = Date()
func now() -> String { String(format: "%.2f", Date().timeIntervalSince(t0)) }
func emit(_ d: [String: Any]) {
  var d = d
  d["t"] = now()
  if let data = try? JSONSerialization.data(withJSONObject: d, options: [.sortedKeys]), let s = String(data: data, encoding: .utf8) {
    print(s)
    fflush(stdout)
  }
}
func describe(_ app: NSRunningApplication?) -> [String: Any] {
  ["app": app?.localizedName ?? "?", "bundle": app?.bundleIdentifier ?? "", "pid": Int(app?.processIdentifier ?? 0)]
}
func pathOf(_ pid: Int) -> String {
  var buf = [CChar](repeating: 0, count: 4096)
  return proc_pidpath(Int32(pid), &buf, UInt32(buf.count)) > 0 ? String(cString: buf) : ""
}
let naviFolder = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().path
func isNavi(_ pid: Int) -> Bool {
  let p = pathOf(pid)
  return p.contains("/ms-playwright/") || (!naviFolder.isEmpty && p.hasPrefix(naviFolder + "/"))
}

let first = NSWorkspace.shared.frontmostApplication
emit(["event": "start", "front": describe(first)])

NotificationCenter.default.addObserver(forName: nil, object: nil, queue: nil) { _ in }
NSWorkspace.shared.notificationCenter.addObserver(forName: NSWorkspace.didActivateApplicationNotification, object: nil, queue: .main) { n in
  let app = n.userInfo?[NSWorkspace.applicationUserInfoKey] as? NSRunningApplication
  var d = describe(app)
  d["event"] = "activate"
  let pid = Int(app?.processIdentifier ?? 0)
  d["navi"] = isNavi(pid)
  d["path"] = pathOf(pid)
  emit(d)
}

var seen = Set<Int>()
Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { _ in
  guard let list = CGWindowListCopyWindowInfo([.optionOnScreenOnly, .excludeDesktopElements], kCGNullWindowID) as? [[String: Any]] else { return }
  for w in list {
    let owner = w[kCGWindowOwnerName as String] as? String ?? ""
    let num = w[kCGWindowNumber as String] as? Int ?? 0
    let layer = w[kCGWindowLayer as String] as? Int ?? 0
    let pid = w[kCGWindowOwnerPID as String] as? Int ?? 0
    guard !seen.contains(num), isNavi(pid) else { continue }
    seen.insert(num)
    let b = w[kCGWindowBounds as String] as? [String: Any] ?? [:]
    emit(["event": "window", "owner": owner, "pid": pid, "layer": layer, "path": pathOf(pid),
          "w": b["Width"] ?? 0, "h": b["Height"] ?? 0])
  }
}
for s in giveBack {
  DispatchQueue.main.asyncAfter(deadline: .now() + s) {
    if let id = first?.bundleIdentifier {
      let p = Process()
      p.executableURL = URL(fileURLWithPath: "/usr/bin/open")
      p.arguments = ["-b", id]
      try? p.run()
      emit(["event": "give-back", "to": id])
    }
  }
}
DispatchQueue.main.asyncAfter(deadline: .now() + duration) {
  emit(["event": "end", "front": describe(NSWorkspace.shared.frontmostApplication)])
  exit(0)
}
NSApplication.shared.setActivationPolicy(.prohibited)
RunLoop.main.run()
