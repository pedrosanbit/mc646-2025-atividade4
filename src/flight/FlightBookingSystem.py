from datetime import datetime
from src.flight.BookingResult import BookingResult


class FlightBookingSystem:
    def book_flight(
        self,
        passengers: int,
        booking_time: datetime,
        available_seats: int,
        current_price: float,
        previous_sales: int,
        is_cancellation: bool,
        departure_time: datetime,
        reward_points_available: int,
    ) -> BookingResult:
        final_price = 0.0
        refund_amount = 0.0
        confirmation = False
        points_used = False

        if passengers > available_seats:
            return BookingResult(confirmation, final_price, refund_amount, points_used)

        price_factor = (previous_sales / 100.0) * 0.8
        final_price = current_price * price_factor * passengers

        time_difference = departure_time - booking_time
        hours_to_departure = time_difference.total_seconds() / 3600

        if hours_to_departure < 24:
            final_price += 100

        if passengers > 4:
            final_price *= 0.95

        if reward_points_available > 0:
            final_price -= reward_points_available * 0.01
            points_used = True

        if final_price < 0:
            final_price = 0

        if is_cancellation:
            if hours_to_departure >= 48:
                refund_amount = final_price
            else:
                refund_amount = final_price * 0.5

            return BookingResult(False, 0, refund_amount, False)

        confirmation = True

        return BookingResult(confirmation, final_price, refund_amount, points_used)