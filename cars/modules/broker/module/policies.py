# Политики безопасности
policies = (
    # IoT Система
    {"src": "conn_with_manag_sys", "dst": "command_validator"},
    {"src": "eblocks", "dst": "conn_with_manag_sys"},
    {"src": "park_management_system", "dst": "conn_with_manag_sys"},
    {"src": "conn_with_manag_sys", "dst": "park_management_system"},
    {"src": "payment_validator", "dst": "conn_with_manag_sys"},
    {"src": "conn_with_manag_sys", "dst": "payment_validator"},
    {"src": "acccess_validator", "dst": "conn_with_manag_sys"},
    {"src": "conn_with_manag_sys", "dst": "acccess_validator"},
    {"src": "ic", "dst": "conn_with_manag_sys"},

    {"src": "conn_with_mob_app", "dst": "mobile-client"},
    {"src": "mobile-client", "dst": "conn_with_mob_app"},
    {"src": "conn_with_mob_app", "dst": "payment_validator"},
    {"src": "payment_validator", "dst": "conn_with_mob_app"},
    {"src": "conn_with_mob_app", "dst": "access_validator"},
    {"src": "access_validator", "dst": "conn_with_mob_app"},
    {"src": "conn_with_mob_app", "dst": "command_validator"},
    {"src": "conn_with_mob_app", "dst": "data_validator"},

    {"src": "ic", "dst": "doors_controller"},
    {"src": "doors_controller", "dst": "ic"},
    {"src": "engine_controller", "dst": "ic"},
    {"src": "ic", "dst": "engine_controller"},
    {"src": "data_validator", "dst": "ic"},
    {"src": "payment_validator", "dst": "ic"},
    {"src": "access_validator", "dst": "ic"},
    {"src": "command_validator", "dst": "ic"},
   
    # Модуль технического состояния
    {"src": "tire_sensons", "dst": "eblocks"},
    {"src": "vehicle_braking", "dst": "eblocks"},
    {"src": "fuel_tank", "dst": "eblocks"},
    {"src": "headlights", "dst": "eblocks"},
    
    # Модуль управления двигателем
    {"src": "engine", "dst": "engine_controller"},
    {"src": "engine_controller", "dst": "eblocks"},
    
    # Модуль навигации
    {"src": "gps", "dst": "navigation_handler"},
    {"src": "navigation_handler", "dst": "eblocks"},
    
    # Модуль управления дверьми
    {"src": "doors_controller", "dst": "locking_device"},
    {"src": "doors_controller", "dst": "eblocks"},
    
    # Модуль валидации
    {"src": "eblocks", "dst": "data_validator"},
    {"src": "command_validator", "dst": "payment_validator"},
    {"src": "command_validator", "dst": "access_validator"},
)


def check_operation(id, details) -> bool:
    """ Проверка возможности совершения обращения. """
    src: str = details.get("source")
    dst: str = details.get("deliver_to")

    if not all((src, dst)):
        return False

    print(f"[info] checking policies for event {id}, {src}->{dst}")

    return {"src": src, "dst": dst} in policies
