from datetime import datetime


class DeviceSchedule:
    """Representa um agendamento de ativação para um dispositivo."""
    def __init__(self, device_name: str, scheduled_time: datetime):
        self.device_name = device_name
        self.scheduled_time = scheduled_time

    def __repr__(self) -> str:
        """Retorna uma representação legível do objeto."""
        return f"DeviceSchedule(device_name='{self.device_name}', scheduled_time='{self.scheduled_time}')"


