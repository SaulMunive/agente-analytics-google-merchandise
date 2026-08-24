import functions_framework
from flask import jsonify
from google.cloud import geminidataanalytics
from google.api_core import client_options
from google.protobuf.json_format import MessageToDict
import proto

# --- Configuración ---
BILLING_PROJECT = "courses-agent-dmc"
LOCATION = "us"  # multi-región EE.UU., donde vive el agente
DATA_AGENT_ID = "agent_cd394777-67dd-4be0-bad3-d4648d28b10e"

# Configurar endpoint según la ubicación
if LOCATION == "global":
    endpoint = "geminidataanalytics.googleapis.com"
elif "-" in LOCATION:
    endpoint = f"geminidataanalytics-{LOCATION}.googleapis.com"
else:
    endpoint = f"geminidataanalytics.{LOCATION}.rep.googleapis.com"

opts = client_options.ClientOptions(api_endpoint=endpoint)
data_chat_client = geminidataanalytics.DataChatServiceClient(client_options=opts)


def _cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }


def _value_to_dict(v):
    """Convierte recursivamente estructuras proto-plus (MapComposite /
    RepeatedComposite) a tipos nativos de Python serializables en JSON."""
    if isinstance(v, proto.marshal.collections.maps.MapComposite):
        return _map_to_dict(v)
    elif isinstance(v, proto.marshal.collections.RepeatedComposite):
        return [_value_to_dict(el) for el in v]
    elif isinstance(v, (int, float, str, bool)):
        return v
    else:
        try:
            return MessageToDict(v)
        except Exception:
            return str(v)


def _map_to_dict(d):
    out = {}
    for k in d:
        if isinstance(d[k], proto.marshal.collections.maps.MapComposite):
            out[k] = _map_to_dict(d[k])
        else:
            out[k] = _value_to_dict(d[k])
    return out


@functions_framework.http
def chat_with_agent(request):
    """
    Endpoint HTTP que recibe una pregunta en lenguaje natural y la reenvía
    al Data Agent de BigQuery (Conversational Analytics API), devolviendo
    el texto de respuesta final, una tabla de datos (si aplica) y una
    especificación de gráfico Vega-Lite (si el agente decidió graficar).

    Body esperado (JSON): {"question": "texto de la pregunta"}
    """
    # Manejo de preflight CORS
    if request.method == "OPTIONS":
        return ("", 204, _cors_headers())

    headers = _cors_headers()

    try:
        request_json = request.get_json(silent=True)
        if not request_json or "question" not in request_json:
            return (jsonify({"error": "Falta el campo 'question' en el body"}), 400, headers)

        question = request_json["question"]

        # Construir el mensaje del usuario
        messages = [geminidataanalytics.Message()]
        messages[0].user_message.text = question

        # Referencia al Data Agent ya publicado en BigQuery Studio
        data_agent_context = geminidataanalytics.DataAgentContext()
        data_agent_context.data_agent = (
            f"projects/{BILLING_PROJECT}/locations/{LOCATION}/dataAgents/{DATA_AGENT_ID}"
        )

        request_obj = geminidataanalytics.ChatRequest(
            parent=f"projects/{BILLING_PROJECT}/locations/{LOCATION}",
            messages=messages,
            data_agent_context=data_agent_context,
        )

        # Llamada en streaming al Data Agent (single-turn, sin estado)
        stream = data_chat_client.chat(request=request_obj, timeout=300)

        final_text = ""
        table_data = None
        chart_spec = None

        for response in stream:
            m = response.system_message

            if "text" in m:
                # Solo nos interesa el texto de tipo FINAL_RESPONSE.
                # Se ignora THOUGHT (razonamiento interno del agente).
                text_type = m.text.text_type
                is_final = (
                    text_type == 1
                    or str(text_type) == "FINAL_RESPONSE"
                    or getattr(text_type, "name", "") == "FINAL_RESPONSE"
                )
                if is_final:
                    final_text += "".join(m.text.parts)

            elif "data" in m and "result" in m.data:
                fields = [f.name for f in m.data.result.schema.fields]
                rows = []
                for el in m.data.result.data:
                    row = {field: el[field] for field in fields}
                    rows.append(row)
                table_data = rows

            elif "chart" in m and "result" in m.chart:
                try:
                    chart_spec = _map_to_dict(m.chart.result.vega_config)
                except Exception:
                    chart_spec = None

        if not final_text:
            final_text = (
                "El agente procesó la consulta pero no devolvió un texto final. "
                "Revisa la tabla de datos si está disponible."
            )

        return (
            jsonify({"answer": final_text, "table": table_data, "chart": chart_spec}),
            200,
            headers,
        )

    except Exception as e:
        return (jsonify({"error": str(e)}), 500, headers)
