from .tensor import Device, Function, register
from functools import lru_cache

@lru_cache
def compile_wrapper(ane, dat):
  return ane.compile(dat)

def roundup(x, v):
  return x + (v-x)%v

@lru_cache
def compile_relu(ane, sz):
  dat = list(open("ane/ops/relu.hwx", "rb").read())
  # TODO: make this all nice and once
  # number of engines? (max 0x100)
  dat = ane.fill(dat, [0x1ec, 0x1f0, 0x1f4, 0x1f8], "I", max(0x100, roundup(sz*2, 0x10)))
  stride = roundup(sz*2, 0x40)
  dat = ane.filln(dat, {
    "InputWidth": sz, "OutputWidth": sz,
    "InputRowStride": stride, "InputPlaneStride": stride, "InputDepthStride": stride,
    "OutputRowStride": stride, "OutputPlaneStride": stride, "OutputDepthStride": stride})
  return compile_wrapper(ane, bytes(dat))

class ReLU(Function):
  @staticmethod
  def forward(ctx, input):
    ret = ctx.ane.tensor(input.shape)
    ctx.ane.run(compile_relu(ctx.ane, input.sz), input, ret)
    return ret
register('relu', ReLU, device=Device.ANE)
