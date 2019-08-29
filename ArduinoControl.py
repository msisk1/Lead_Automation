import cv2
import mk2Camera
from time import sleep
from GantryControl import Gantry

xCenter = 360
yCenter = 640
pixelsToMM = 23.4

def tryToFindLabel(cap, t):
  i = 0
  while i < t:
    ret, frame = cap.read()
    processed, label = mk2Camera.processFrame(frame)
    if "" != label:
      print("Found label")
      i = t
    cv2.imshow('processView',processed)
    cv2.waitKey(1)
    i+=1
  return label

def tryToFindTape(number, x, y, cap):
  i = 0
  while i < number:
    ret, frame = cap.read()
    processed, center = mk2Camera.processColor(frame)
    cv2.imshow('processView',processed)
    cv2.waitKey(1)
    if center is not None:
      break
    i+=1
  if center is not None:
    xTarget = (center[1] - xCenter)/pixelsToMM
    yTarget = (yCenter - center[0])/pixelsToMM
    return (str.format("%4.3f"%(x+xTarget)), str.format("%4.3f"%(y+yTarget)))
  else:
    print("Could not find tape")
    return None

def readLabels(number, x, y, gant, cap):
  labels = []
  positions = []
  for n in range(number):
    yTarget = y-(n*65.3)
    gant.sendTo(str.format("%4.3f"%(x)), str.format("%4.3f"%(yTarget)))
    labels.append(tryToFindLabel(cap, 20))
    cX = x+25
    gant.sendTo(str.format("%4.3f"%(cX)), str.format("%4.3f"%(yTarget)))
    center = tryToFindTape(20, cX, yTarget, cap)
    if center is None:
      cX = x+50
      gant.sendTo(str.format("%4.3f"%(cX)), str.format("%4.3f"%(yTarget)))
      center = tryToFindTape(20, cX, yTarget, cap)
      if center is None:
        cX = x+75
        gant.sendTo(str.format("%4.3f"%(cX)), str.format("%4.3f"%(yTarget)))
        center = tryToFindTape(20, cX, yTarget, cap)
    positions.append(center)
  return labels, positions

def singlePass(number, gant):
  cap = cv2.VideoCapture(1)
  labels, positions = readLabels(number, -70, 0, gant, cap)
  cap.release()
  return(labels, positions)


if __name__ == '__main__':
  gant = Gantry()
  labels, positions = singlePass(8)
  print(labels)
  print(positions)
  gant.sendTo(0,0)
  gant.close()
  
'''
  while(True):
    ret, frame = cap.read()
    processed = mk2Camera.processFrame(frame)
    cv2.imshow('frame',processed)
    if cv2.waitKey() & 0xFF == ord('q'):
        break
  
  cv2.destroyAllWindows()'''
