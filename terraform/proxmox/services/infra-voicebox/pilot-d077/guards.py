"""Same resource stops as D076; pure function for synthetic boundary tests."""
GIB = 2**30
MIB = 2**20


def predictive_preflight(sample):
    """D079 admission only; existing stop thresholds remain unchanged.

    Observed startup increments4.25–4.48GiB rounded up to4.5GiB, plus0.5GiB
    reserve. Include file/kernel in current, never discount cache speculatively.
    """
    expected = int(4.5 * GIB)
    reserve = int(0.5 * GIB)
    guard = int(14 * GIB)
    projected = sample['ct_current'] + expected + reserve
    return {'initial_ct_bytes': sample['ct_current'], 'expected_increment_bytes': expected,
            'safety_margin_bytes': reserve, 'guard_bytes': guard,
            'projected_with_margin_bytes': projected, 'passed': projected <= guard}


def stop_reason(sample, baseline, now, psi_since):
    if sample["ct_current"] >= 14 * GIB:
        return "CT_MEMORY_14_GIB", psi_since
    if max(sample.get("worker_current", 0), sample.get("rss_bytes", 0)) >= 8.2 * GIB:
        return "WORKER_MEMORY_8_2_GIB", psi_since
    if sample["ct_swap"] >= 1920 * MIB:
        return "CT_SWAP_1920_MIB", psi_since
    if sample["ct_swap"] - baseline["ct_swap"] >= 128 * MIB:
        return "CT_SWAP_GROWTH_128_MIB", psi_since
    if sample["host_available"] < 4 * GIB:
        return "HOST_AVAILABLE_BELOW_4_GIB", psi_since
    if sample["host_oom"] > baseline["host_oom"] or any(
        sample["ct_events"][k] > baseline["ct_events"][k] or sample.get("worker_events", {}).get(k, 0) > 0
        for k in ["oom", "oom_kill"]
    ):
        return "NEW_OOM", psi_since
    bad = sample["ct_psi_full_avg10"] >= 5 or (
        sample["host_psi_full_avg10"] >= 20 and sample["host_available"] < 6 * GIB
    )
    psi_since = (now if psi_since is None else psi_since) if bad else None
    if psi_since is not None and now - psi_since >= 10:
        return "PSI_SUSTAINED_10_SECONDS", psi_since
    return None, psi_since
