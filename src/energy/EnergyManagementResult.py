class EnergyManagementResult:
    """Armazena os resultados da lógica de gerenciamento de energia."""
    def __init__(
        self,
        device_status: dict[str, bool],
        energy_saving_mode: bool,
        temperature_regulation_active: bool,
        total_energy_used: float,
    ):
        self.device_status = device_status
        self.energy_saving_mode = energy_saving_mode
        self.temperature_regulation_active = temperature_regulation_active
        self.total_energy_used = total_energy_used

    def __repr__(self) -> str:
        """Retorna uma representação legível do objeto."""
        return (f"EnergyManagementResult(device_status={self.device_status}, "
                f"energy_saving_mode={self.energy_saving_mode}, "
                f"temperature_regulation_active={self.temperature_regulation_active}, "
                f"total_energy_used={self.total_energy_used})")