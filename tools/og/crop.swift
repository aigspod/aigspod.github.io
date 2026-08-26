import Foundation
import Quartz
// crop.swift <in> <out.png> <x> <y> <w> <h>
let a = CommandLine.arguments
let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: a[1]) as CFURL, nil)!
let img = CGImageSourceCreateImageAtIndex(src, 0, nil)!
let rect = CGRect(x: Int(a[3])!, y: Int(a[4])!, width: Int(a[5])!, height: Int(a[6])!)
let cropped = img.cropping(to: rect)!
let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: a[2]) as CFURL,
                                           "public.png" as CFString, 1, nil)!
CGImageDestinationAddImage(dest, cropped, nil)
CGImageDestinationFinalize(dest)
print("\(cropped.width)x\(cropped.height)")
