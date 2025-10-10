from src.fraud.Transaction import Transaction
from src.fraud.FraudCheckResult import FraudCheckResult


class FraudDetectionSystem:
    def check_for_fraud(
        self,
        current_transaction: Transaction,
        previous_transactions: list[Transaction],
        blacklisted_locations: list[str],
    ) -> FraudCheckResult:
        is_fraudulent = False
        is_blocked = False
        verification_required = False
        risk_score = 0
        if current_transaction.amount > 10000:
            is_fraudulent = True
            verification_required = True
            risk_score += 50
        recent_transaction_count = 0
        for transaction in previous_transactions:
            time_difference = current_transaction.timestamp - transaction.timestamp
            time_diff_minutes = time_difference.total_seconds() / 60
            if time_diff_minutes <= 60:
                recent_transaction_count += 1
        
        if recent_transaction_count > 10:
            is_blocked = True
            risk_score += 30
        if previous_transactions:
            last_transaction = previous_transactions[-1]
            time_since_last = current_transaction.timestamp - last_transaction.timestamp
            minutes_since_last = time_since_last.total_seconds() / 60
            
            if minutes_since_last < 30 and last_transaction.location != current_transaction.location:
                is_fraudulent = True
                verification_required = True
                risk_score += 20
        if current_transaction.location in blacklisted_locations:
            is_blocked = True
            risk_score = 100

        return FraudCheckResult(is_fraudulent, is_blocked, verification_required, risk_score)