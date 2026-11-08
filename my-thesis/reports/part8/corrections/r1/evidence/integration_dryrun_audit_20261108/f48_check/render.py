import sys
from pathlib import Path
R = Path("/home/user/academia7/my-thesis"); sys.path.insert(0, str(R / "colab"))
import r1_render_guard as rg; rg.pin_default_rc()
import r1_tierb as tb; tb.use_scientific_code(Path(sys.argv[1]))
import r1_integration_dependents as dep
from thesis.core.config import load_config
from thesis.core.paths import CONFIG_DIR
config = load_config(names=("baseline", "series_catalog", "thresholds"), config_dir=CONFIG_DIR)
tab = Path(sys.argv[2])
print(dep.render_f48(tab, "UNRATE", Path(sys.argv[3]), config))
for r in dep.f48_inputs(tab, "UNRATE"): print(r)
