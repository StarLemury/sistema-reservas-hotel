from datetime import datetime


class HotelError(Exception):
    pass


class QuartoIndisponivelError(HotelError):
    pass


class DataInvalidaError(HotelError):
    pass


class Cliente:
    def __init__(self, nome: str, documento: str, contato: str):
        self.nome = nome
        self.documento = documento
        self.contato = contato

    def to_dict(self) -> dict:
        return {
            "nome": self.nome,
            "documento": self.documento,
            "contato": self.contato
        }

    @classmethod
    def from_dict(cls, dados: dict):
        return cls(dados["nome"], dados["documento"], dados["contato"])

    def __str__(self) -> str:
        return f"{self.nome} (Doc: {self.documento} | Contato: {self.contato})"


class Quarto:
    def __init__(self, numero: int, preco_base: float):
        self.numero = numero
        self.preco_base = preco_base
        self.tipo = "Padrão"

    def calcular_diaria(self) -> float:
        return self.preco_base

    def to_dict(self) -> dict:
        return {
            "numero": self.numero,
            "preco_base": self.preco_base,
            "tipo": self.tipo
        }

    @staticmethod
    def from_dict(dados: dict):
        tipo = dados.get("tipo")
        numero = dados["numero"]
        preco = dados["preco_base"]

        if tipo == "Solteiro":
            return QuartoSolteiro(numero, preco)
        elif tipo == "Casal":
            return QuartoCasal(numero, preco)
        elif tipo == "Suíte":
            return Suite(numero, preco)
        return Quarto(numero, preco)

    def __str__(self) -> str:
        return f"Quarto {self.numero:02d} [{self.tipo}] - Diária: R$ {self.calcular_diaria():.2f}"


class QuartoSolteiro(Quarto):
    def __init__(self, numero: int, preco_base: float):
        super().__init__(numero, preco_base)
        self.tipo = "Solteiro"

    def calcular_diaria(self) -> float:
        return self.preco_base


class QuartoCasal(Quarto):
    def __init__(self, numero: int, preco_base: float):
        super().__init__(numero, preco_base)
        self.tipo = "Casal"

    def calcular_diaria(self) -> float:
        return self.preco_base


class Suite(Quarto):
    def __init__(self, numero: int, preco_base: float):
        super().__init__(numero, preco_base)
        self.tipo = "Suíte"

    def calcular_diaria(self) -> float:
        return self.preco_base


class Reserva:
    def __init__(self, id_reserva: int, cliente: Cliente, quarto: Quarto, check_in: str, check_out: str):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.quarto = quarto
        self.check_in = check_in
        self.check_out = check_out
        self.dias = self._calcular_dias()
        self.valor_total = self.dias * self.quarto.calcular_diaria()

    def _calcular_dias(self) -> int:
        dt_in = datetime.strptime(self.check_in, "%d/%m/%Y")
        dt_out = datetime.strptime(self.check_out, "%d/%m/%Y")
        diferenca = (dt_out - dt_in).days

        if diferenca <= 0:
            raise DataInvalidaError("A data de check-out deve ser posterior à data de check-in.")
        return diferenca

    def to_dict(self) -> dict:
        return {
            "id_reserva": self.id_reserva,
            "cliente_doc": self.cliente.documento,
            "quarto_numero": self.quarto.numero,
            "check_in": self.check_in,
            "check_out": self.check_out
        }

    def __str__(self) -> str:
        return (
            f"Reserva #{self.id_reserva} | Cliente: {self.cliente.nome} | "
            f"Quarto {self.quarto.numero:02d} ({self.quarto.tipo}) | "
            f"{self.check_in} a {self.check_out} ({self.dias} diárias) | "
            f"Total: R$ {self.valor_total:.2f}"
        )