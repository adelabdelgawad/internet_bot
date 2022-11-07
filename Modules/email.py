from datetime import date
import smtplib
from email.utils import formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
        result['UsedPercentage'], ">", indicators['MaxUsedPercentage']
        )

    remaining_color: HTMLColor = coloring_result(
        result['UsedPercentage'], ">", indicators['MaxUsedPercentage']
        )
     
    usage_color: HTMLColor = coloring_result(
        result['Usage'], ">", indicators['MaxUsage']
        )

    balance_color: HTMLColor = coloring_result(
        result['Balance'], "<", indicators['MinBalance']
        )

    used_percentage: str = add_symbol_to_result(result['UsedPercentage'], "%")
    used: str = add_symbol_to_result(result['Used'], "GB")
    remaining = add_symbol_to_result(result['Remaining'], "GB")
    usage = add_symbol_to_result(result['Usage'], "GB")
    balance = add_symbol_to_result(result['Balance'], "LE")
    hours = ''

    if result['Hours']:
        hours = f" in {result['Hours']} Hours"

    return f"""\
        <tr>
                <td style="height:25px; text-align:center; width:40px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: #000000;">{result['LineNumber']}</td>

                <td style="height:25px; text-align:center; width:40px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: #000000;">{result['LineName']}</td>

                <td style="height:25px; text-align:center; width:40px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: #000000;">{result['LineISP']}</td>


                <td style="height:25px; text-align:center; width:40px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: #000000;">{result['LineDescription']}</td>


                <td style="height:25px; text-align:center; width:40px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: #000000;">{result['Download']}</td>

                <td style="height:25px; text-align:center; width:40px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: #000000;">{result['Upload']}</td>

                <td style="height:25px; text-align:center">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: {used_color};">{str(used)} - {str(used_percentage)}</td>

                <td style="height:25px; text-align:center; width:70px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: {remaining_color};">{remaining}</td>

                <td style="height:25px; text-align:center; width:70px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: {usage_color};">{str(usage)}{hours}</td>

                <td style="height:25px; text-align:center; width:70px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: #000000;">{result["RenewalDate"]}</td>

                <td style="height:25px; text-align:center; width:60px">
                <span style="font-family:Calibri,&quot;sans-serif&quot;; font-size:14pt;
                Color: {balance_color};">{str(balance)}</td>
            </tr>"""

def html_table(rows) -> None:
    return f"""\
        <table border="1" cellspacing="0" style="border-collapse:collapse; margin-left:auto; margin-right:auto;">
        <tbody>
        <tr>
            <td style="width: 120px; height:30"; bgcolor="#ff9900"; colspan="4">
            <h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
            <span style="font-family:Calibri,&quot;sans-serif&quot;;">Line Information</span></span></strong></h3></td>

            <td style="width: 80px"; bgcolor="#ff9900"; colspan="2"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
            <span style="font-family:Calibri,&quot;sans-serif&quot;;">Speedtest</span></span></strong></h3></td>

            <td style="width: 80px"; bgcolor="#ff9900"; colspan="5"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
            <span style="font-family:Calibri,&quot;sans-serif&quot;;">Quota Results</span></span></strong></h3></td>
        </tr>
        <tr>
        <td style="width: 120px; height:40"; bgcolor="#ff9900">
        <h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">Number</span></span></strong></h3></td>

        <td style="width: 60px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">Name</span></span></strong></h3></td>

        <td style="width: 60px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">ISP</span></span></strong></h3></td>

        <td style="width: 320px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">Line Used For</span></span></strong></h3></td>

        <td style="width: 70px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">D.L</span></span></strong></h3></td>

        <td style="width: 80px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">U.L</span></span></strong></h3></td>

        <td style="width: 200px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <Color: #000000;"><span style="font-family:Calibri,&quot;sans-serif&quot;;">Used</span></span></strong></h3></td>

        <td style="width: 100px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">Remaining</span></span></strong></h3></td>

        <td style="width: 180px"; bgcolor="#ff9900"><h3 style="text-align:center"><strong><span style="font-size:14pt; Color: #000000;">
        <span style="font-family:Calibri,&quot;sans-serif&quot;;">Consumption</span></span></strong></h3></td>

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
    def start(cls, results: list[dict], recipients: list, indicators: list[dict]) -> None:
        """
        Constructing Email in HTML Table Format and Send it to Recipients List
        """
        table: list = " ".join(convert_result_to_html(result, indicators) for result in results)
        Email.send(recipients, table)

    def send(recipients, table) -> None:
        """
        The Connecter to SMTP Server and Email Sender
         Using GMAIL Connection
        """

        msg = MIMEMultipart('alternative')  
        sender = 'smh-portal@andalusiagroup.net'
        alias = 'Netowork Automation'
        subject = "SMH Daily InternetCheck"

        msg['From'] = formataddr((alias, sender))
        msg['To'] = ','.join(recipients)
        msg['Subject'] = subject
        msg['CC'] = 'Adel.aly@andalusiagroup.net'

        html = (f"""\
        <p><span style="font-size:20px"><strong><Color: #000000;"><span style="font-family:Comic Sans MS,cursive"> {str(date.today())} </span></strong></span></p>

        <!DOCTYPE html>
        <html>
            <body>
            {" ".join([html_table(table)])}
            </body>
        </html>
        """)
        msg.attach(MIMEText(html, 'html'))

        s = smtplib.SMTP('smh-ex-03')
        s.sendmail(sender,recipients, msg.as_string())
        s.quit() 

if __name__ == "__main__":
    Email.send('smhit.bkp@gmail.com', "baypifdcneetnqio", "adel.aly@andalusiagroup.net", "test")