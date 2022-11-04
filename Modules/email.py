from datetime import date
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from typing import NewType

HTMLColor = NewType("HTMLColor", int)
HTMLTable = NewType("HTMLTable", int)


def coloring_result(item: int, condition: str, indicator: int) -> HTMLColor:
    """
    Coloring Result Color Variable Based on Indicator as a Limit
     The indicator limits taken from the DataBase Indicators_limit Table
    Condition Should be < or >
    """
    try:
        if condition == ">":
            if int(item) > indicator:
                return '#ff0000'
            else:
                return '#000000'

        if condition == "<":
            if int(item) < indicator:
                return '#ff0000'
            else:
                return '#000000'
    except Exception as ex:
        return '#000000'

def add_symbol_to_result(item: str, symbol: str):
    """
    Take An integer Item and retrieve the result with Symbol 
     For Example GB or %
    """
    if item:
        return (f"{item} {symbol}")

def convert_result_to_html(result: list, indicators: dict) -> HTMLTable:
    """
    Take List of results and convert it to HTML Row
     Coloring the results based on Indicators
      Append Each Created html row to The Email's rows list
    """
    used_color: HTMLColor = coloring_result(
        result['used_percentage'], ">", indicators['maximum_used_percentage']
        )

    remaining_color: HTMLColor = coloring_result(
        result['used_percentage'], ">", indicators['maximum_used_percentage']
        )

    usage_color: HTMLColor = coloring_result(
        result['usage'], ">", indicators['maximum_usage']
        )

    balance_color: HTMLColor = coloring_result(
        result['balance'], "<", indicators['minimum_balance']
        )

    used_percentage: str = add_symbol_to_result(result['used_percentage'], "%")
    remaining = add_symbol_to_result(result['remaining'], "GB")
    usage = add_symbol_to_result(result['usage'], "GB")
    balance = add_symbol_to_result(result['balance'], "LE")
    return f"""\
        <tr>
                <td style="height:25px; text-align:center; width:40px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: #000000;">{result['line_number']}</td>

                <td style="height:25px; text-align:center; width:40px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: #000000;">{result['line_name']}</td>

                <td style="height:25px; text-align:center; width:40px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: #000000;">{result['isp']}</td>


                <td style="height:25px; text-align:center; width:40px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: #000000;">{result['line_using']}</td>


                <td style="height:25px; text-align:center; width:40px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: #000000;">{result['download']}</td>

                <td style="height:25px; text-align:center; width:40px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: #000000;">{result['upload']}</td>

                <td style="height:25px; text-align:center; width:60px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: {used_color};">{str(used_percentage)}</td>

                <td style="height:25px; text-align:center; width:70px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: {remaining_color};">{remaining}</td>

                <td style="height:25px; text-align:center; width:70px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: {usage_color};">{str(usage)}</td>

                <td style="height:25px; text-align:center; width:70px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: #000000;">{result["renew_date"]}</td>

                <td style="height:25px; text-align:center; width:60px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: {balance_color};">{str(balance)}</td>
            </tr>"""

def html_table(rows) -> None:
    return f"""\
        <table border="1" cellspacing="0" style="border-collapse:collapse; margin-left:auto; margin-right:auto;">
        <tbody>

        <tr>
        <td style="width: 120px; height:50"; bgcolor="#ff9900">
        <h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">Number</span></span></strong></h3></td>

        <td style="width: 80px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">Name</span></span></strong></h3></td>

        <td style="width: 100px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">ISP</span></span></strong></h3></td>

        <td style="width: 320px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">Line Used For</span></span></strong></h3></td>

        <td style="width: 70px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">D.L</span></span></strong></h3></td>

        <td style="width: 80px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">U.L</span></span></strong></h3></td>

        <td style="width: 100px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <Color: #000000;"><span style="font-family:Calibri,&quot;sans-serif&quot;;">Used</span></span></strong></h3></td>

        <td style="width: 100px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">Remaining</span></span></strong></h3></td>

        <td style="width: 150px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">Usage</span></span></strong></h3></td>

        <td style="width: 200px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">Renewal Date</span></span></strong></h3></td>

        <td style="width: 120px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <Color: #000000;"><span style="font-family:Calibri,&quot;sans-serif&quot;;">Balance</span></span></strong></h3></td>
        </tr>

        {rows}

        </tbody>
        </table>
        <p>&nbsp;</p>
        """

class Email:
    @classmethod
    def start(cls, results: list[dict], settings: list[dict], recipients: list, indicators: list[dict]) -> None:
        """
        Constructing Email in HTML Table Format and Send it to Recipients List
        """
        table: list = " ".join(convert_result_to_html(result, indicators) for result in results)
        Email.send(settings, recipients, table)

    def send(config, recipients, table) -> None:
        """
        The Connecter to SMTP Server and Email Sender
         Using GMAIL Connection
        """
        msg = EmailMessage()
        msg['Subject'] = config['email_subject']
        msg['From'] = formataddr(("Netowork Automation", config['sender']))
        msg['To'] = recipients
        msg['Alias'] 

        msg.add_alternative(f"""\
        <p><span style="font-size:20px"><strong><Color: #000000;"><span style="font-family:Comic Sans MS,cursive"> {str(date.today())} </span></strong></span></p>

        <!DOCTYPE html>
        <html>
            <body>
            {" ".join([Email.html_table(table)])}
            </body>
        </html>
        """, subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(config['sender'], config['password'])
            smtp.send_message(msg)
            print('Email Sent \n Done')

if __name__ == "__main__":
    Email.send('smhit.bkp@gmail.com', "baypifdcneetnqio", "adel.aly@andalusiagroup.net", "test")