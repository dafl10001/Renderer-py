from vector import vec2, vec3, vec4, transform3
import math
import time
import sys
import multiprocessing

FOV = math.radians(90)


def drawPixel(pixels, width, height, x, y, brightness, color=(0, 0, 0)):
    if 0 <= x < width and 0 <= y < height:
        idx = (int(y) * width + int(x)) * 3

        r = max(0, min(255, int(255 * (1 - brightness) + color[0] * brightness)))
        g = max(0, min(255, int(255 * (1 - brightness) + color[1] * brightness)))
        b = max(0, min(255, int(255 * (1 - brightness) + color[2] * brightness)))
        
        pixels[idx:idx+3] = bytes([r, g, b])

def line(p0, p1, pixels, width, height):
    x0, y0 = p0.x, p0.y
    x1, y1 = p1.x, p1.y
    
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0
    gradient = dy / dx if dx != 0 else 1.0

    intery = y0
    for x in range(int(x0), int(x1) + 1):
        f_part = intery - int(intery)
        inv_f_part = 1 - f_part
        
        if steep:
            drawPixel(pixels, width, height, int(intery), x, inv_f_part)
            drawPixel(pixels, width, height, int(intery) + 1, x, f_part)
        else:
            drawPixel(pixels, width, height, x, int(intery), inv_f_part)
            drawPixel(pixels, width, height, x, int(intery) + 1, f_part)
        intery += gradient

def drawGeometry3D(pixels, width, height, vertices: list[vec3], edges: list[tuple[int, int]], k):
    projected = []
    scale = width * 0.3
    offset = vec2(width / 2, height / 2)

    for v in vertices:
        p = v.map2(k)
        screen_pos = (p * scale) + offset
        projected.append(screen_pos)

    for edge in edges:
        line(projected[edge[0]], projected[edge[1]], pixels, width, height)

def drawGeometry4D(pixels, width, height, vertices: list[vec4], edges: list[tuple[int, int]], k4, k3):
    vertices_3d = []
    for v in vertices:
        vertices_3d.append(v.map3(k4))
    
    drawGeometry3D(pixels, width, height, vertices_3d, edges, k3)


def rotate4D(v: vec4, theta, phi):
    c, s = math.cos(theta), math.sin(theta)
    x = v.x * c - v.w * s
    w = v.x * s + v.w * c
    v = vec4(x, v.y, v.z, w)

    c, s = math.cos(phi), math.sin(phi)
    y = v.y * c - v.w * s
    w = v.y * s + v.w * c
    return vec4(v.x, y, v.z, w)


def drawFrame(width, height, objects: list[tuple[list[vec3], list[tuple[int, int]]]]):
    header = f"P6\n{width} {height}\n255\n".encode()
    pixels = bytearray([255, 255, 255] * height * width)

    for p, e in objects:
        drawGeometry3D(pixels, width, height, p, e, 1 / math.tan(FOV / 2))

    return header + pixels


def renderBatch(batch_idx, CoreID, CoreAmount, framecount, frameCountSize, WIDTH, HEIGHT, start, tesseract_points, tesseract_edges):
    frames = []
    
    for j in range(50):
        i = (batch_idx * 50) + j
        
        current_frame = i * CoreAmount + CoreID
        
        if current_frame >= framecount:
            break

        angle = math.radians(current_frame * 2) 
        rotated_4d = [rotate4D(v, angle, angle * 0.5) for v in tesseract_points]
        vertices_3d = [v.map3(3) for v in rotated_4d]

        now = time.time()

        cubetransform = transform3(vec3(0, 0, 5), vec3(3, 3, 3), vec3(angle * 0.2, angle * 0.3, 0))
        final_vertices = cubetransform.mapVertices(vertices_3d)

        percentile = round(100 * ((current_frame + 1) / framecount))
        percentSize = len(str(percentile))
        iSize = len(str(current_frame))

        if CoreID == 0:
            fps = round(i / (now - start) * CoreAmount) if (now - start) > 0 else 0
            print("\033[1A" + " " * 100)
            print(f"\033[1ADrawing frame #{current_frame}{' ' * (frameCountSize - iSize)} ({' ' * (3 - percentSize)}{percentile}%) ({fps}fps) with {CoreAmount} cores")
        
        frames.append((current_frame, drawFrame(WIDTH, HEIGHT, [(final_vertices, tesseract_edges)])))
    return frames


def runCore(CoreID, CoreAmount, framecount, frameCountSize, WIDTH, HEIGHT, start, tesseract_points, tesseract_edges):
    frames_for_this_core = math.ceil(framecount / CoreAmount)
    total_batches = math.ceil(frames_for_this_core / 50)
    
    for b in range(total_batches):
        frames = renderBatch(b, CoreID, CoreAmount, framecount, frameCountSize, WIDTH, HEIGHT, start, tesseract_points, tesseract_edges)

        for i in frames:
            num, frame = i
            with open(f"images/frame{num}.ppm", "wb") as file:
                file.write(frame)
            

def main():
    S = 50
    WIDTH, HEIGHT = S * 8, S * 8

    # 16 vertices of a Tesseract
    tesseract_points = []
    for x in [-1, 1]:
        for y in [-1, 1]:
            for z in [-1, 1]:
                for w in [-1, 1]:
                    tesseract_points.append(vec4(x, y, z, w))

    # 32 edges of a Tesseract
    tesseract_edges = []
    for i in range(16):
        for j in range(i + 1, 16):
            # Connect points if they differ by only one coordinate
            diffs = 0
            if tesseract_points[i].x != tesseract_points[j].x: diffs += 1
            if tesseract_points[i].y != tesseract_points[j].y: diffs += 1
            if tesseract_points[i].z != tesseract_points[j].z: diffs += 1
            if tesseract_points[i].w != tesseract_points[j].w: diffs += 1
            if diffs == 1:
                tesseract_edges.append((i, j))

    if len(sys.argv) != 1:
        framecount = int(sys.argv[1])
    else:
        framecount = 1800

    frameCountSize = len(str(framecount))

    ProcessAmount = multiprocessing.cpu_count()

    print() # Print so cursor can move up

    start = time.time()

    TaskArgs = [(i, ProcessAmount, framecount, frameCountSize, WIDTH, HEIGHT, start, tesseract_points, tesseract_edges) for i in range(ProcessAmount)]
    with multiprocessing.Pool(processes=ProcessAmount) as pool:
        pool.starmap(runCore, TaskArgs)

    end = time.time()

    print(f"Rendering took {round(end - start)}s")
    

if __name__ == "__main__":
    main()