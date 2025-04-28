import fimex
import os
import datetime


def interpolate_atm_forcing(atm_file):
    atm_cfg = 'fimex/atm.cfg'
    cfg = fimex.FimexConfig()
    cfg.read_cfg(atm_cfg)
    cfg.addattr('input', 'file', atm_file)
    cfg.addattr('output', 'file', atm_file.replace('.nc', '_NK800.nc'))
    cfg.addattr("extract", "reduceTime.start", datetime.datetime(2022,1,1))
    cfg.addattr("extract", "reduceTime.end", datetime.datetime(2022,1,2))
    cfg.run_fimex(fimex_kwargs={'-n': str(8)}, debug=True)

if __name__ == '__main__':
    interpolate_atm_forcing('/lustre/storeB/project/fou/hi/foccus/datasets/norkyst-v3-hindcast/forcing/atm/arome_meps_2_5km_2022010100-2023010100_ext_newTair.nc')