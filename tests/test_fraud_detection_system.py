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


# CT10 — Fronteira: exatamente 10000 (NÃO deve acionar fraude)
def test_transaction_exactly_10000(system):
    """Mutantes 72, 73: Testa fronteira em exatamente 10000 - sem fraude"""
    tx = Transaction(10000, datetime.now(), "Brasil")
    result = system.check_for_fraud(tx, [], [])
    assert not result.is_fraudulent
    assert result.risk_score == 0


# CT11 — Fronteira: exatamente 60 minutos entre transações
def test_transaction_exactly_60_minutes(system):
    """Mutantes 88, 89: Testa fronteira em exatamente 60 minutos"""
    now = datetime.now()
    prev = [Transaction(100, now - timedelta(minutes=60), "Brasil")]
    tx = Transaction(500, now, "Brasil")
    result = system.check_for_fraud(tx, prev, [])
    assert not result.is_blocked
    assert result.risk_score == 0


# CT12 — Fronteira: exatamente 30 minutos para mudança de local
def test_location_change_exactly_30_minutes(system):
    """Mutantes 108, 109: Testa fronteira em exatamente 30 minutos"""
    now = datetime.now()
    prev = [Transaction(100, now - timedelta(minutes=30), "França")]
    tx = Transaction(200, now, "EUA")
    result = system.check_for_fraud(tx, prev, [])
    assert not result.is_fraudulent
    assert result.risk_score == 0


# CT13 — Exatamente 10 transações (NÃO deve bloquear)
def test_exactly_10_transactions(system):
    """Testa fronteira com exatamente 10 transações anteriores"""
    now = datetime.now()
    prev = [Transaction(100, now - timedelta(minutes=i*5), "Brasil") for i in range(10)]
    tx = Transaction(500, now, "Brasil")
    result = system.check_for_fraud(tx, prev, [])
    assert not result.is_blocked
    assert result.risk_score == 0


# CT14 — Acumulação de pontuação de risco: valor alto + mudança de local
def test_risk_score_accumulates_value_and_location(system):
    """Mutantes 78, 116: Verifica que pontuações de risco se acumulam, não substituem"""
    now = datetime.now()
    prev = [Transaction(100, now - timedelta(minutes=20), "França")]
    tx = Transaction(15000, now, "EUA")
    result = system.check_for_fraud(tx, prev, [])
    assert result.is_fraudulent
    assert result.verification_required
    assert result.risk_score == 70


# CT15 — Acumulação de pontuação de risco: apenas valor alto
def test_risk_score_high_value_only(system):
    """Verifica que a pontuação de risco é definida corretamente para condição única"""
    tx = Transaction(15000, datetime.now(), "Brasil")
    result = system.check_for_fraud(tx, [], [])
    assert result.is_fraudulent
    assert result.risk_score == 50  # Exatamente 50, não 0


# CT16 — Acumulação de pontuação de risco: apenas mudança de local
def test_risk_score_location_only(system):
    """Verifica que a pontuação de risco é definida corretamente para mudança de local"""
    now = datetime.now()
    prev = [Transaction(100, now - timedelta(minutes=20), "França")]
    tx = Transaction(5000, now, "EUA")  # Não valor alto, apenas mudança de local
    result = system.check_for_fraud(tx, prev, [])
    assert result.is_fraudulent
    assert result.risk_score == 20  # Exatamente 20, não 0


# CT17 — Verificação explícita de tipos booleanos para transação normal
def test_boolean_types_normal_transaction(system):
    """Mutantes 65, 67, 69: Garante que booleanos são do tipo correto, não None"""
    tx = Transaction(5000, datetime.now(), "Brasil")
    result = system.check_for_fraud(tx, [], [])
    assert result.is_fraudulent is False  # False explícito, não None
    assert result.is_blocked is False  # False explícito, não None
    assert result.verification_required is False  # False explícito, não None
    assert isinstance(result.is_fraudulent, bool)
    assert isinstance(result.is_blocked, bool)
    assert isinstance(result.verification_required, bool)


# CT18 — Múltiplas transações em intervalos de exatamente 60 minutos
def test_multiple_transactions_at_60_minute_boundary(system):
    """Testa contagem de transações na fronteira de 60 minutos"""
    now = datetime.now()
    prev = [
        Transaction(100, now - timedelta(minutes=60), "Brasil"),
        *[Transaction(100, now - timedelta(minutes=i*5), "Brasil") for i in range(1, 11)]
    ]
    tx = Transaction(500, now, "Brasil")
    result = system.check_for_fraud(tx, prev, [])
    assert result.is_blocked
    assert result.risk_score == 30


# CT19 — Mudança de local com mesmo local (não deve acionar)
def test_same_location_no_fraud(system):
    """Verifica que detecção de mudança de local requer localizações diferentes"""
    now = datetime.now()
    prev = [Transaction(100, now - timedelta(minutes=10), "Brasil")]
    tx = Transaction(200, now, "Brasil")
    result = system.check_for_fraud(tx, prev, [])
    assert not result.is_fraudulent
    assert result.risk_score == 0
