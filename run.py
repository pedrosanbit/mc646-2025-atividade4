from src.fraud.FraudDetectionSystem import FraudDetectionSystem
from src.fraud.Transaction import Transaction
from datetime import datetime, timedelta

def run_fraud_detection_system():
    fds = FraudDetectionSystem()
    # Aqui você pode adicionar
    fds.check_for_fraud(
        current_transaction=Transaction(
            amount=15000,
            timestamp=datetime.now(),
            location="New York"
        ),
        previous_transactions=[
            Transaction(
                amount=5000,
                timestamp=datetime.now() - timedelta(minutes=10),
                location="Los Angeles"
            ),
            Transaction(
                amount=20000,
                timestamp=datetime.now() - timedelta(minutes=5),
                location="New York"
            )
        ],
        blacklisted_locations=["Las Vegas", "Miami"]
    )
if __name__ == "__main__":
    run_fraud_detection_system()