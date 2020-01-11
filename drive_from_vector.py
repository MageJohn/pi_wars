piv_limit = 0.20

def drive_from_vector(x,y):
    left_motor_premix = 0.0
    right_motor_premix = 0.0
    pivot_speed = 0.0
    pivot_scale = 0.0

    if (y >= 0):
        if(x >= 0):
            left_motor_premix = 1.0
            right_motor_premix = 1.0 - x
        else:
            left_motor_premix = 1.0 + x
            right_motor_premix = 1.0
    else:
        if (x >= 0):
            left_motor_premix = 1.0 - x
            right_motor_premix = 1.0
        else:
            left_motor_premix = 1.0
            right_motor_premix = 1.0 + x

    left_motor_premix *= (y/1.0)
    right_motor_premix *= (y/1.0)

    pivot_speed = x

    if (abs(y)>piv_limit):
        pivot_scale = 0.0
    else:
        pivot_scale = 1.0 - (abs(y)/piv_limit)

    left_motor_mix = (1.0 - pivot_scale)*left_motor_premix + pivot_scale*pivot_speed
    right_motor_mix = (1.0 - pivot_scale)*right_motor_premix + pivot_scale*-pivot_speed

    return((left_motor_mix,right_motor_mix))
    
            
        
        
    
    
