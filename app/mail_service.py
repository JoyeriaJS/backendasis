import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = "smtp.hostinger.com"
SMTP_PORT = 465

EMAIL = "rrhh@casteable.cl"
PASSWORD = "TU_PASSWORD"


def enviar_comprobante(
    destino,
    usuario,
    documento,
    estado,
    fecha,
    observacion=None
):

    try:

        print("INICIANDO SMTP")

        asunto = f"Comprobante de documento {estado}"

        body = f"""
Hola {usuario}

Tu documento fue procesado.

Documento: {documento}
Estado: {estado}
Fecha: {fecha}

Observación:
{observacion or 'Sin observación'}

Sistema de Gestión Documental
"""

        mensaje = MIMEMultipart()

        mensaje["From"] = EMAIL
        mensaje["To"] = destino
        mensaje["Subject"] = asunto

        mensaje.attach(MIMEText(body, "plain"))

        print("CONECTANDO")

        server = smtplib.SMTP_SSL(
            SMTP_SERVER,
            SMTP_PORT
        )

        print("LOGIN")

        server.login(EMAIL, PASSWORD)

        print("ENVIANDO")

        server.sendmail(
            EMAIL,
            destino,
            mensaje.as_string()
        )

        server.quit()

        print("CORREO ENVIADO")

    except Exception as e:

        print("ERROR SMTP:")
        print(str(e))