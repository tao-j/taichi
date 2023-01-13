import taichi as ti
from tests import test_utils


@test_utils.test(exclude=[ti.vulkan, ti.dx11])
def test_loop_grad():
    x = ti.field(ti.f32)

    n = 16
    m = 8

    ti.root.dense(ti.ij, (n, m)).place(x)
    ti.root.lazy_grad()

    @ti.kernel
    def func():
        for k in range(n):
            for i in range(m - 1):
                x[k, i + 1] = x[k, i] * 2

    for k in range(n):
        x[k, 0] = k
    func()

    for k in range(n):
        x.grad[k, m - 1] = 1
    func.grad()

    for k in range(n):
        # The grad of fields on left-hand sides of assignments (GlobalStoreStmt) need to be reset to zero after the corresponding adjoint assignments.
        # Therefore, only the grad of the element with index 0 at second dimension is preserved here.
        assert x[k, 0] == 2**0 * k
        assert x.grad[k, 0] == 2**(m - 1 - 0)


@test_utils.test(exclude=[ti.vulkan, ti.dx11])
def test_loop_grad_complex():
    return  # This case is not supported yet
    x = ti.field(ti.f32)

    n = 16
    m = 8

    ti.root.dense(ti.ij, (n, m)).place(x)
    ti.root.lazy_grad()

    @ti.kernel
    def func():
        for k in range(n):
            t = k * k
            tt = t * 2
            for i in range(m - 1):
                x[k, i + 1] = x[k, i] * 2 + tt

    for k in range(n):
        x[k, 0] = k
    func()

    for k in range(n):
        x.grad[k, m - 1] = 1
    func.grad()

    for k in range(n):
        for i in range(m):
            assert x[k, i] == i**2 + 2 * k**2
            assert x.grad[k, i] == 2**(m - 1 - i)
