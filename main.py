import numpy as np
import cv2
from mss import mss
from point_cloud import *
from extract_matches import *
from frame import *
from triangulation import *
from time import sleep
import ctypes
import win32gui
import win32process

bounding_box = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}

alt_tab = True

# good F?
F = 270

W = 1920//2 
H = 1080//2
imgsize = (W, H)
K = np.array([[F, 0, W // 2], [0, F, H // 2], [0, 0, 1]])

frames = []

def get_active_window_title():
  hwnd = win32gui.GetForegroundWindow()
  tid, pid = win32process.GetWindowThreadProcessId(hwnd)
  window_title = win32gui.GetWindowText(hwnd)
  return window_title

if __name__ == '__main__':
  sct = mss()

  app = QtWidgets.QApplication([])
  window = ScatterPlot3D()
  window.show()

  while True:
    if 'NFS Underground' in get_active_window_title():
      if alt_tab:
        sleep(2)
        alt_tab = False
      sct_img = sct.grab(bounding_box)
      frame = np.array(sct_img)[:, :, :3]
      frame = cv2.resize(frame, imgsize)
      
      slam_frame = Frame(frame, K, imgsize)
      frames.append(slam_frame)

      if slam_frame.id == 0:
        continue

      frame1 = frames[-2]
      frame2 = frames[-1]
      idx1, idx2, Rt = generate_match(frame1, frame2)

      if frame2.id <= 2:
        continue

      img, pts3d, camera_position = triangulate(frame, frame1, frame2, Rt, idx1, idx2)

      if len(pts3d) == 0:
        continue

      max_dist = 150
      pts3d = distance_filtering(np.array(pts3d), camera_position, max_dist)

      window.update_scatter(pts3d, camera_position)
    else:
      alt_tab = True

    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  cv2.destroyAllWindows()