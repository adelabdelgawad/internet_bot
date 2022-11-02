from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
import smtplib
import ssl



class EmailSender:
    def send(config, receiver, table) -> None:
        sender_alias: str = config[0]
        sender: str = config[1]
        password: str = config[2]
        subject: str = config[3]

        mail_body: list = []  # list will contain the results and used in email
        mail_body.append(EmailSender.created_table(table))
        mail_body = " ".join(mail_body)
        



        #######################################
        # Beginning of email script
        #######################################
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = formataddr((sender_alias, sender))
        message["To"] = receiver
        message["Cc"] = ""

        # Create the plain-text and HTML version of your message
        text = """\
        Hi,
        How are you?
        Real Python has many great tutorials:
        www.realpython.com"""
        html = """\
        Hi,
        How are you?
        Real Python has many great tutorials:
        www.realpython.com"""
        html = f"""\
        <p><span style="font-size:16px"><strong><span style="font-family:Comic Sans MS,cursive"> {str(date.today())} </span></strong></span></p>

        <!DOCTYPE html>
        <html>
            <body>
            {mail_body}
            </body>
        </html>
        """
        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender, password)
            server.sendmail(
                sender, receiver, message.as_string()
            )
        print('Email Sent \n Done')
    # Method will used on each if statment
    # To create table for each site
    def created_table(value) -> None:
        return f"""\
            <table border="1" cellspacing="0" style="border-collapse:collapse; margin-left:auto; margin-right:auto;">
            <tbody>

            <tr>
            <td style="width: 120px; height:50"; bgcolor="#ff9900">
            <h3 style="text-align:center"><strong><span style="font-size:14pt">
            <span style="font-family:Calibri,&quot;sans-serif&quot;;">Number</span></span></strong></h3></td>

            <td style="width: 80px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt"> <span
            style="font-family:Calibri,&quot;sans-serif&quot;;">Name</span></span></strong></h3></td>

            <td style="width: 100px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt"> <span
            style="font-family:Calibri,&quot;sans-serif&quot;;">ISP</span></span></strong></h3></td>

            <td style="width: 320px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt"> <span
            style="font-family:Calibri,&quot;sans-serif&quot;;">Line Used For</span></span></strong></h3></td>

            <td style="width: 70px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt"> <span
            style="font-family:Calibri,&quot;sans-serif&quot;;">D.L</span></span></strong></h3></td>

            <td style="width: 70px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt"> <span
            style="font-family:Calibri,&quot;sans-serif&quot;;">U.L</span></span></strong></h3></td>

            <td style="width: 100px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt">
            <span style="font-family:Calibri,&quot;sans-serif&quot;;">Used</span></span></strong></h3></td>

            <td style="width: 100px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt"> <span
            style="font-family:Calibri,&quot;sans-serif&quot;;">Remaining</span></span></strong></h3></td>

            <td style="width: 100px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt"> <span
            style="font-family:Calibri,&quot;sans-serif&quot;;">Consumed</span></span></strong></h3></td>

            <td style="width: 200px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong> <span style="font-size:14pt">
            <span style="font-family:Calibri,&quot;sans-serif&quot;;">Next Renew
            </span></span></strong></h3></td>

            <td style="width: 120px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt"> <span
            style="font-family:Calibri,&quot;sans-serif&quot;;">Balance</span></span></strong></h3></td>
            </tr>

            {value}

            </tbody>
            </table>
            <p>&nbsp;</p>
            """

class EmailCreator:
    result_formated: list = []
    def convert(self, DB, row_id) -> None:
        id: int
        line_name: str
        line_number: str
        download: str
        upload: str
        isp: str
        line_using: str
        used: int
        used_percentage: int
        remaining: int
        balance: int
        renew_date: str
        consumed: int
        date: str
        credit_transaction: str
        renew_status: str

        black_color = '#000000'
        red_color = '#ff0000'

        line_number_color: str = black_color
        line_name_color: str = black_color
        isp_color: str = black_color
        used_color: str = black_color
        remaining_color: str = black_color
        consumed_color: str = black_color
        balance_color: str = black_color
        id, line_id, line_name, line_number, download, upload, isp, line_using, used, used_percentage, remaining, balance, renew_date, consumed, date, credit_transaction, renew_status = DB.get_today_row(row_id)
        
        if line_name == 'WE':
            line_number_color, line_name_color, isp_color = black_color
        try:
            if int(used_percentage) > 70:
                used_color, remaining_color = red_color
        except: pass

        try:
            if int(consumed) > 50:
                consumed_color = red_color
        except: pass

        try:
            if int(balance) < 1000:
                balance_color = red_color
        except:
            pass

        if used_percentage:
            used_percentage = f"{used_percentage}%"
        if remaining:
            remaining = f"{remaining} GB"
        if consumed:
            consumed = f"{consumed} GB"
        if balance:
            balance = f"{balance} LE"



        EmailCreator.result_formated.append(
f"""\
        <tr>
            <td style="height:25px; text-align:center; width:40px">
            <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
            Color: {line_number_color};">{line_number}</td>

            <td style="height:25px; text-align:center; width:40px">
            <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
            Color: {line_name_color};">{line_name}</td>

            <td style="height:25px; text-align:center; width:40px">
            <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
            Color: {isp_color};">{isp}</td>


            <td style="height:25px; text-align:center; width:40px">
            <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
            Color: #000000;">{line_using}</td>


            <td style="height:25px; text-align:center; width:40px">
            <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
            Color: #000000;">{download}</td>

            <td style="height:25px; text-align:center; width:40px">
            <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
            Color: #000000;">{upload}</td>

            <td style="height:25px; text-align:center; width:60px">
            <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
            Color: {used_color};">{str(used_percentage)}</td>

            <td style="height:25px; text-align:center; width:70px">
            <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
            Color: {remaining_color};">{str(remaining)}</td>

            <td style="height:25px; text-align:center; width:70px">
            <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
            Color: {consumed_color};">{str(consumed)}</td>

            <td style="height:25px; text-align:center; width:70px">
            <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
            Color: #000000;">{renew_date}</td>

            <td style="height:25px; text-align:center; width:60px">
            <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
            Color: {balance_color};">{str(balance)}</td>

        </tr>
        """
        )

if __name__ == "__main__":
    EmailSender.send('smhit.bkp@gmail.com', "baypifdcneetnqio", "adel.aly@andalusiagroup.net", "test")
