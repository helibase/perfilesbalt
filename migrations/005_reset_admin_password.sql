UPDATE admin_users 
SET password_hash = 'pbkdf2:sha256:260000$Ry3Ld5Ue3Ld5Ue3Ld5Ue3Ld5Ue$8a7b9c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w' 
WHERE username = 'admin';