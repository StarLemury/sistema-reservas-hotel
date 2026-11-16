import json
import os
from models import Cliente, Quarto, Reserva

ARQUIVO_DADOS = "dados_hotel.json"


def salvar_dados(clientes: list[Cliente], quartos: list[Quarto], reservas: list[Reserva]) -> None:
    dados = {
        "clientes": [c.to_dict() for c in clientes],
        "quartos": [q.to_dict() for q in quartos],
        "reservas": [r.to_dict() for r in reservas]
    }
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)


def carregar_dados() -> tuple[list[Cliente], list[Quarto], list[Reserva]]:
    if not os.path.exists(ARQUIVO_DADOS):
        return [], [], []

    try:
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (json.JSONDecodeError, IOError):
        return [], [], []

    clientes = [Cliente.from_dict(c) for c in dados.get("clientes", [])]
    quartos = [Quarto.from_dict(q) for q in dados.get("quartos", [])]

    mapa_clientes = {c.documento: c for c in clientes}
    mapa_quartos = {q.numero: q for q in quartos}

    reservas = []
    for r in dados.get("reservas", []):
        cliente = mapa_clientes.get(r["cliente_doc"])
        quarto = mapa_quartos.get(r["quarto_numero"])
        if cliente and quarto:
            reserva = Reserva(
                id_reserva=r["id_reserva"],
                cliente=cliente,
                quarto=quarto,
                check_in=r["check_in"],
                check_out=r["check_out"]
            )
            reservas.append(reserva)

    return clientes, quartos, reservas