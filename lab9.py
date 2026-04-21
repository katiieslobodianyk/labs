import cv2
import numpy as np
import matplotlib.pyplot as plt

image = cv2.imread('input.jpg')

kernel = np.array([[0, -1, 0],
                   [-1, 5, -1],
                   [0, -1, 0]])

sharpened = cv2.filter2D(src=image, ddepth=-1, kernel=kernel)

plt.figure(figsize=(12, 6))
plt.subplot(121)
plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
plt.title('Original')
plt.axis('off')

plt.subplot(122)
plt.imshow(cv2.cvtColor(sharpened, cv2.COLOR_BGR2RGB))
plt.title('Sharpened')
plt.axis('off')

plt.tight_layout()
plt.show()

cv2.imwrite('sharpened.jpg', sharpened)
