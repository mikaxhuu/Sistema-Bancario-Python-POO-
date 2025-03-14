import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor > self._saldo or valor <= 0.0:
            print("\nOperação falhou: Saldo insuficiente ou valor inválido.")
            return False
        self._saldo -= valor
        print("\nSaque realizado com sucesso!")
        return True

    def depositar(self, valor):
        if valor <= 0.0:
            print("\nOperação falhou: Valor inválido.")
            return False
        self._saldo += valor
        print("\nDepósito realizado com sucesso!")
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500.0, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [t for t in self.historico.transacoes if t["Tipo"] == "Saque"]
        )

        if valor > self.limite:
            print(f"\nOperação falhou: Valor maior que o limite de R$ {self.limite:.2f}.")
        elif numero_saques >= self.limite_saques:
            print("\nOperação falhou: Limite de saques atingido.")
        else:
            return super().sacar(valor)
        return False

    def __str__(self):
        return (
            f"Agência: {self.agencia} | Conta Corrente: {self.numero} | "
            f"Titular: {self.cliente.nome}\n"
        )


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, tipo, valor):
        mascara_ptbr = "%d/%m/%Y %H:%M:%S"
        self._transacoes.append(
            {
                "Tipo": tipo,
                "Valor": valor,
                "Data": datetime.now().strftime(mascara_ptbr),
            }
        )


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao("Saque", self.valor)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao("Depósito", self.valor)

def menu():
    menu = """\n
    -_-_-_-_-_-_-_- MENU -_-_-_-_-_-_-_-

    [1] Criar Novo Cliente
    [2] Criar Nova Conta
    [3] Listar Contas
    [4] Depositar
    [5] Sacar
    [6] Extrato
    [0] Sair

    ==>> """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
    return None


def criar_cliente(clientes):
    cpf = input("Digite o CPF (somente números): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\nJá existe um cliente com esse CPF!")
        return

    nome = input("\nInforme o nome completo: ")
    data_nascimento = input("\nInforme a data de nascimento (DD-MM-AAAA): ")
    endereco = input("\nInforme o endereço (Logradouro, número - Bairro - Cidade/Sigla, Estado): ")

    cliente = PessoaFisica(cpf=cpf, nome=nome, data_nascimento=data_nascimento, endereco=endereco)
    clientes.append(cliente)
    print("\nCliente criado com sucesso!")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("\nDigite o CPF (somente números): ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nCliente não encontrado.")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)
    print("\nConta criada com sucesso!")


def listar_contas(contas):
    if not contas:
        print("\nNão há contas cadastradas.")
        return

    for conta in contas:
        print("-" * 50)
        print(textwrap.dedent(str(conta)))


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\nEsse cliente não possui conta.")
        return None
    return cliente.contas[0]


def depositar(clientes):
    cpf = input("Digite o CPF (somente números): ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nCliente não encontrado.")
        return

    valor = float(input("\nInforme o valor do depósito: "))
    conta = recuperar_conta_cliente(cliente)

    if conta:
        transacao = Deposito(valor)
        cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf = input("Digite o CPF (somente números): ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nCliente não encontrado.")
        return

    valor = float(input("\nInforme o valor do saque: "))
    conta = recuperar_conta_cliente(cliente)

    if conta:
        transacao = Saque(valor)
        cliente.realizar_transacao(conta, transacao)


def extrato(clientes):
    cpf = input("Digite o CPF (somente números): ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\nCliente não encontrado.")
        return

    conta = recuperar_conta_cliente(cliente)

    if conta:
        print("-" * 50)
        print("EXTRATO".center(50))
        print("-" * 50)

        if not conta.historico.transacoes:
            print("\nNão foram realizadas movimentações nessa conta.")
        else:
            for transacao in conta.historico.transacoes:
                print(f"{transacao['Data']} - {transacao['Tipo']}: R$ {transacao['Valor']:.2f}")

        print(f"\nSaldo Atual: R$ {conta.saldo:.2f}")
        print("-" * 50)


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "1":
            criar_cliente(clientes)

        elif opcao == "2":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "3":
            listar_contas(contas)

        elif opcao == "4":
            depositar(clientes)

        elif opcao == "5":
            sacar(clientes)

        elif opcao == "6":
            extrato(clientes)

        elif opcao == "0":
            print("\nVocê saiu do sistema, até logo!")
            break

        else:
            print("\nOpção inválida. Tente novamente.")


main()
