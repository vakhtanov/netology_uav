# модуль drone_commands.py реализующий команды

from pymavlink import mavutil

# команда включения моторов (arm)
def arm(master):
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        1, 0, 0, 0, 0, 0, 0)

# команда взлета (takeoff)
def takeoff(master, alt):
    mavutil.mavfile.set_mode(master, 4, 0, 0)

    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
        0,
        0, 0, 0, 0, 0, 0, alt)

# команда посадки (land)
def land(master):
    mavutil.mavfile.set_mode(master, 9, 0, 0)