import cv2
import numpy as np
import time
import threading
import multiprocessing as mp
import os
from pathlib import Path


os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

def sharpen_image(image_path):
    img = cv2.imread(image_path)
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharp = cv2.filter2D(img, -1, kernel)
    out_path = Path(image_path).stem + "_sharp.jpg"
    cv2.imwrite(out_path, sharp)

def process_sequential(images):
    for p in images:
        sharpen_image(p)

def process_threading(images, num_threads=4):
    threads = []
    chunk_size = max(1, len(images) // num_threads)
    for i in range(0, len(images), chunk_size):
        chunk = images[i:i+chunk_size]
        t = threading.Thread(target=lambda lst: [sharpen_image(x) for x in lst], args=(chunk,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

def process_multiprocessing(images, num_processes=None):
    if num_processes is None:
        num_processes = min(mp.cpu_count(), 4) 
    with mp.Pool(processes=num_processes) as pool:
        pool.map(sharpen_image, images)

def create_test_images(n=5, size=(800,600), folder='test_imgs'):
    Path(folder).mkdir(exist_ok=True)
    paths = []
    for i in range(n):
        img = np.random.randint(0, 256, (size[1], size[0], 3), dtype=np.uint8)
        path = f"{folder}/img_{i}.jpg"
        cv2.imwrite(path, img)
        paths.append(path)
    return paths

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()

    images = create_test_images(n=5, size=(800,600))
    print(f"Обробка {len(images)} зображень 800x600...\n")

    t0 = time.time()
    process_sequential(images)
    t_seq = time.time() - t0

    t0 = time.time()
    process_threading(images, num_threads=4)
    t_thr = time.time() - t0

    t0 = time.time()
    process_multiprocessing(images, num_processes=2)  
    t_mp = time.time() - t0

    print(f"Послідовно:      {t_seq:.2f} с")
    print(f"Потоки (4):      {t_thr:.2f} с (x{t_seq/t_thr:.2f})")
    print(f"Процеси (2):     {t_mp:.2f} с (x{t_seq/t_mp:.2f})")
