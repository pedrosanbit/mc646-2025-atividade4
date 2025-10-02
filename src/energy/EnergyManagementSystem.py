from datetime import datetime
from src.energy.DeviceSchedule import DeviceSchedule
from src.energy.EnergyManagementResult import EnergyManagementResult

class SmartEnergyManagementSystem:
    """Um sistema para gerenciar inteligentemente o consumo de energia."""
    def manage_energy(
        self,
        current_price: float,
        price_threshold: float,
        device_priorities: dict[str, int],
        current_time: datetime,
        current_temperature: float,
        desired_temperature_range: tuple[float, float],
        energy_usage_limit: float,
        total_energy_used_today: float,
        scheduled_devices: list[DeviceSchedule],
    ) -> EnergyManagementResult:

        device_status: dict[str, bool] = {}
        energy_saving_mode = False
        temperature_regulation_active = False

        # 1. Ativa o modo de economia de energia se o preço exceder o limite
        if current_price > price_threshold:
            energy_saving_mode = True
            for device, priority in device_priorities.items():
                if priority > 1:  
                    device_status[device] = False
                else:
                    device_status[device] = True 
        else:
            # Sem modo de economia; mantém todos os dispositivos ligados inicialmente
            for device in device_priorities:
                device_status[device] = True

        # 2. Modo noturno entre 23h e 6h
        if current_time.hour >= 23 or current_time.hour < 6:
            for device in device_priorities:
                if device not in ("Security", "Refrigerator"):
                    device_status[device] = False

        # 3. Regulação de temperatura
        if current_temperature < desired_temperature_range[0]:
            device_status["Heating"] = True
            temperature_regulation_active = True
        elif current_temperature > desired_temperature_range[1]:
            device_status["Cooling"] = True
            temperature_regulation_active = True
        else:
            device_status["Heating"] = False
            device_status["Cooling"] = False


        devices_were_on = True
        while total_energy_used_today >= energy_usage_limit and devices_were_on:
            devices_to_turn_off = [
                device for device, priority in device_priorities.items()
                if device_status.get(device, False) and priority > 1
            ]
            
            if not devices_to_turn_off:
                devices_were_on = False
                continue

            for device in devices_to_turn_off:
                 if total_energy_used_today < energy_usage_limit:
                     break
                 device_status[device] = False
                 total_energy_used_today -= 1

        # 5. Lida com dispositivos agendados
        for schedule in scheduled_devices:
            if schedule.scheduled_time == current_time:
                device_status[schedule.device_name] = True

        return EnergyManagementResult(device_status, energy_saving_mode, temperature_regulation_active, total_energy_used_today)