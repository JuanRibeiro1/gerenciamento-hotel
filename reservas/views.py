from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Reserva, STATUS_RESERVA_CHOICES
from .forms import ReservaForm, RelatorioReservas

STATUS_MAP = dict(STATUS_RESERVA_CHOICES)
ORDENACAO_RESERVA_LOOKUP = {
    "cliente": "cliente__nome",
    "data_entrada": "data_entrada",
    "status": "status",
    "data_saida": "data_saida",
}


@login_required
def reservas(request):
    query = request.GET.get('busca', '')

    if query:
        reservas = Reserva.objects.filter(
            cliente__nome__icontains=query, ativa=True
        )
    else:
        reservas = Reserva.objects.filter(ativa=True)

    dados = {
        'reservas': reservas,
        'query': query,
        'ativos': True,
    }

    return render(request, 'reservas/index.html', dados)


@login_required
def cadastrar_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('reservas:reservas')
        else:
            print(form.errors)
    else:
        form = ReservaForm()

    return render(request, 'reservas/cadastrar_reserva.html', {'form': form})


@login_required
def editar_reserva(request, id):
    try:
        reserva = Reserva.objects.get(id=id)
    except Reserva.DoesNotExist:
        return redirect('reservas:reservas')

    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            reserva_editada = form.save()
            if reserva_editada.ativa:
                return redirect('reservas:reservas')
            else:
                return redirect('reservas:reservas_inativas')
    else:
        form = ReservaForm(instance=reserva)

    return render(request, 'reservas/editar_reserva.html', {'form': form, 'reserva': reserva})


@login_required
def excluir_reserva(request, id):
    try:
        reserva = Reserva.objects.get(id=id)
        reserva.ativa = False
        reserva.save()
        messages.success(request, "Reserva excluída com sucesso.")
    except Reserva.DoesNotExist:
        messages.error(request, "Reserva não encontrada.")

    return redirect('reservas:reservas')


@login_required
def ativar_reserva(request, id):
    try:
        reserva = Reserva.objects.get(id=id)
    except Reserva.DoesNotExist:
        messages.error(request, "Reserva não encontrada.")
        return redirect('reservas:reservas_inativas')

    if not reserva.ativa:
        reserva.ativa = True
        reserva.save()
        messages.success(request, "Reserva reativada com sucesso.")
    else:
        messages.info(request, "A reserva já está ativa.")

    return redirect('reservas:reservas_inativas')


@login_required
def listar_inativas(request):
    query = request.GET.get('busca', '')

    if query:
        reservas = Reserva.objects.filter(
            ativa=False, cliente__nome__icontains=query
        )
    else:
        reservas = Reserva.objects.filter(ativa=False)

    return render(request, 'reservas/index.html', {'reservas': reservas, 'ativos': False, 'query': query})


@login_required
def ordenar_reservas_view(request, campo):
    busca = request.GET.get('busca', '')
    ativo_param = request.GET.get('ativo', 'true').lower()
    ativo = ativo_param == 'true'
    campo_ordenacao = ORDENACAO_RESERVA_LOOKUP.get(campo, 'id')

    reservas = Reserva.objects.filter(ativa=ativo)
    if busca:
        reservas = reservas.filter(cliente__nome__icontains=busca)

    reservas = reservas.order_by(campo_ordenacao)

    dados = {
        'reservas': reservas,
        'ativos': ativo,
        'query': busca,
    }
    return render(request, 'reservas/index.html', dados)


@login_required
def gerar_relatorio_reservas(request):

    form = RelatorioReservas(request.GET or None)
    reservas = Reserva.objects.select_related(
        'cliente', 'quarto', 'funcionario').all()

    if form.is_valid():
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        cliente = form.cleaned_data.get('cliente')
        status = form.cleaned_data.get('status')
        ativo = form.cleaned_data.get('ativo')
        quarto = form.cleaned_data.get('quarto')

        if data_inicio:
            reservas = reservas.filter(data_entrada__gte=data_inicio)
        if data_fim:
            reservas = reservas.filter(data_saida__lte=data_fim)
        if cliente:
            reservas = reservas.filter(cliente__nome__icontains=cliente)
        if status:
            reservas = reservas.filter(status=status)
        if ativo:
            reservas = reservas.filter(ativa=(ativo == 'ativo'))
        if quarto:
            reservas = reservas.filter(quarto__tipo__nome__icontains=quarto)

    for reserva in reservas:
        reserva.nome_status = STATUS_MAP.get(
            reserva.status, 'Desconhecido')

    context = {
        'form': form,
        'reservas': reservas,
    }
    return render(request, 'reservas/relatorio_reservas.html', context)
