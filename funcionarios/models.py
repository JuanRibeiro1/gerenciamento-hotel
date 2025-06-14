from django.db import models


class Cargo(models.Model):
    nome_funcao = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return f"{self.nome_funcao}"


class Funcionario(models.Model):
    nome = models.CharField(max_length=50, blank=False)
    ativo = models.BooleanField(default=True)
    email = models.EmailField(max_length=254, blank=False)
    cargo = models.ForeignKey(Cargo, on_delete=models.RESTRICT, blank=False)

    def __str__(self):
        return f"Funcionário#{self.pk}:{self.nome} - {self.cargo}"
