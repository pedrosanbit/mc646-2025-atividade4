import pytest
from datetime import datetime, timedelta
from src.fraud import FraudDetectionSystem, Transaction, FraudCheckResult

@pytest.fixture
def system():
    return FraudDetectionSystem()


# CT1 — Transação comum sem histórico
def test_normal_transaction_no_history(system):
    """Caminho base: nenhuma regra ativada"""
    tx = Transaction(5000, datetime.now(), "Brasil")
    result = system.check_for_fraud(tx, [], [])
    assert not result.is_fraudulent
    assert not result.is_blocked
    assert not result.verification_required
    assert result.risk_score == 0


# CT2 — Valor elevado (>10.000)
def test_high_value_transaction(system):
    """Ativa Regra 1 — valor elevado"""
    tx = Transaction(15000, datetime.now(), "Brasil")
    result = system.check_for_fraud(tx, [], [])
    assert result.is_fraudulent
    assert not result.is_blocked
    assert result.verification_required
    assert result.risk_score == 50


# CT3 — Excesso de transações em 1 hora (>10)
def test_excessive_transactions_in_one_hour(system):
    """Ativa Regra 2 — bloqueio por excesso de transações"""
    now = datetime.now()
    prev = [Transaction(100, now - timedelta(minutes=i*5), "Brasil") for i in range(11)]
    tx = Transaction(500, now, "Brasil")
    result = system.check_for_fraud(tx, prev, [])
    assert not result.is_fraudulent
    assert result.is_blocked
    assert not result.verification_required
    assert result.risk_score == 30


# CT4 — Limite exato (10 transações)
def test_transaction_limit_boundary(system):
    """Verifica fronteira de bloqueio: 10 transações não bloqueiam"""
    now = datetime.now()
    prev = [Transaction(100, now - timedelta(minutes=i*5), "Brasil") for i in range(10)]
    tx = Transaction(500, now, "Brasil")
    result = system.check_for_fraud(tx, prev, [])
    assert not result.is_blocked
    assert result.risk_score == 0


# CT5 — Mudança de país em menos de 30 minutos
def test_location_change_short_interval(system):
    """Ativa Regra 3 — mudança rápida de localização"""
    now = datetime.now()
    prev = [Transaction(100, now - timedelta(minutes=20), "França")]
    tx = Transaction(200, now, "EUA")
    result = system.check_for_fraud(tx, prev, [])
    assert result.is_fraudulent
    assert result.verification_required
    assert result.risk_score == 20


# CT6 — Mudança de país após 30 minutos
def test_location_change_after_30_minutes(system):
    """Aresta falsa da Regra 3 — tempo > 30 min"""
    now = datetime.now()
    prev = [Transaction(100, now - timedelta(minutes=45), "EUA")]
    tx = Transaction(200, now, "França")
    result = system.check_for_fraud(tx, prev, [])
    assert not result.is_fraudulent
    assert not result.verification_required
    assert result.risk_score == 0


# CT7 — Local em blacklist
def test_blacklisted_location(system):
    """Ativa Regra 4 — bloqueio automático"""
    tx = Transaction(500, datetime.now(), "País de Alto Risco")
    result = system.check_for_fraud(tx, [], ["País de Alto Risco"])
    assert not result.is_fraudulent
    assert result.is_blocked
    assert result.risk_score == 100


# CT8 — Valor alto + excesso + mudança de país
def test_combined_high_risk_conditions(system):
    """Combina Regras 1, 2 e 3 — risco acumulado até 100"""
    now = datetime.now()
    prev = [Transaction(100, now - timedelta(minutes=i*5), "França") for i in range(11)]
    tx = Transaction(15000, now, "EUA")
    result = system.check_for_fraud(tx, prev, [])
    assert result.is_fraudulent
    assert result.is_blocked
    assert result.verification_required
    assert result.risk_score == 80


# CT9 — Blacklist sobrepondo outras regras
def test_blacklist_overrides_other_rules(system):
    """Blacklist deve sobrescrever risco acumulado e forçar bloqueio"""
    tx = Transaction(20000, datetime.now(), "País de Alto Risco")
    prev = [Transaction(100, datetime.now() - timedelta(minutes=20), "EUA")]
    result = system.check_for_fraud(tx, prev, ["País de Alto Risco"])
    assert result.is_blocked
    assert result.risk_score == 100
    assert result.is_fraudulent
    assert result.verification_required
