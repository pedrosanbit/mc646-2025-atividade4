import pytest
from datetime import datetime, timedelta
from src.flight import FlightBookingSystem, BookingResult

@pytest.fixture
def system():
    return FlightBookingSystem()

# FT1 — Reserva simples, assentos suficientes, horas > 24, pontos=0
def test_simple_booking(system):
    """Caminho base: assentos disponíveis, sem taxas e sem pontos"""
    now = datetime.now()
    result = system.book_flight(
        passengers=2,
        booking_time=now,
        available_seats=5,
        current_price=500,
        previous_sales=50,
        is_cancellation=False,
        departure_time=now + timedelta(days=2),
        reward_points_available=0
    )
    assert result.confirmation
    assert result.total_price > 0
    assert not result.points_used
    assert result.refund_amount == 0


# FT2 — Falta de assentos
def test_insufficient_seats(system):
    """Ativa regra de rejeição por assentos insuficientes"""
    now = datetime.now()
    result = system.book_flight(
        passengers=6,
        booking_time=now,
        available_seats=5,
        current_price=500,
        previous_sales=50,
        is_cancellation=False,
        departure_time=now + timedelta(days=2),
        reward_points_available=0
    )
    assert not result.confirmation
    assert result.total_price == 0
    assert result.refund_amount == 0
    assert not result.points_used


# FT3 — Última hora (<24h)
def test_last_minute_booking(system):
    """Ativa taxa de última hora"""
    now = datetime.now()
    result = system.book_flight(
        passengers=1,
        booking_time=now,
        available_seats=5,
        current_price=200,
        previous_sales=20,
        is_cancellation=False,
        departure_time=now + timedelta(hours=10),
        reward_points_available=0
    )
    assert result.confirmation
    assert result.total_price >= 100  # pelo menos taxa aplicada
    assert not result.points_used


# FT4 — Reserva em grupo (>4 passageiros)
def test_group_booking_discount(system):
    """Ativa desconto de 5% para grupos"""
    now = datetime.now()
    result = system.book_flight(
        passengers=5,
        booking_time=now,
        available_seats=10,
        current_price=100,
        previous_sales=50,
        is_cancellation=False,
        departure_time=now + timedelta(days=2),
        reward_points_available=0
    )
    assert result.confirmation
    assert result.total_price > 0
    assert result.total_price < 100 * ((50/100.0)*0.8*5)  # confirma desconto aplicado
    assert not result.points_used


# FT5 — Uso de pontos de recompensa
def test_reward_points_usage(system):
    """Ativa resgate de pontos"""
    now = datetime.now()
    result = system.book_flight(
        passengers=2,
        booking_time=now,
        available_seats=5,
        current_price=300,
        previous_sales=50,
        is_cancellation=False,
        departure_time=now + timedelta(days=2),
        reward_points_available=500
    )
    assert result.confirmation
    assert result.points_used
    assert result.total_price >= 0


# FT6 — Cancelamento >48h antes
def test_cancellation_full_refund(system):
    """Cancelamento com reembolso total"""
    now = datetime.now()
    result = system.book_flight(
        passengers=2,
        booking_time=now,
        available_seats=5,
        current_price=300,
        previous_sales=50,
        is_cancellation=True,
        departure_time=now + timedelta(days=3),
        reward_points_available=100
    )
    assert not result.confirmation
    assert result.refund_amount > 0
    assert not result.points_used


# FT7 — Cancelamento <48h antes
def test_cancellation_partial_refund(system):
    """Cancelamento com reembolso parcial"""
    now = datetime.now()
    result = system.book_flight(
        passengers=2,
        booking_time=now,
        available_seats=5,
        current_price=300,
        previous_sales=50,
        is_cancellation=True,
        departure_time=now + timedelta(hours=36),
        reward_points_available=100
    )
    assert not result.confirmation
    assert result.refund_amount > 0
    assert result.refund_amount < 300 * ((50/100.0)*0.8*2 + 0)  # menor que valor total
    assert not result.points_used


# FT8 — Combinação: grupo + última hora + pontos
def test_complex_combination(system):
    """Reserva em grupo, última hora, uso de pontos"""
    now = datetime.now()
    result = system.book_flight(
        passengers=6,
        booking_time=now,
        available_seats=10,
        current_price=200,
        previous_sales=80,
        is_cancellation=False,
        departure_time=now + timedelta(hours=12),
        reward_points_available=1000
    )
    assert result.confirmation
    assert result.points_used
    assert result.total_price >= 0


# FT9 — Preço negativo por pontos > tarifa
def test_negative_price_due_to_points(system):
    """Garantia de preço mínimo zero"""
    now = datetime.now()
    result = system.book_flight(
        passengers=1,
        booking_time=now,
        available_seats=5,
        current_price=50,
        previous_sales=10,
        is_cancellation=False,
        departure_time=now + timedelta(days=2),
        reward_points_available=5000  # muito alto, > preço final
    )
    assert result.confirmation
    assert result.total_price == 0
    assert result.points_used


# FT10 — Fronteira: passengers == available_seats (deve ter sucesso)
def test_exact_seat_match(system):
    """Mutante 17: Testa fronteira onde passageiros igualam assentos disponíveis"""
    now = datetime.now()
    result = system.book_flight(
        passengers=5,
        booking_time=now,
        available_seats=5,
        current_price=300,
        previous_sales=50,
        is_cancellation=False,
        departure_time=now + timedelta(days=2),
        reward_points_available=0
    )
    assert result.confirmation
    assert result.total_price > 0


# FT11 — Fronteira: exatamente 4 passageiros (sem desconto de grupo)
def test_exactly_four_passengers(system):
    """Mutante 36: Testa fronteira com exatamente 4 passageiros - sem desconto"""
    now = datetime.now()
    result = system.book_flight(
        passengers=4,
        booking_time=now,
        available_seats=10,
        current_price=100,
        previous_sales=50,
        is_cancellation=False,
        departure_time=now + timedelta(days=2),
        reward_points_available=0
    )
    expected_no_discount = 100 * (50/100.0) * 0.8 * 4
    assert result.confirmation
    assert abs(result.total_price - expected_no_discount) < 0.01


# FT12 — Fronteira: exatamente 24 horas antes da partida (sem taxa)
def test_exactly_24_hours(system):
    """Mutantes 31, 32: Testa fronteira em exatamente 24 horas - sem taxa de última hora"""
    now = datetime.now()
    result = system.book_flight(
        passengers=1,
        booking_time=now,
        available_seats=5,
        current_price=200,
        previous_sales=50,
        is_cancellation=False,
        departure_time=now + timedelta(hours=24),
        reward_points_available=0
    )
    expected = 200 * (50/100.0) * 0.8 * 1
    assert result.confirmation
    assert abs(result.total_price - expected) < 0.01


# FT13 — Fronteira: exatamente 48 horas antes da partida (reembolso total)
def test_cancellation_exactly_48_hours(system):
    """Mutantes 53, 54: Testa fronteira em exatamente 48 horas - reembolso total"""
    now = datetime.now()
    result = system.book_flight(
        passengers=2,
        booking_time=now,
        available_seats=5,
        current_price=300,
        previous_sales=50,
        is_cancellation=True,
        departure_time=now + timedelta(hours=48),
        reward_points_available=0
    )
    expected_price = 300 * (50/100.0) * 0.8 * 2
    assert not result.confirmation
    assert abs(result.refund_amount - expected_price) < 0.01
    assert result.total_price == 0


# FT14 — Exatamente 1 ponto de recompensa
def test_one_reward_point(system):
    """Mutante 42: Testa com exatamente 1 ponto de recompensa"""
    now = datetime.now()
    result = system.book_flight(
        passengers=1,
        booking_time=now,
        available_seats=5,
        current_price=200,
        previous_sales=50,
        is_cancellation=False,
        departure_time=now + timedelta(days=2),
        reward_points_available=1
    )
    assert result.confirmation
    assert result.points_used
    expected_base = 200 * (50/100.0) * 0.8
    assert result.total_price < expected_base


# FT15 — Validação do cálculo de preço (multiplicação, não divisão)
def test_price_calculation_per_passenger(system):
    """Mutante 24: Verifica que o preço aumenta com passageiros (multiplicação)"""
    now = datetime.now()
    result1 = system.book_flight(
        passengers=1,
        booking_time=now,
        available_seats=5,
        current_price=100,
        previous_sales=50,
        is_cancellation=False,
        departure_time=now + timedelta(days=2),
        reward_points_available=0
    )
    result2 = system.book_flight(
        passengers=2,
        booking_time=now,
        available_seats=5,
        current_price=100,
        previous_sales=50,
        is_cancellation=False,
        departure_time=now + timedelta(days=2),
        reward_points_available=0
    )
    assert result2.total_price > result1.total_price
    assert abs(result2.total_price / result1.total_price - 2.0) < 0.01


# FT16 — Taxa de última hora é aditiva
def test_last_minute_fee_additive(system):
    """Mutante 33: Verifica que a taxa de 100 é adicionada, não definida"""
    now = datetime.now()
    result = system.book_flight(
        passengers=2,
        booking_time=now,
        available_seats=5,
        current_price=200,
        previous_sales=50,
        is_cancellation=False,
        departure_time=now + timedelta(hours=10),
        reward_points_available=0
    )
    base_price = 200 * (50/100.0) * 0.8 * 2
    expected = base_price + 100
    assert result.confirmation
    assert abs(result.total_price - expected) < 0.01
    assert result.total_price > 100


# FT17 — Desconto de grupo é multiplicativo
def test_group_discount_multiplicative(system):
    """Mutante 38: Verifica que o desconto multiplica, não substitui"""
    now = datetime.now()
    result = system.book_flight(
        passengers=5,
        booking_time=now,
        available_seats=10,
        current_price=200,
        previous_sales=50,
        is_cancellation=False,
        departure_time=now + timedelta(days=2),
        reward_points_available=0
    )
    base_price = 200 * (50/100.0) * 0.8 * 5
    expected = base_price * 0.95
    assert result.confirmation
    assert abs(result.total_price - expected) < 0.01
    assert result.total_price > 0.95


# FT18 — Verificação explícita de tipos booleanos
def test_boolean_types_on_failure(system):
    """Mutantes 14, 16: Garante que booleanos são do tipo correto, não None"""
    now = datetime.now()
    result = system.book_flight(
        passengers=10,
        booking_time=now,
        available_seats=5,
        current_price=200,
        previous_sales=50,
        is_cancellation=False,
        departure_time=now + timedelta(days=2),
        reward_points_available=0
    )
    assert result.confirmation is False
    assert result.points_used is False
    assert isinstance(result.confirmation, bool)
    assert isinstance(result.points_used, bool)
