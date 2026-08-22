import pytest

from simulation.distribution import histogram, percentile_bands


class TestHistogram:
    def test_bins_and_edges_shape(self) -> None:
        edges, counts = histogram([100.0, 200.0, 300.0, 400.0], num_bins=4)
        assert len(edges) == 5
        assert len(counts) == 4

    def test_counts_sum_to_total(self) -> None:
        finals = [float(i) for i in range(250)]
        _, counts = histogram(finals, num_bins=10)
        assert sum(counts) == 250

    def test_all_same_value_single_bin_range(self) -> None:
        edges, counts = histogram([500.0] * 20, num_bins=5)
        assert sum(counts) == 20
        assert edges[0] < edges[-1]

    @pytest.mark.parametrize("bad", [[], [1.0]])
    def test_edge_cases(self, bad: list[float]) -> None:
        if not bad:
            with pytest.raises(ValueError):
                histogram(bad)
        else:
            edges, counts = histogram(bad, num_bins=3)
            assert sum(counts) == 1

    def test_invalid_num_bins_raises(self) -> None:
        with pytest.raises(ValueError):
            histogram([1.0], num_bins=0)


class TestPercentileBands:
    def test_band_keys_and_lengths(self) -> None:
        trajs = [
            [100.0, 110.0, 120.0],
            [100.0, 90.0, 80.0],
            [100.0, 105.0, 95.0],
            [100.0, 115.0, 130.0],
        ]
        bands = percentile_bands(trajs)
        assert set(bands.keys()) == {"p10", "median", "p90", "min", "max"}
        for series in bands.values():
            assert len(series) == 3

    def test_median_is_per_index_median(self) -> None:
        trajs = [
            [100.0, 90.0],
            [100.0, 100.0],
            [100.0, 110.0],
        ]
        bands = percentile_bands(trajs)
        assert bands["median"][0] == pytest.approx(100.0)
        assert bands["median"][1] == pytest.approx(100.0)

    def test_min_max_envelop_everything(self) -> None:
        trajs = [
            [100.0, 50.0, 200.0],
            [100.0, 150.0, 75.0],
        ]
        bands = percentile_bands(trajs)
        for i in range(3):
            assert bands["min"][i] <= min(t[i] for t in trajs) + 1e-9
            assert bands["max"][i] >= max(t[i] for t in trajs) - 1e-9

    def test_ragged_trajectories_raise(self) -> None:
        with pytest.raises(ValueError):
            percentile_bands([[100.0, 90.0], [100.0]])

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError):
            percentile_bands([])
