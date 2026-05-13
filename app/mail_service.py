import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

def enviar_comprobante(
    destino,
    usuario,
    documento,
    estado,
    fecha,
    observacion=None
):

    html = f"""
    <h2>Comprobante de documento</h2>

    <p>Hola {usuario}</p>

    <p>Tu documento fue procesado.</p>

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

    params = {
        "from": "RRHH <rrhh@casteable.cl>",
        "to": destinatarios,
        "subject": f"Documento {estado}",
        "html": html
    }

    resend.Emails.send(params)