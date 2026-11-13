// NAVI privacy: read the text in images with Apple's built-in Vision framework (nothing to install).
// Usage: navi-ocr <image> [<image> ...]   One JSON line per image:
//   {"image": path, "width": w, "height": h, "lines": [{"text", "conf", "box": [x,y,w,h], "words": [{"text","box"}]}]}
// Boxes are in image pixels, top-left origin. Language correction is off: keys and codes aren't words.
import Foundation
import Vision
import ImageIO

func box(_ r: CGRect, _ w: Int, _ h: Int) -> [Int] {
    let x = r.minX * CGFloat(w), y = (1 - r.maxY) * CGFloat(h)
    return [Int(x.rounded()), Int(y.rounded()), Int((r.width * CGFloat(w)).rounded()), Int((r.height * CGFloat(h)).rounded())]
}

for path in CommandLine.arguments.dropFirst() {
    guard let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: path) as CFURL, nil),
          let img = CGImageSourceCreateImageAtIndex(src, 0, nil) else {
        print("{\"image\": \(String(reflecting: path)), \"error\": \"unreadable\"}"); continue
    }
    let w = img.width, h = img.height
    let req = VNRecognizeTextRequest()
    req.recognitionLevel = .accurate
    req.usesLanguageCorrection = false
    req.minimumTextHeight = 0.006
    try? VNImageRequestHandler(cgImage: img, options: [:]).perform([req])
    var lines: [[String: Any]] = []
    for obs in req.results ?? [] {
        guard let c = obs.topCandidates(1).first else { continue }
        var words: [[String: Any]] = []
        let s = c.string
        var i = s.startIndex
        while i < s.endIndex {
            while i < s.endIndex && s[i] == " " { i = s.index(after: i) }
            var j = i
            while j < s.endIndex && s[j] != " " { j = s.index(after: j) }
            if i < j, let b = try? c.boundingBox(for: i..<j) {
                words.append(["text": String(s[i..<j]), "box": box(b.boundingBox, w, h),
                              "start": s.distance(from: s.startIndex, to: i)])
            }
            i = j
        }
        lines.append(["text": s, "conf": Double(c.confidence), "box": box(obs.boundingBox, w, h), "words": words])
    }
    let out: [String: Any] = ["image": path, "width": w, "height": h, "lines": lines]
    let data = try! JSONSerialization.data(withJSONObject: out, options: [])
    print(String(data: data, encoding: .utf8)!)
}
