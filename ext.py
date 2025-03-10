import os, cv2
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import statistics

page = cv2.imread("testocr/page_15.jpg")
# ratio = page.shape[0] / 640
# page = cv2.resize(page, (int(page.shape[1] / ratio), 640))
# cv2.imshow("page", page)
# cv2.waitKey(0)
# cv2.dilate(
#     page,
#     cv2.getStructuringElement(cv2.MORPH_RECT, (1, page.shape[1] // 30)),
#     page,
#     iterations=1,
# )
# proc_img = cv2.dilate(
#     page,
#     cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)),
#     iterations=2,
# )
proc_img = cv2.morphologyEx(
    page,
    cv2.MORPH_DILATE,
    cv2.getStructuringElement(cv2.MORPH_RECT, (page.shape[0] // 100, 1)),
)
proc_img = cv2.cvtColor(src=proc_img, code=cv2.COLOR_BGR2GRAY)
proc_img = cv2.threshold(proc_img, 100, 255, cv2.THRESH_OTSU)[1]
# cv2.imshow("proc_img", proc_img)
# cv2.waitKey(0)

contours, hier = cv2.findContours(
    proc_img,
    cv2.RETR_TREE,
    cv2.CHAIN_APPROX_SIMPLE,
)

print(f"{len(contours)} contours found")

groups = {}

for c in contours:
    x, y, w, h = cv2.boundingRect(c)

    found = False
    for delta in range(-5, 6):  # bounding box 的拟合误差：5px
        if (x + delta) in groups:
            groups[x + delta].append(c)
            found = True
            break
    if not found:
        groups[x] = [c]


tmp = {}
for c in groups:
    if len(groups[c]) <= 1:
        continue
    tmp[c] = groups[c]
    for cont in groups[c]:
        x, y, w, h = cv2.boundingRect(cont)
        cv2.rectangle(page, (x, y), (x + w, y + h), (0, 255, 0), 5)

groups = tmp
result = []
for x in groups:
    if len(groups[x]) <= 1:  # filter if only one line
        continue

    w = statistics.median([cv2.boundingRect(c)[2] for c in groups[x]])
    lst = [
        cv2.boundingRect(c)
        for c in groups[x]
        if cv2.boundingRect(c)[2] >= w - 5 and cv2.boundingRect(c)[2] <= w + 5
    ]  # filter "word underline"

    lst.sort(key=lambda x: x[1])
    b1, b2 = lst[0], lst[-1]

    if b2[0] + b2[2] - b1[0] <= 50 or b2[1] - b1[1] + b2[3] <= 50:
        continue  # 长/宽太小，不太可能是表格

    result.append((b1[0], b1[1], b2[0] + b2[2] - b1[0], b2[1] - b1[1] + b2[3]))  # bbox
    cv2.rectangle(page, (b1[0], b1[1]), (b2[0] + b2[2], b2[1] + b2[3]), (0, 0, 255), 5)

cv2.imwrite("contours.jpg", page)
