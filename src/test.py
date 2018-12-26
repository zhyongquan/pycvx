from pycvx import cvxinfo

cvx = cvxinfo()
cvx.read("../data/DEMO.CSV")
# find functions:2, calibrations:5, axises:0

print(cvx.calibrations["DEMO_CURVE"])
# name=DEMO_CURVE, description=
# line_start=30, line_end=33
# type=CURVE, unit=
# value
# [0.30078125, 0.3984375, 0.5, 0.59765625, 0.69921875, 0.80078125, 0.8984375]
# x
# name=, description=
# line_start=38, line_end=39
# type=X_AXIS_PTS, unit=revs
# value
# [120.0, 200.0, 320.0, 400.0, 520.0, 600.0, 720.0]

cvx.calibrations["DEMO_CURVE"].show()
