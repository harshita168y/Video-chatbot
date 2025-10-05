import cv2
import os

# Ask for username and number of images
username = input("Enter your username: ").strip()
num_images = int(input("How many images to capture? "))

# Create folder for user
save_folder = f"data/users/{username}"
os.makedirs(save_folder, exist_ok=True)

# Open webcam
cap = cv2.VideoCapture(0)
print(f"Press 'c' to capture image, 'q' to quit. Capture {num_images} images.")

count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    cv2.imshow(f"Register Face: {username}", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("c"):
        count += 1
        img_path = os.path.join(save_folder, f"{count}.jpg")
        cv2.imwrite(img_path, frame)
        print(f"Saved image {count} for {username}")
        if count >= num_images:
            print("Captured all images.")
            break
    elif key == ord("q"):
        print("Registration canceled.")
        break

cap.release()
cv2.destroyAllWindows()
