"""Synthetic plumbing checks against installed code, without model weights/forward."""
from pathlib import Path
from unittest.mock import patch


def chunk_contract():
    import torch
    import runtime
    _, cls = runtime.decoder_classes()

    class MarkerDecoder:
        total_upsample = 1

        def __init__(self):
            self.inputs = []

        def __call__(self, codes):
            self.inputs.append(codes[0, 0].tolist())
            # Token markers, not audio and not a real model forward.
            return codes[:, :1, :]

    codes = torch.arange(701).reshape(1, 1, -1).repeat(1, 16, 1)
    results = {}
    for size in [300, 120]:
        fake = MarkerDecoder()
        markers = cls.chunked_decode(fake, codes, chunk_size=size, left_context_size=25)
        if not torch.equal(markers, codes[:, :1, :]):
            raise ValueError("Chunk ordering/context removal changed")
        if fake.inputs[1][0] != size - 25:
            raise ValueError("Incorrect left overlap")
        results[str(size)] = {"chunks": len(fake.inputs), "markers_preserved": True, "context": 25}
    return {"structural_only_not_acoustic_equivalence": True, "results": results}


def decoder_loader_contract():
    """Exercise meta/assign and CPU buffers using one synthetic scalar parameter."""
    import torch
    import runtime

    class TinyDecoder(torch.nn.Module):
        def __init__(self, config):
            super().__init__()
            self.weight = torch.nn.Parameter(torch.empty(1))
            self.register_buffer("rotary", torch.ones(1), persistent=False)

    class FakeSafeFile:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def keys(self):
            return ["encoder.forbidden", "decoder.weight"]

        def get_tensor(self, key):
            if key != "decoder.weight":
                raise ValueError("Attempt to load encoder")
            return torch.tensor([42.0])

    with patch.object(runtime, "decoder_classes", return_value=(None, TinyDecoder)), \
         patch.object(runtime, "decoder_config", return_value=None), \
         patch("safetensors.safe_open", return_value=FakeSafeFile()):
        tiny = runtime.load_decoder_only(Path("/nonexistent-synthetic-codec"))
    if tiny.weight.item() != 42 or tiny.rotary.is_meta or tiny.weight.device.type != "cpu":
        raise ValueError("Decoder-only state assignment/CPU buffers failed")
    return {"synthetic_weight_only": True, "encoder_never_read": True, "nonpersistent_buffers_cpu": True,
            "real_model_weights_loaded": False}
