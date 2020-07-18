from joystick import Joystick
from motors import RovMovement

if __name__ == '__main__':
    rov_movement = RovMovement(xy_lf_pin=0, xy_rf_pin=0, xy_lb_pin=0, xy_rb_pin=0,
                               z_lf_pin=0, z_rf_pin=0, z_lb_pin=0, z_rb_pin=0)
    joystick = Joystick()
    try:
        while True:
            z_guc = None
            if z_guc < 0:
                rov_movement.go_down(100)
            elif z_guc > 0:
                rov_movement.go_up(100)

            z_ekseninde_donme_gucu = None
            if z_ekseninde_donme_gucu < 0:
                rov_movement.turn_left(100)
            elif z_ekseninde_donme_gucu > 0:
                rov_movement.turn_right(100)

            xy_aci, xy_guc = None, None
            rov_movement.go_xy(xy_guc, xy_aci)

            robotik_kol = None
            if robotik_kol == 1:
                rov_movement.open_arm()
            elif robotik_kol == -1:
                rov_movement.close_arm()

    except KeyboardInterrupt:
        print("Program kapatılıyor (Ctrl+C)")
    finally:
        rov_movement.close()
