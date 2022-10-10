from picamera import PiCamera
camera = PiCamera()
time.sleep(2)
camera.capture("/home/pi/Pictures/img.jpg")
print("Done.")