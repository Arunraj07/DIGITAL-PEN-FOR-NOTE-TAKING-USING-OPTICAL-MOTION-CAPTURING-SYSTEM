
from evdev import InputDevice, ecodes
from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import subprocess
import time
import uuid
from scipy.interpolate import splprep, splev

def track_mouse():
    mouse = InputDevice("/dev/input/event0")
    point=[]
    x, y = 0, 0

    for event in mouse.read_loop():
        if event is None:
            continue
        if event.type == ecodes.EV_KEY:
            if event.code == ecodes.BTN_LEFT:
                if event.value == 1:
                    print("Tracking Started...")
                    points = []
                    while True:
                        event = mouse.read_one()
                        if event is None:
                            continue
                        if event.type == ecodes.EV_KEY:
                            if event.code ==  ecodes.BTN_LEFT and event.value == 1:
                                print ("Tracking stopped.")
                                break
                        elif event.type == ecodes.EV_REL:
                            if event.code == ecodes.REL_X:
                                x += event.value
                            elif event.code == ecodes.REL_Y:
                                y += event.value
                            points.append((x, y))

                    return points
def convert_to_image(points):
    if len(points) < 4:
        print ("No points to plot.")
        return None

    points = np.array([(x, -y) for x, y in points])

    tck, u = splprep(points.T, s=0.5)
    u_new = np.linspace(0, 1, 1000)
    x_smooth, y_smooth = splev(u_new, tck)

    plt.figure()
    plt.plot(x_smooth, y_smooth, color = 'black')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.axis('off')
    plt.tight_layout()

    save_path = "/home/arunr/Desktop/project_output/"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    image_name = str(uuid.uuid4())

    try:
        image_path = os.path.join(save_path, f"{image_name}.png")
        plt.savefig(image_path)
        print ("Image saved successfully.")
        return image_path
    except Exception as e:
        print (f"Error saving image: {e}")
        return None
#    plt.show()

def send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, attachment_path ):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        msg=MIMEMultipart()
        msg['From']=sender_email
        msg['To']=recipient_email
        msg['subject']=subject

        msg.attach(MIMEText(body, 'plain'))

        with open(attachment_path,'rb') as attachment:
            image_data = attachment.read()
        image = MIMEImage(image_data, name=os.path.basename(attachment_path))
        msg.attach(image)

        server.sendmail(sender_email, recipient_email, msg.as_string())
        print("Email.sent successfully.")
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
    except Exception as e:
        print(f"Email not sent!: {e}")
    finally:
        server.quit()

def perform_ocr(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error performing OCR: {e}")
        return None

def main():

    sender_email = 'smartpenproject@gmail.com'
    sender_password = 'okjzlxihdpsokurd'
    recipient_email = 'smartpenproject@gmail.com'
    subject = 'Smart pen image'
    body = 'This is the image captured by the Smart pen.'

    while True:
         print("Start")
         tracked_points=track_mouse()
         image_path = convert_to_image(tracked_points)

         if image_path:
              send_email_with_attachment(sender_email, sender_password, recipient_email, subject, body, image_path)

         time.sleep(3)


if __name__ == "__main__":
    main()
