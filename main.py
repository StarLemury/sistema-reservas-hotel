from datetime import datetime
from models import (
    Cliente, Quarto, QuartoSolteiro, QuartoCasal, Suite, Reserva,
    HotelError, QuartoIndisponivelError, DataInvalidaError
)
from storage import salvar_dados, carregar_dados


def buscar_cliente(clientes: list[Cliente], documento: str) -> Cliente | None:
    for cliente in clientes:
        if cliente.documento == documento:
            return cliente
    return None


def buscar_quarto(quartos: list[Quarto], numero: int) -> Quarto | None:
    for quarto in quartos:
        if quarto.numero == numero:
            return quarto
    return None


def verificar_disponibilidade(reservas: list[Reserva], numero_quarto: int, check_in: str, check_out: str) -> bool:
    novo_in = datetime.strptime(check_in, "%d/%m/%Y")
    novo_out = datetime.strptime(check_out, "%d/%m/%Y")

    for reserva in reservas:
        if reserva.quarto.numero == numero_quarto:
            res_in = datetime.strptime(reserva.check_in, "%d/%m/%Y")
            res_out = datetime.strptime(reserva.check_out, "%d/%m/%Y")

            if novo_in < res_out and novo_out > res_in:
                return False
    return True


def validar_formato_data(data_str: str) -> None:
    try:
        datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        raise DataInvalidaError(f"Data '{data_str}' inválida. Use o formato DD/MM/AAAA.")


def cadastrar_cliente(clientes: list[Cliente], quartos: list[Quarto], reservas: list[Reserva]) -> None:
    print("\n--- CADASTRO DE CLIENTE ---")
    nome = input("Nome completo: ").strip()
    documento = input("Documento (CPF/RG): ").strip()
    contato = input("Contato (Telefone/E-mail): ").strip()

    if not nome or not documento or not contato:
        raise HotelError("Todos os campos do cliente são obrigatórios.")

    if buscar_cliente(clientes, documento):
        raise HotelError(f"Já existe um cliente cadastrado com o documento '{documento}'.")

    novo_cliente = Cliente(nome, documento, contato)
    clientes.append(novo_cliente)
    salvar_dados(clientes, quartos, reservas)
    print(f"Sucesso! Cliente '{nome}' cadastrado.")


def cadastrar_quarto(clientes: list[Cliente], quartos: list[Quarto], reservas: list[Reserva]) -> None:
    print("\n--- CADASTRO DE QUARTO ---")
    try:
        numero = int(input("Número do quarto: "))
        preco_base = float(input("Valor da diária (R$): ").replace(",", "."))
    except ValueError:
        raise HotelError("Número do quarto e preço devem ser valores numéricos.")

    if numero <= 0 or preco_base <= 0:
        raise HotelError("Número do quarto e preço devem ser maiores que zero.")

    if buscar_quarto(quartos, numero):
        raise HotelError(f"O quarto {numero} já está cadastrado.")

    print("Tipos de acomodação:")
    print("  1 - Quarto Solteiro")
    print("  2 - Quarto Casal")
    print("  3 - Suíte")
    tipo = input("Escolha o tipo (1/2/3): ").strip()

    if tipo == "1":
        quarto = QuartoSolteiro(numero, preco_base)
    elif tipo == "2":
        quarto = QuartoCasal(numero, preco_base)
    elif tipo == "3":
        quarto = Suite(numero, preco_base)
    else:
        raise HotelError("Tipo de acomodação inválido.")

    quartos.append(quarto)
    salvar_dados(clientes, quartos, reservas)
    print(f"Sucesso! {quarto} cadastrado.")


def realizar_reserva(clientes: list[Cliente], quartos: list[Quarto], reservas: list[Reserva]) -> None:
    print("\n--- NOVA RESERVA ---")
    if not clientes or not quartos:
        raise HotelError("É necessário ter ao menos um cliente e um quarto cadastrados.")

    documento = input("Documento do cliente: ").strip()
    cliente = buscar_cliente(clientes, documento)
    if not cliente:
        raise HotelError("Cliente não encontrado. Cadastre o cliente primeiro.")

    print("\nQuartos cadastrados:")
    for q in sorted(quartos, key=lambda x: x.numero):
        print(f"  {q}")

    try:
        num_quarto = int(input("\nNúmero do quarto desejado: "))
    except ValueError:
        raise HotelError("Número de quarto inválido.")

    quarto = buscar_quarto(quartos, num_quarto)
    if not quarto:
        raise HotelError(f"Quarto {num_quarto} não encontrado.")

    check_in = input("Data de Check-in (DD/MM/AAAA): ").strip()
    check_out = input("Data de Check-out (DD/MM/AAAA): ").strip()

    validar_formato_data(check_in)
    validar_formato_data(check_out)

    novo_id = max([r.id_reserva for r in reservas], default=0) + 1
    nova_reserva = Reserva(novo_id, cliente, quarto, check_in, check_out)

    if not verificar_disponibilidade(reservas, num_quarto, check_in, check_out):
        raise QuartoIndisponivelError(
            f"O Quarto {num_quarto:02d} já está reservado no período de {check_in} a {check_out}."
        )

    reservas.append(nova_reserva)
    salvar_dados(clientes, quartos, reservas)
    print(f"\nReserva confirmada!\n{nova_reserva}")


def listar_dados(clientes: list[Cliente], quartos: list[Quarto], reservas: list[Reserva]) -> None:
    print("\n=== CLIENTES CADASTRADOS ===")
    if not clientes:
        print("Nenhum cliente cadastrado.")
    for c in clientes:
        print(f" - {c}")

    print("\n=== QUARTOS CADASTRADOS ===")
    if not quartos:
        print("Nenhum quarto cadastrado.")
    for q in sorted(quartos, key=lambda x: x.numero):
        print(f" - {q}")

    print("\n=== RESERVAS ATIVAS ===")
    if not reservas:
        print("Nenhuma reserva registrada.")
    for r in reservas:
        print(f" - {r}")


def cancelar_reserva(clientes: list[Cliente], quartos: list[Quarto], reservas: list[Reserva]) -> None:
    print("\n--- CANCELAR RESERVA ---")
    if not reservas:
        raise HotelError("Não há reservas ativas para cancelar.")

    for r in reservas:
        print(f" - {r}")

    try:
        id_alvo = int(input("\nInforme o ID da reserva a cancelar: "))
    except ValueError:
        raise HotelError("ID inválido.")

    for i, reserva in enumerate(reservas):
        if reserva.id_reserva == id_alvo:
            removida = reservas.pop(i)
            salvar_dados(clientes, quartos, reservas)
            print(f"Reserva #{removida.id_reserva} cancelada com sucesso.")
            return

    raise HotelError(f"Reserva #{id_alvo} não encontrada.")


def main() -> None:
    clientes, quartos, reservas = carregar_dados()

    while True:
        print("\n" + "=" * 42)
        print("      SISTEMA DE RESERVAS DE HOTEL")
        print("=" * 42)
        print("1. Cadastrar Cliente")
        print("2. Cadastrar Quarto")
        print("3. Realizar Reserva")
        print("4. Listar Clientes, Quartos e Reservas")
        print("5. Cancelar Reserva")
        print("0. Sair")
        print("=" * 42)

        opcao = input("Escolha uma opção: ").strip()

        try:
            if opcao == "1":
                cadastrar_cliente(clientes, quartos, reservas)
            elif opcao == "2":
                cadastrar_quarto(clientes, quartos, reservas)
            elif opcao == "3":
                realizar_reserva(clientes, quartos, reservas)
            elif opcao == "4":
                listar_dados(clientes, quartos, reservas)
            elif opcao == "5":
                cancelar_reserva(clientes, quartos, reservas)
            elif opcao == "0":
                print("Encerrando o sistema. Até logo!")
                break
            else:
                print("Opção inválida! Tente novamente.")
        except HotelError as erro:
            print(f"\n[ERRO]: {erro}")
        except Exception as erro_inesperado:
            print(f"\n[ERRO INESPERADO]: {erro_inesperado}")


if __name__ == "__main__":
    main()