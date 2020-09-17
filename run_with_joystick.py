import copy
from time import sleep

from joystick import Joystick
from motors import RovMovement

arayuz_running = True


def update_from_joystick(rov_movement):
    print("Thrade oluşturuldu")

    # Joystick variables are creating
    joystick_values = {}
    prev_joystick_values = copy.deepcopy(joystick_values)
    Joy_obj = Joystick()
    joystick_values.update(Joy_obj.shared_obj.ret_dict)
    # Joystick variables are created

    global arayuz_running
    while arayuz_running:
        Joy_obj.while_initializer()
        if Joy_obj.joystick_count:
            Joy_obj.for_initializer()
            Joy_obj.joysticks()
            joystick_values = Joy_obj.shared_obj.ret_dict

            pf = joystick_values["power_factor"]
            # print(joystick_values)
            if joystick_values != prev_joystick_values:
                prev_joystick_values = copy.deepcopy(joystick_values)
                print(joystick_values)

                if rov_movement:
                    # Robotik kol hareketi
                    arm_status = int(joystick_values["robotik_kol"])
                    if arm_status == -1:
                        rov_movement.toggle_arm(False)
                    elif arm_status == 1:
                        rov_movement.toggle_arm(True)

                    # XY düzleminde hareket
                    xy_power = joystick_values["xy_plane"]["magnitude"] * pf * 100
                    xy_angle = joystick_values["xy_plane"]["angel"]
                    turn_power = joystick_values["turn_itself"] * pf * 100
                    rov_movement.go_xy_and_turn(xy_power, xy_angle, turn_power)
            else:
                sleep(0.05)

            if rov_movement:
                # Z ekseninde hareket (Eğer z'de değişme yoksa denge için çalışır)
                tilt_degree = joystick_values["tilt_degree"]
                z_power = joystick_values["z_axes"] * pf * 60
                rov_movement.go_z_bidirectional(z_power, tilt_degree=tilt_degree)

        sleep(0.04)
        Joy_obj.clock.tick(50)


if __name__ == "__main__":
    print("__main__")
    rm = RovMovement(
        xy_lf_pin="-1", xy_rf_pin="4", xy_lb_pin="-0", xy_rb_pin="6",
        z_lf_pin="-3", z_rf_pin="2", z_lb_pin="-5", z_rb_pin="7",
        arm_pin=8,
        initialize_motors=True, ssc_control=True
    )
    try:
        update_from_joystick(rm)
    except KeyboardInterrupt:
        print("Keyboard interupt...")
    finally:
        rm.stop()
