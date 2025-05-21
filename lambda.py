import json
import requests

def lambda_handler(event, context):
    # Parse del body JSON (API Gateway passa tutto come stringa)
    print("Event:", event)  # stampa l'intero evento nel CloudWatch Logs
    try:
        body = json.loads(event.get('body', '{}'))
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Body non valido"})
        }

    prompt = body.get("prompt")
    top_k = body.get("top_k", 1)

    if not prompt:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Parametro 'prompt' mancante"})
        }

    # URL della tua API FastAPI sulla EC2
    api_url = "http://3.90.186.56:8000/fake-news"

    payload = {
        "text": prompt,
        "top_k": top_k
    }

    try:
        # Chiamata POST alla API EC2
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # solleva errori HTTP

        data = response.json()

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(data)
        }

    except requests.exceptions.RequestException as e:
        # Gestione errori di rete o HTTP
        return {
            "statusCode": 502,
            "body": json.dumps({"error": "Errore nella chiamata API EC2", "details": str(e)})
        }
