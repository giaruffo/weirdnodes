# import config.py

import config

# access EXPERIMENT_TYPE and run the corresponding python file
if config.EXPERIMENT_TYPE == "ER_VOLCANOES_AND_BLACKHOLES":
    import run_ER_volcanoes_blackholes
    run_ER_volcanoes_blackholes.run()
elif config.EXPERIMENT_TYPE == "ER_GHOSTS_MUSHROOMS":
    import run_ER_ghosts_mushrooms
    run_ER_ghosts_mushrooms.run()
elif config.EXPERIMENT_TYPE == "ER_INTERMEDIARIES":
    import run_ER_intermediaries
    run_ER_intermediaries.run()
elif config.EXPERIMENT_TYPE == "ER_MIXED_ANOMALIES":
    import run_ER_mixed_anomalies
    run_ER_mixed_anomalies.run()
else:
    print("Invalid EXPERIMENT_TYPE")
