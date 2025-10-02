class BookingResult:
    """
    Uma classe para armazenar o resultado de uma operação de reserva de voo.
    """
    def __init__(self, confirmation, total_price, refund_amount, points_used):
        self.confirmation = confirmation
        self.total_price = total_price
        self.refund_amount = refund_amount
        self.points_used = points_used

    def __repr__(self):
        """Retorna uma representação legível do objeto."""
        return (f"BookingResult(confirmation={self.confirmation}, "
                f"total_price={self.total_price:.2f}, "
                f"refund_amount={self.refund_amount:.2f}, "
                f"points_used={self.points_used})")