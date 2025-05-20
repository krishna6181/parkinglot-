import cv2
import numpy as np

def line_angle(line):
    x1, y1, x2, y2 = line[0]
    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
    return angle

def filter_lines(lines, angle_min, angle_max):
    filtered = []
    for line in lines:
        angle = line_angle(line)
        
        if angle < -90:
            angle += 180
        elif angle > 90:
            angle -= 180
        if angle_min <= abs(angle) <= angle_max:
            filtered.append(line)
    return filtered

def draw_lines(img, lines, color=(0, 255, 0), thickness=2):
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(img, (x1,y1), (x2,y2), color, thickness)

def main():
    img = cv2.imread('pklots.jpg')
    if img is None:
        print("Error loading image 'pklots.jpg'. Please provide a valid image.")
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edges = cv2.Canny(blur, 50, 150, apertureSize=3)

    
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
    if lines is None:
        print("No lines detected")
        return

    
    vertical_lines = filter_lines(lines, 80, 100)    
    horizontal_lines = filter_lines(lines, 0, 10)      

    line_img = img.copy()
    draw_lines(line_img, vertical_lines, (0, 0, 255), 2)
    draw_lines(line_img, horizontal_lines, (255, 0, 0), 2)

    
    vertical_pts = []
    for line in vertical_lines:
        x1, y1, x2, y2 = line[0]
        vertical_pts.append(((x1, y1), (x2, y2)))
    horizontal_pts = []
    for line in horizontal_lines:
        x1, y1, x2, y2 = line[0]
        horizontal_pts.append(((x1, y1), (x2, y2)))

    intersections = []
    for vline in vertical_pts:
        for hline in horizontal_pts:
            
            x1, y1 = vline[0]
            x2, y2 = vline[1]
            x3, y3 = hline[0]
            x4, y4 = hline[1]

            denom = (x1 - x2)*(y3 - y4) - (y1 - y2)*(x3 - x4)
            if denom == 0:
                continue  

            px = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / denom
            py = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / denom

            if 0 <= px < img.shape[1] and 0 <= py < img.shape[0]:
                intersections.append((int(px), int(py)))

    
    
    if len(intersections) < 4:
        print("Not enough intersections detected.")
        cv2.imshow("Detected Lines", line_img)
        cv2.waitKey(0)
        return

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    k = 20  
    pts = np.array(intersections, dtype=np.float32)
    _, labels, centers = cv2.kmeans(pts, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    
    cluster_img = img.copy()
    for i in range(k):
        cx, cy = centers[i]
        cv2.circle(cluster_img, (int(cx), int(cy)), 5, (0, 255, 255), -1)

   
    cv2.imshow("Edges", edges)
    cv2.imshow("Detected Lines", line_img)
    cv2.imshow("Clustered Intersections", cluster_img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

