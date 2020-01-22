piv_limit = 0.20


def drive_from_vector(x, y):
    left_premix = 0.0
    right_premix = 0.0
    pivot_speed = 0.0
    pivot_scale = 0.0

    if y >= 0:
        if x >= 0:
            left_premix = 1.0
            right_premix = 1.0 - x
        else:
            left_premix = 1.0 + x
            right_premix = 1.0
    else:
        if x >= 0:
            left_premix = 1.0 - x
            right_premix = 1.0
        else:
            left_premix = 1.0
            right_premix = 1.0 + x

    left_premix *= y / 1.0
    right_premix *= y / 1.0

    pivot_speed = x

    if abs(y) > piv_limit:
        pivot_scale = 0.0
    else:
        pivot_scale = 1.0 - (abs(y) / piv_limit)

    left_mix = (1.0 - pivot_scale) * left_premix + pivot_scale * pivot_speed
    right_mix = (1.0 - pivot_scale) * right_premix + pivot_scale * -pivot_speed

    return (left_mix, right_mix)
