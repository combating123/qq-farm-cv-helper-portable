import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "portable" / "hook.py"
SLOT_IDS = tuple(f"L{index:02d}" for index in range(1, 25))

# Index order is the existing canonical isometric lattice order used by the
# empty-land matcher, not row-major screen order.
CANONICAL_24 = (
    (202, 424),
    (172, 439), (231, 439),
    (143, 454), (202, 454), (260, 454),
    (114, 469), (172, 469), (231, 469), (289, 466),
    (85, 484), (143, 484), (201, 481), (260, 484),
    (55, 499), (114, 499), (172, 499), (230, 496),
    (85, 514), (143, 514), (202, 514),
    (114, 529), (173, 529),
    (144, 544),
)


def load_function(name):
    source = HOOK.read_text(encoding="utf-8-sig")
    tree = ast.parse(source, filename=str(HOOK))
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if not nodes:
        raise AssertionError(f"hook.py is missing: {name}")
    module = ast.Module(body=nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {"__file__": str(HOOK)}
    exec(compile(module, str(HOOK), "exec"), namespace)
    return namespace[name]


def point_for(slot_index, *, shift=(17, -11), width=428, height=800):
    base_x, base_y = CANONICAL_24[slot_index - 1]
    normalized_x = base_x + shift[0]
    normalized_y = base_y + shift[1]
    return (
        round(normalized_x * width / 428.0, 3),
        round(normalized_y * height / 800.0, 3),
    )


def candidates_for(indices, *, state, shift=(17, -11), width=428, height=800):
    return [
        {
            "center": point_for(
                index, shift=shift, width=width, height=height
            ),
            "state": state,
            "confidence": 0.99,
        }
        for index in indices
    ]


class V374PartialLatticeMappingTests(unittest.TestCase):
    def test_partial_twelve_empty_plus_twelve_occupied_maps_all_fixed_slots(self):
        fit = load_function("_qqfarm_fit_24_plot_lattice_from_candidates")
        result = fit(
            candidates_for(range(13, 25), state="empty"),
            frame_shape=(800, 428, 3),
            occupied_candidates=candidates_for(
                range(1, 13), state="occupied-2x2"
            ),
        )

        self.assertEqual("aligned", result["status"])
        self.assertEqual("matched-all-24", result["reason"])
        self.assertEqual({"x": 17, "y": -11}, result["transform"])
        self.assertEqual(SLOT_IDS[12:], tuple(result["empty_slots"]))
        self.assertEqual(SLOT_IDS[:12], tuple(result["occupied_slots"]))
        self.assertEqual(24, result["matched_count"])
        self.assertEqual(0, result["unknown_count"])
        self.assertEqual(
            "occupied-2x2", result["slot_observations"]["L01"]["state"]
        )
        self.assertEqual(
            "empty", result["slot_observations"]["L24"]["state"]
        )
        self.assertEqual(
            (219, 413), result["slot_centers"]["L01"]
        )

    def test_normalized_resize_keeps_slot_ids_transform_and_board_signature(self):
        fit = load_function("_qqfarm_fit_24_plot_lattice_from_candidates")
        native = fit(
            candidates_for(range(13, 25), state="empty"),
            frame_shape=(800, 428, 3),
            occupied_candidates=candidates_for(
                range(1, 13), state="occupied-2x2"
            ),
        )
        resized = fit(
            candidates_for(
                range(13, 25), state="empty", width=447, height=834
            ),
            frame_shape=(834, 447, 3),
            occupied_candidates=candidates_for(
                range(1, 13), state="occupied-2x2", width=447, height=834
            ),
        )

        self.assertEqual("aligned", native["status"])
        self.assertEqual("aligned", resized["status"])
        self.assertEqual(native["transform"], resized["transform"])
        self.assertEqual(native["board_signature"], resized["board_signature"])
        self.assertEqual(native["empty_slots"], resized["empty_slots"])
        self.assertEqual(native["occupied_slots"], resized["occupied_slots"])
        self.assertEqual((229, 430), resized["slot_centers"]["L01"])

    def test_a_repeated_single_quad_is_ambiguous_without_an_accepted_previous_transform(self):
        fit = load_function("_qqfarm_fit_24_plot_lattice_from_candidates")
        quad_indices = (1, 3, 2, 5)
        ambiguous = fit(
            candidates_for(quad_indices, state="empty"),
            frame_shape=(800, 428, 3),
        )
        recovered = fit(
            candidates_for(quad_indices, state="empty"),
            frame_shape=(800, 428, 3),
            previous_transform={"x": 17, "y": -11},
        )

        self.assertEqual("unknown", ambiguous["status"])
        self.assertEqual("ambiguous-transform", ambiguous["reason"])
        self.assertEqual("aligned", recovered["status"])
        self.assertEqual({"x": 17, "y": -11}, recovered["transform"])
        self.assertEqual(("L01", "L02", "L03", "L05"), recovered["empty_slots"])

    def test_stale_previous_transform_refits_an_unambiguous_current_board(self):
        """A camera shift must discard a stale lattice translation and re-fit."""
        fit = load_function("_qqfarm_fit_24_plot_lattice_from_candidates")
        result = fit(
            candidates_for(
                range(1, 25),
                state="occupied-1x1",
                shift=(51, 31),
                width=671,
                height=1251,
            ),
            frame_shape=(1251, 671, 3),
            previous_transform={"x": 130, "y": 43},
        )

        self.assertEqual("aligned", result["status"])
        self.assertEqual({"x": 51, "y": 31}, result["transform"])
        self.assertEqual(24, result["matched_count"])
        self.assertEqual(0, result["unknown_count"])


    def test_insufficient_partial_evidence_never_guesses_occupied_slots(self):
        fit = load_function("_qqfarm_fit_24_plot_lattice_from_candidates")
        result = fit(
            candidates_for((1, 3), state="empty"),
            frame_shape=(800, 428, 3),
        )

        self.assertEqual("unknown", result["status"])
        self.assertEqual("insufficient-evidence", result["reason"])
        self.assertEqual(24, result["unknown_count"])
        self.assertEqual((), tuple(result["empty_slots"]))
        self.assertEqual((), tuple(result["occupied_slots"]))


if __name__ == "__main__":
    unittest.main()
