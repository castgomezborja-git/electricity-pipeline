import requests

url = "https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real"
params = {
    "start_date": "2026-09-11T00:00",
    "end_date": "2026-09-12T23:59",
    "time_trunc": "hour",
}

response = requests.get(url, params=params)
print(response.status_code)
print(response.json())
