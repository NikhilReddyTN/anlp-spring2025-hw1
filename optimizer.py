from typing import Callable, Iterable, Tuple

import torch
from torch.optim import Optimizer


class AdamW(Optimizer):
    def __init__(
            self,
            params: Iterable[torch.nn.parameter.Parameter],
            lr: float = 1e-3,
            betas: Tuple[float, float] = (0.9, 0.999),
            eps: float = 1e-6,
            weight_decay: float = 0.0,
            correct_bias: bool = True,
            max_grad_norm: float = None,
    ):
        if lr < 0.0:
            raise ValueError("Invalid learning rate: {} - should be >= 0.0".format(lr))
        if not 0.0 <= betas[0] < 1.0:
            raise ValueError("Invalid beta parameter: {} - should be in [0.0, 1.0[".format(betas[0]))
        if not 0.0 <= betas[1] < 1.0:
            raise ValueError("Invalid beta parameter: {} - should be in [0.0, 1.0[".format(betas[1]))
        if not 0.0 <= eps:
            raise ValueError("Invalid epsilon value: {} - should be >= 0.0".format(eps))
        defaults = dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay, correct_bias=correct_bias, max_grad_norm=max_grad_norm)
        super().__init__(params, defaults)

    def step(self, closure: Callable = None):
        loss = None
        if closure is not None:
            loss = closure()
        for group in self.param_groups:
            # TODO: Clip gradients if max_grad_norm is set
            if group['max_grad_norm'] is not None:
                torch.nn.utils.clip_grad_norm_(group['params'],group["max_grad_norm"])
                # raise NotImplementedError()  
            for p in group["params"]:
                if p.grad is None:
                    continue
                grad = p.grad.data
                if grad.is_sparse:
                    raise RuntimeError("Adam does not support sparse gradients, please consider SparseAdam instead")
                # raise NotImplementedError()

                # State should be stored in this dictionary
                state = self.state[p]

                # TODO: Access hyperparameters from the `group` dictionary
                alpha = group["lr"]

                # TODO: Update first and second moments of the gradients
                if len(state) == 0:
                    state['m']=0
                    state['v']=0
                    state['step']=0
                state['step']+=1
                beta1,beta2=group["betas"]
                m= beta1*state['m'] + (1-beta1)*grad
                v= beta2*state['v'] + (1-beta2)*(grad*grad)
                state['m']=m
                state['v']=v
                # TODO: Bias correction
                # Please note that we are using the "efficient version" given in
                # https://arxiv.org/abs/1412.6980
                lr=alpha*((1-beta2**state['step'])**0.5) / (1-beta1**state['step'])
                # TODO: Update parameters
                p.data=p.data-lr*(m/(torch.sqrt(v)+group['eps']) + group['weight_decay']*p.data)
                # TODO: Add weight decay after the main gradient-based updates.
                # Please note that the learning rate should be incorporated into this update.
        return loss
