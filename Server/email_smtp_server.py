# import the necessary components first

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

port = 2525
smtp_server = "smtp.mailtrap.io"
login = "a35fff1ed64201" # paste your login generated by Mailtrap
password = "8ee7462b268fbc" # paste your password generated by Mailtrap
sender_email = "erori_program@victor.com"
receiver_email = "inginer@victor.com"
message = MIMEMultipart("alternative")
message["Subject"] = "Camera de servare a fost accesata"
message["From"] = sender_email
message["To"] = receiver_email


# convert both parts to MIMEText objects and add them to the MIMEMultipart message
def trimite_email(mesaj_eroare):


    # write the text/plain part
    text = f"""\
    Hi,
    Eroare detectata:
    {mesaj_eroare}"""
    # write the HTML part

    html = """
     <html>
     <head>
     <style>
     /* Add your styles here */
     body {
     font-family: Arial, sans-serif;
     background-color: #f5f5f5;
     padding: 20px;
     }
     .container {
     max-width: 600px;
     margin: 0 auto;
     background-color: #ffffff;
     padding: 20px;
     border-radius: 4px;
     box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
     }
     h1 {
     color: #333333;
     }
     p {
     color: #666666;
     }
     .button {
     display: inline-block;
     background-color: #0066cc;
     color: #ffffff;
     padding: 10px 20px;
     text-decoration: none;
     border-radius: 4px;
     }
     </style>
     </head>
     <body>
     <div class="container">
     <h1>Persoana necunoscuta aflata in camera de servere. 
     Poza atasata</h1>
     </div>
     </body>
     </html>
     """

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")
    message.attach(part1)
    message.attach(part2)
    
    with open("necunoscut.jpg", "rb") as image_file:
         image_data = image_file.read()
         image_part = MIMEImage(image_data, name="necunoscut.jpg")
         image_part.add_header('Content-ID', '<Mailtrapimage>')
         message.attach(image_part)
    
    # send your email
    with smtplib.SMTP("sandbox.smtp.mailtrap.io", 587) as server:
        server.starttls()
        server.login(login, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
    print('Sent')
