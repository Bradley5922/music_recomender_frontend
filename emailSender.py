import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# loading variables from .env file
import os
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

def send_email(email, actual_recommendations):
    print(f"Sending recommendation email to {email} [...]")

    # Email credentials and settings
    username = "apikey"  
    sender_email = "app@bradleycable.co.uk"
    receiver_email = email
    password = SENDGRID_API_KEY

    # Create the email content
    subject = "Dissertation Music Recommendation Feedback"
    body = f"""
    <body style="font-size: 15px; line-height: 1.4; font-family: Arial, sans-serif;">
        <p>Thank you for filling out the form, <b style="color:red">your recommendation is ready!</b></p>

        <p>Some context behind the project: I am creating a music recommendation algorithm, 
        which is going to be tailored specifically to the medium of vinyl.</p>

        <p>I am taking this opportunity to test out different similarity and distance metrics, 
        methods for numerically quantifying how similar or how "close" elements are 
        (in this case, comparing the genres you like with the general genre of an artist's discography).</p>

        <p>The two methods being tested are:</p>
        <ul>
            <li>Euclidean Distance (Measure A)</li>
            <li>Dot Product (Measure B)</li>
        </ul>

        <p>
            <a href="http://app.bradleycable.co.uk/draft" style="font-size: 16px; color: #1a73e8;">Here is part of my dissertation so far, if you are interested further.</a>
        </p>

        <hr style="border: 1px solid #ddd;">

        <p style="font-weight: bold; color:red;">Here is your song recommendation:</p>
        <p style="font-style: italic;">Please listen to all the songs below in your own time, and then use the survey to answer questions about each song...</p>

        {actual_recommendations}

        <p>
            <a href="https://forms.gle/15orBPuby5SFrecZ6" style="font-size: 16px; color: #1a73e8;">Here is a link to the survey for you to fill out</a>
        </p>
        <span style="font-style: italic;">(Please read the survey first so you know what questions you will be asked)</span>

        <p>Thanks for your help, kind regards!</p>

        <hr style="border: 1px solid #ddd;">

        <div style="display: inline-block; vertical-align: middle; margin-right: 15px;">
            <img src="https://bradleycable.co.uk/img/uob.png" alt="University of Birmingham Logo" width="45" height="50" style="vertical-align: middle;">
        </div>
        <div style="display: inline-block; vertical-align: middle; font-size: 16px;">
            <strong style="font-size: 18px;">Bradley Cable</strong><br>
            <span>Computer Science Undergraduate</span><br>
            <span>University of Birmingham</span>
        </div>
    </body>
    """

    # Set up the MIME multipart message to include HTML content
    message = MIMEMultipart("alternative")
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    # Attach the HTML content to the message
    html_part = MIMEText(body, "html")
    message.attach(html_part)

    # Connect to the SMTP server and send the email using SSL
    try:
        # Connect to the SMTP server with SSL (port 465 is used for SSL)
        with smtplib.SMTP_SSL("smtp.sendgrid.net", 465) as server:
            server.login(username, password)  
            server.sendmail(sender_email, receiver_email, message.as_string())  # Send the email

        print("Email sent successfully!")

    except Exception as e:
        print(f"Error: {e}")

def test_email(email):
    print("Sending test email...")

    try:
        send_email(email, "TEST EMAIL")
    except Exception as e:
        print(f"Error: {e}")

# test_email(input("Enter the recipient email address: "))
