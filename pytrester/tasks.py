from tqdm import tqdm
from coverage import Coverage
from redis import from_url, Redis
from rq.decorators import job
from .tools import get_modules, futurize, fix_patterns, run_destral, update_module

try:
    REDIS_CONN = from_url('REDIS_URL')
except ValueError:
    REDIS_CONN = Redis()


def enqueue_modules(modules=None, only_failed=True):
    modules_values = get_modules()
    if not modules:
        modules = [x[0] for x in modules_values]
    if only_failed:
        modules = [x[0] for x in modules_values if x[1] == '0' and x[0] in modules[:]]

    for module in tqdm(modules):
        test_py3.delay(module)


@job('py3', connection=REDIS_CONN)
def test_py3(module):
    futurize(module)
    fix_patterns(module)
    result, elapsed = run_destral(module)
    py3 = int(result == 0)
    cov = Coverage()
    try:
        cov.load()
        cov_per = cov.report()
        cov.erase()
    except Exception:
        cov_per = 0

    update_module(module, py3, coverage=cov_per, test_time=elapsed)
