class FraudCheckResult:
    """Armazena os resultados de uma verificação de detecção de fraude."""
    def __init__(self, is_fraudulent: bool, is_blocked: bool, verification_required: bool, risk_score: int):
        self.is_fraudulent = is_fraudulent
        self.is_blocked = is_blocked
        self.verification_required = verification_required
        self.risk_score = risk_score

    def __repr__(self) -> str:
        """Retorna uma representação legível do objeto."""
        return (f"FraudCheckResult(is_fraudulent={self.is_fraudulent}, "
                f"is_blocked={self.is_blocked}, "
                f"verification_required={self.verification_required}, "
                f"risk_score={self.risk_score})")