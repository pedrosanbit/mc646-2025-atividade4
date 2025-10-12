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
    assert result.final_price > 0
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
    assert result.final_price == 0
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
    assert result.final_price >= 100  # pelo menos taxa aplicada
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
    assert result.final_price > 0
    assert result.final_price < 100 * ((50/100.0)*0.8*5)  # confirma desconto aplicado
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
    assert result.final_price >= 0


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
    assert result.final_price >= 0


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
    assert result.final_price == 0
    assert result.points_used
