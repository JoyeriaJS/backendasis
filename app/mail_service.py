import os
import resend
import requests
import base64

resend.api_key = os.getenv("RESEND_API_KEY")


def enviar_comprobante(
    destino,
    usuario,
    documento,
    estado,
    fecha,
    observacion=None,
    archivo_url=None,
    nombre_archivo=None
):

    html = f"""
    <h2>Comprobante de documento</h2>

    <p>Hola {usuario}</p>

    <p>Tu documento fue procesado correctamente.</p>

    <ul>
        <li><strong>Documento:</strong> {documento}</li>
        <li><strong>Estado:</strong> {estado}</li>
        <li><strong>Fecha:</strong> {fecha}</li>
    </ul>

    <p>
        <strong>Observación:</strong><br>
        {observacion or 'Sin observación'}
    </p>
    """

    destinatarios = [destino]

    # 🔥 ALERTA RRHH SI RECHAZA
    if estado == "rechazado":
        destinatarios.append("casteable.js@gmail.com")

    attachments = []

    # 🔥 ADJUNTAR PDF
    if archivo_url:

        try:

            response = requests.get(archivo_url)

            if response.status_code == 200:

                pdf_base64 = base64.b64encode(
                    response.content
                ).decode("utf-8")

                attachments.append({
                    "filename": nombre_archivo or "documento.pdf",
                    "content": pdf_base64
                })

        except Exception as e:

            print("❌ ERROR ADJUNTANDO PDF:")
            print(str(e))

    params = {
        "from": "RRHH <rrhh@casteable.cl>",
        "to": destinatarios,
        "subject": f"Documento {estado}",
        "html": html,
        "attachments": attachments
    }

    try:

        resend.Emails.send(params)

        print("✅ CORREO ENVIADO")

    except Exception as e:

        print("❌ ERROR RESEND:")
        print(str(e))
