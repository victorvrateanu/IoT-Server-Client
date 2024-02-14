# import the necessary components first

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
port = 2525
smtp_server = "smtp.mailtrap.io"
login = "a35fff1ed64201" # paste your login generated by Mailtrap
parola = "8ee7462b268fbc" # paste your password generated by Mailtrap
sender_email = "erori_program@victor.com"
receiver_email = "inginer@victor.com"
mesaj = MIMEMultipart("alternative")
mesaj["Subject"] = "Camera de servare a fost accesata"
mesaj["From"] = sender_email
mesaj["To"] = receiver_email


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
     <h1>Alerta in camera de servere</h1>
     <p>Accesati linkul pentru mai multe informatii..</p>
     <a class="button" href="http://192.168.207.75/">Accesare server</a>
     </div>
     </body>
     </html>
     """

    partea1 = MIMEText(text, "plain")
    partea2 = MIMEText(html, "html")
    mesaj.attach(partea1)
    mesaj.attach(partea2)
    # send your email
    with smtplib.SMTP("sandbox.smtp.mailtrap.io", 2525) as server:
        server.login(login, parola)
        server.sendmail(
            sender_email, receiver_email, mesaj.as_string()
        )
    print('Sent')