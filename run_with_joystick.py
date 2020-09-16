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
                    xy_power = joystick_values["xy_plane"]["magnitude"] * 100
                    xy_angle = joystick_values["xy_plane"]["angel"]
                    turn_power = joystick_values["turn_itself"] * 100
                    rov_movement.go_xy_and_turn(xy_power, xy_angle, turn_power)

            else:
                sleep(0.05)

            if rov_movement:
                # Z ekseninde hareket (Eğer z'de değişme yoksa denge için çalışır)
                if joystick_values.get("dik_dur"):
                    target_x = 90
                elif joystick_values.get("asagi_bak"):
                    target_x = -30
                else:
                    target_x = 0
                z_power = int(joystick_values["z_axes"] * 30)
                rov_movement.go_z_bidirectional(z_power, target_x=target_x)

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
