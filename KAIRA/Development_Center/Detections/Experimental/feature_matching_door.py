import os
import cv2
import numpy as np
import math

# Function to detect features using BRISK (Binary Robust Invariant Scalable Keypoints)
def brisk_feature_detect(img):
    """
    Detects and displays features in the image using BRISK feature detector.
    """
    brisk = cv2.BRISK_create(1, 2)  # Create BRISK detector with specific parameters
    (kp, des) = brisk.detectAndCompute(img, None)  # Detect keypoints and descriptors

    # Draw only the keypoints location, not size or orientation
    img2 = cv2.drawKeypoints(img, kp, img, color=(0, 255, 0), flags=0)
    cv2.imshow("keypoints", img2)  # Show the image with keypoints
    cv2.waitKey(0)  # Wait for user to close the image window

# Function to detect features using FAST (Features from Accelerated Segment Test)
def fast_feature_detect(img):
    """
    Detects and displays features in the image using FAST feature detector.
    """
    fast = cv2.FastFeatureDetector_create(threshold=1)  # Initialize FAST detector with threshold
    kp = fast.detect(img, None)  # Detect keypoints

    br = cv2.BRISK_create(10000000, 2)  # BRISK to compute descriptors
    kp, _ = br.compute(img, kp)  # Compute descriptors for detected keypoints

    print("Threshold: ", fast.getThreshold())
    print("nonmaxSuppression: ", fast.getNonmaxSuppression())
    print("neighborhood: ", fast.getType())
    print("Total Keypoints with nonmaxSuppression: ", len(kp))

    img2 = cv2.drawKeypoints(img, kp, img, color=(0, 255, 0), flags=0)
    cv2.imshow("keypoints", img2)
    cv2.waitKey(0)

# Function to detect features using ORB (Oriented FAST and Rotated BRIEF)
def feature_detect(img):
    """
    Detects and displays features using ORB feature detector.
    """
    orb = cv2.ORB_create(nfeatures=10000000, scoreType=cv2.ORB_FAST_SCORE)  # Create ORB detector
    kp = orb.detect(img, None)  # Detect keypoints
    kp, _ = orb.compute(img, kp)  # Compute descriptors for the keypoints

    img2 = cv2.drawKeypoints(img, kp, img, color=(0, 255, 0), flags=0)
    cv2.imshow("keypoints", img2)  # Display the keypoints
    cv2.waitKey(0)

# Function to match features between two images using FAST feature detection
def fast_feature_match(img_scene, img_template):
    """
    Matches features between two images using FAST and BRISK.
    """
    fast = cv2.FastFeatureDetector_create(threshold=60)  # Initialize FAST detector with threshold
    MIN_MATCHES = 10  # Minimum number of matches to consider for a valid match
    br = cv2.BRISK_create()  # BRISK descriptor for matching
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)  # Matcher for descriptors

    # Compute keypoints and descriptors for the model and scene
    kp_m = fast.detect(img_template, None)  # Detect keypoints using FAST
    kp_model, des_model = br.compute(img_template, kp_m)  # Use BRISK for descriptors

    kp_f = fast.detect(img_scene, None)
    kp_frame, des_frame = br.compute(img_scene, kp_f)

    matches = bf.match(des_model, des_frame)  # Match descriptors
    matches = sorted(matches, key=lambda x: x.distance)  # Sort matches by distance

    if len(matches) > MIN_MATCHES:
        img_scene = cv2.drawMatches(
            img_template, kp_model, img_scene, kp_frame, matches[:MIN_MATCHES], 0, flags=2
        )  # Draw matches on the image
        cv2.imshow("frame", img_scene)  # Show matched image
        cv2.waitKey(0)
    else:
        print("Not enough matches have been found - %d/%d" % (len(matches), MIN_MATCHES))

# Function to match features using ORB feature detection and brute-force matching
def feature_match(img_scene, img_template):
    MIN_MATCHES = 20
    orb = cv2.ORB_create(nfeatures=10000000, scoreType=cv2.ORB_FAST_SCORE)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    kp_model, des_model = orb.detectAndCompute(img_template, None)
    kp_frame, des_frame = orb.detectAndCompute(img_scene, None)
    
    matches = bf.match(des_model, des_frame)
    matches = sorted(matches, key=lambda x: x.distance)

    min_x, min_y, max_x, max_y = calculate_bounds(matches, kp_model, kp_frame)
    h, w = max_y - min_y, max_x - min_x

    list_grouped_matches = group_matches(matches, kp_model, kp_frame, w, h)
    list_grouped_matches_filtered = [group for group in list_grouped_matches if len(group) >= 4]

    corners = cv2.goodFeaturesToTrack(img_template, 3, 0.01, 20)
    corners = np.int0(corners)

    origin = calculate_origin(corners)
    process_matches(list_grouped_matches_filtered, origin, img_scene, kp_model, kp_frame, MIN_MATCHES, matches, img_template)


def calculate_bounds(matches, kp_model, kp_frame):
    min_x = min_y = math.inf
    max_x = max_y = 0

    for mat in matches:
        x1, y1 = kp_model[mat.queryIdx].pt
        _, _ = kp_frame[mat.trainIdx].pt

        if x1 < min_x:
            min_x = x1
        if x1 > max_x:
            max_x = x1
        if y1 < min_y:
            min_y = y1
        if y1 > max_y:
            max_y = y1

    return min_x, min_y, max_x, max_y


def group_matches(matches, kp_model, kp_frame, w, h):
    list_grouped_matches = []

    for mat in matches:
        x1, y1 = kp_model[mat.queryIdx].pt
        x2, y2 = kp_frame[mat.trainIdx].pt

        found = False
        for i, existing_match in enumerate(list_grouped_matches):
            if abs(existing_match[0][1][0] - x2) < w and abs(existing_match[0][1][1] - y2) < h:
                list_grouped_matches[i].append(((int(x1), int(y1)), (int(x2), int(y2))))
                found = True
                break

        if not found:
            list_grouped_matches.append([((int(x1), int(y1)), (int(x2), int(y2)))])

    return list_grouped_matches


def calculate_origin(corners):
    min_x = min_y = math.inf
    max_x = max_y = 0

    for cr in corners:
        x1, y1 = cr[0]
        if x1 < min_x:
            min_x = x1
        if x1 > max_x:
            max_x = x1
        if y1 < min_y:
            min_y = y1
        if y1 > max_y:
            max_y = y1

    return int((max_x + min_x) / 2), int((min_y + max_y) / 2)


def process_matches(list_grouped_matches_filtered, origin, img_scene, kp_model, kp_frame, min_matches, matches, img_template):
    scaled_upper_left = (0, 0)
    scaled_upper_right = (1, 0)
    scaled_down = (0, 1)

    for match in list_grouped_matches_filtered:
        index1, index2 = calculate_best_matches_with_modulus_angle(match)
        pos1_model = match[index1][0]
        pos2_model = match[index2][0]
        pos1_cap = match[index1][1]
        pos2_cap = match[index2][1]

        pt1 = (pos1_model[0] - pos2_model[0], pos1_model[1] - pos2_model[1])
        pt2 = (pos1_cap[0] - pos2_cap[0], pos1_cap[1] - pos2_cap[1])

        ang = math.degrees(angle(pt1, pt2))

        new_upper_left = rotate(origin, scaled_upper_left, math.radians(ang))
        new_upper_right = rotate(origin, scaled_upper_right, math.radians(ang))
        new_down = rotate(origin, scaled_down, math.radians(ang))

        new_pos1_model = rotate(origin, scaled_upper_left, math.radians(ang))
        offset = (new_pos1_model[0] - pos1_model[0], new_pos1_model[1] - pos1_model[1])
        move_dist = (pos1_cap[0] - pos1_model[0], pos1_cap[1] - pos1_model[1])

        moved_new_upper_left = (
            int(new_upper_left[0] + move_dist[0] - offset[0]),
            int(new_upper_left[1] + move_dist[1] - offset[1]),
        )
        moved_new_upper_right = (
            int(new_upper_right[0] + move_dist[0] - offset[0]),
            int(new_upper_right[1] + move_dist[1] - offset[1]),
        )
        moved_new_down = (
            int(new_down[0] + move_dist[0] - offset[0]),
            int(new_down[1] + move_dist[1] - offset[1]),
        )

        img_scene = cv2.circle(img_scene, moved_new_upper_left, radius=4, color=(0, 0, 0), thickness=5)
        img_scene = cv2.circle(img_scene, moved_new_upper_right, radius=4, color=(0, 0, 0), thickness=5)
        img_scene = cv2.circle(img_scene, moved_new_down, radius=4, color=(0, 0, 0), thickness=5)

    for match in list_grouped_matches_filtered:
        img_scene = cv2.circle(img_scene, (match[0][1][0], match[0][1][1]), radius=4, color=(0, 0, 0), thickness=5)

    if len(matches) > min_matches:
        img_scene = cv2.drawMatches(img_template, kp_model, img_scene, kp_frame, matches[:min_matches], 0, flags=2)
        cv2.imshow("frame", img_scene)
        cv2.waitKey(0)
    else:
        print(f"Not enough matches have been found - {len(matches)}/{min_matches}")


# Additional Helper Functions

def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return (qx, qy)



def angle(vector1, vector2):
    """
    Calculate the angle between two vectors in 2D.
    """
    x1, y1 = vector1
    x2, y2 = vector2
    inner_product = x1 * x2 + y1 * y2
    len1 = math.hypot(x1, y1)
    len2 = math.hypot(x2, y2)
    return math.acos(inner_product / (len1 * len2))


def scale_model_point_to_origin(origin, point, x_scale, y_scale):
    """
    Scale the coordinates of a point relative to a given origin with x and y scaling factors.
    """
    dx, dy = (point[0] - origin[0], point[1] - origin[1])
    return (dx * x_scale, dy * y_scale)


def calculate_best_matches_with_angle_checks(match_list):
    """
    Calculate the best matches by checking how much they differ from the average angle.
    """
    list_of_angles = calculate_angles(match_list)
    average_angle = average(list_of_angles)
    return find_best_matches(match_list, average_angle)


def calculate_angles(match_list):
    """
    Calculate the angles between all pairs of matches in the list.
    """
    list_of_angles = []
    for i, match1 in enumerate(match_list):
        for j, match2 in enumerate(match_list):
            pos1_model, pos2_model, pos1_cap, pos2_cap = get_positions(match_list, i, j)
            pt1, pt2 = get_points(pos1_model, pos2_model, pos1_cap, pos2_cap)
            if pt1 == pt2 or pt1 == (0, 0) or pt2 == (0, 0):
                continue
            ang = math.degrees(angle(pt1, pt2))
            list_of_angles.append(ang)
    return list_of_angles


def get_positions(match_list, i, j):
    """
    Get the positions of the model and capture points for the given indices.
    """
    pos1_model = match_list[i][0]
    pos2_model = match_list[j][0]
    pos1_cap = match_list[i][1]
    pos2_cap = match_list[j][1]
    return pos1_model, pos2_model, pos1_cap, pos2_cap


def get_points(pos1_model, pos2_model, pos1_cap, pos2_cap):
    """
    Get the points for the model and capture positions.
    """
    pt1 = (pos1_model[0] - pos2_model[0], pos1_model[1] - pos2_model[1])
    pt2 = (pos1_cap[0] - pos2_cap[0], pos1_cap[1] - pos2_cap[1])
    return pt1, pt2


def find_best_matches(match_list, average_angle):
    """
    Find the best matches by comparing the angles to the average angle.
    """
    current_best = math.inf
    _index1 = _index2 = 0
    for i, match1 in enumerate(match_list):
        for j, match2 in enumerate(match_list):
            pos1_model, pos2_model, pos1_cap, pos2_cap = get_positions(match_list, i, j)
            pt1, pt2 = get_points(pos1_model, pos2_model, pos1_cap, pos2_cap)
            if pt1 == pt2 or pt1 == (0, 0) or pt2 == (0, 0):
                continue
            ang = math.degrees(angle(pt1, pt2))
            diff = average_angle - ang
            if diff < current_best:
                current_best = diff
                _index1 = i
                _index2 = j
    return _index1, _index2


def average(lst):
    """
    Calculate the average of a list of numbers.
    """
    return sum(lst) / len(lst)


def calculate_best_matches_with_modulus_angle(match_list):
    """
    Calculate best matches by looking at the most significant feature distances.
    """
    best = math.inf
    index1 = index2 = 0

    for i, match1 in enumerate(match_list):
        for j, match2 in enumerate(match_list):
            pos1_model = match_list[i][0]
            pos2_model = match_list[j][0]
            pos1_cap = match_list[i][1]
            pos2_cap = match_list[j][1]

            pt1 = (pos1_model[0] - pos2_model[0], pos1_model[1] - pos2_model[1])
            pt2 = (pos1_cap[0] - pos2_cap[0], pos1_cap[1] - pos2_cap[1])

            if pt1 == pt2 or pt1 == (0, 0) or pt2 == (0, 0):
                continue

            ang = math.degrees(angle(pt1, pt2))
            diff = ang % 30

            if diff < best:
                best = diff
                index1 = i
                index2 = j

    return index1, index2


def calculate_best_matches_distance(match_list):
    """
    Calculate best matches based on the most significant feature distances.
    """
    max_dist = 0
    index1 = index2 = 0

    for i, match1 in enumerate(match_list):
        for j, match2 in enumerate(match_list):
            dist = abs(match1[1][0] - match2[1][0]) + abs(match1[1][1] - match2[1][1])
            if dist > max_dist:
                max_dist = dist
                index1 = i
                index2 = j

    return index1, index2


if __name__ == "__main__":
    example_image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../Images/Examples/example.png")
    door_image_paths = [
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../Images/Models/Doors/door1.png"),
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../Images/Models/Doors/door2.png"),
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../../Images/Models/Doors/door3.png")
    ]
     # Load the example image
    img1 = cv2.imread(example_image_path, 0)

    # Iterate through each door image and match features
    for door_image_path in door_image_paths:
        img2 = cv2.imread(door_image_path, 0)
        print(f"Matching features for door image: {door_image_path}")
        feature_match(img1, img2)  # Call the feature match function for each door image