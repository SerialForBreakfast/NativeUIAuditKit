"""Hash-bound bulk confirmation for the local diagnostic review editor."""
import copy
import os

import human_annotation_review as h


def prepare_document(frame, doc):
    """Propose binary checkbox defaults, confirmation and IDs for explicit consent."""
    proposed = copy.deepcopy(doc)
    h.bool_flags(proposed.get("flags"), h.FRAME_FLAGS)
    shapes = proposed["shapes"]
    h.require(isinstance(shapes, list) and 0 < len(shapes) <= 100, "no_controls_or_control_limit")
    ids = [s.get("group_id") for s in shapes if s.get("group_id") is not None]
    h.require(all(type(i) is int and 0 < i <= 100000 for i in ids)
              and len(ids) == len(set(ids)), "invalid_or_duplicate_control_id")
    reserved = set(range(1, len(frame["proposals"])+1))
    h.require(reserved <= set(ids), "missing_original_control_id_do_not_guess")
    used = set(ids) | reserved
    available = iter(i for i in range(1, 100001) if i not in used)
    assigned = []
    for n, shape in enumerate(shapes, 1):
        h.bool_flags(shape.get("flags"), h.SHAPE_FLAGS)
        # Match the binary editor: unchecked Focused means unfocused. Preserve
        # true/true conflicts for adjudication; preview never writes the source.
        if not shape['flags']['focused'] and not shape['flags']['unfocused']:
            shape['flags']['unfocused'] = True
        if shape.get("group_id") is None:
            shape["group_id"] = next(available)
            assigned.append(dict(box=n, groupID=shape["group_id"]))
        if not shape["flags"]["rejected"]:
            shape["flags"]["confirmed"] = True
    proposed["flags"] = {k: True for k in h.FRAME_FLAGS}
    return proposed, assigned


def preview(batch_path, frame_ids=None):
    """Read-only whole-batch preview; blocked frames are never proposed for writes."""
    batch_path = h.local(batch_path)
    batch_ref = h.ref(batch_path)
    batch = h.validate_batch(batch_path)
    scope = list(frame_ids) if frame_ids is not None else [f['id'] for f in batch['frames']]
    h.require(len(scope) == len(set(scope)) and set(scope) <= {f['id'] for f in batch['frames']},
              'invalid_review_scope')
    editor = batch_path.parent / "editor"
    expected = {f["editorStem"]+suffix for f in batch["frames"] if f["disposition"] == "imported"
                for suffix in (".png", ".json")}
    h.require({p.name for p in editor.iterdir()} == expected, "editor_membership_mismatch")
    rows = []
    for frame in batch["frames"]:
        row = dict(id=frame["id"], screen=frame["screen"], ready=False, issues=[], assignedIDs=[], boxes=0)
        rows.append(row)
        if frame["disposition"] != "imported":
            row["issues"] = list(frame["reasons"]) or ["frame_not_imported"]
            continue
        path = editor / (frame["editorStem"]+".json")
        row["source"] = h.ref(path)
        row["imagePath"] = str(path.with_suffix(".png"))
        if frame['id'] not in scope:
            row['issues'] = ['outside_selected_review_batch']
            continue
        try:
            doc = h.read(path)
            proposed, assigned = prepare_document(frame, doc)
            row["boxes"] = len(proposed["shapes"])
            controls = h.parse_editor_document(batch, frame, path, proposed)
            row["issues"] = [f"Box {c['groupID']}: {', '.join(c['reasons'])}"
                             for c in controls if c["disposition"] == "blocked"]
            if not row["issues"]:
                row.update(ready=True, document=proposed, assignedIDs=assigned)
        except (ValueError, OSError, KeyError, TypeError) as error:
            row["issues"] = [str(error)]
        h.require(h.ref(path) == row["source"], "annotations_changed_during_preview")
    h.require(h.ref(batch_path) == batch_ref, "batch_changed")
    return dict(version="human-review-finish-preview-v1", **h.FLAGS,
                batch=batch_ref, selectedFrames=scope, frames=rows)


def apply_preview(plan, output, *, reviewer, attested, reviewer_kind="human", complete_frames=False):
    """Explicit consent, backups and stale-state checks precede all annotation writes."""
    h.require(attested is True, "explicit_bulk_attestation_required")
    h.text(reviewer)
    h.require(bool(reviewer.strip()), "reviewer_required")
    h.require(reviewer_kind in ("human", "software-test"), "invalid_reviewer_kind")
    h.require(type(complete_frames) is bool and (not complete_frames or reviewer_kind == 'human'),
              'completeness_requires_human')
    batch_path = h.checked(h.ROOT, plan["batch"])
    current = preview(batch_path, plan.get('selectedFrames'))
    h.require(h.digest(current) == h.digest(plan), "review_preview_stale_reopen_finish_review")
    ready = [r for r in current["frames"] if r["ready"]]
    h.require(bool(ready), "no_ready_frames")
    if complete_frames:
        h.require(all(any(not s['flags']['rejected'] for s in row['document']['shapes']) for row in ready),
                  'completeness_requires_reviewed_controls')
    output = h.fresh(output)
    output.mkdir(parents=True)
    backup = output / "before"
    staged = output / "staged"
    backup.mkdir()
    staged.mkdir()
    h.write(output / "preview.json", current, sealed=True)
    applied = []
    try:
        # Preserve every JSON, including pending frames, before the first update.
        for row in current["frames"]:
            if "source" in row:
                source = h.checked(h.ROOT, row["source"])
                h.copy_ref(row["source"], backup / source.name, 8*1024*1024)
        for row in ready:
            source = h.checked(h.ROOT, row["source"])
            h.write(staged / source.name, row["document"])
        h.require(h.digest(preview(batch_path, plan.get('selectedFrames'))) == h.digest(plan), "review_preview_stale_before_write")
        expected = {r["source"]["path"]: r["source"]["sha256"] for r in current["frames"] if "source" in r}
        for row in ready:
            source = h.checked(h.ROOT, row["source"])
            replacement = staged / source.name
            new_hash = h.sha(replacement)
            os.replace(replacement, source)
            applied.append(row["id"])
            expected[row["source"]["path"]] = new_hash
        for path, digest in expected.items():
            h.checked(h.ROOT, dict(path=path, sha256=digest))
        revision = h.finish(batch_path, output / "revision", reviewer=reviewer.strip(),
                            reference="Finish review explicit bulk attestation; " + str(output.relative_to(h.ROOT)),
                            reviewer_kind=reviewer_kind, confirm_batch=True)
        receipt = dict(version="human-review-finish-receipt-v1", **h.FLAGS, appliedFrames=applied,
                       reviewer=reviewer.strip(), reviewerKind=reviewer_kind,
                       attested=True, revision=h.ref(output / "revision/revision.json"),
                       frameCounts=revision["frameCounts"], controlCounts=revision["controlCounts"])
        if complete_frames:
            from human_regression_review import attest_completeness
            attest_completeness(output / 'revision/revision.json', applied, output / 'completeness.json')
            receipt['completeness'] = h.ref(output / 'completeness.json')
        h.write(output / "receipt.json", receipt, sealed=True)
        return receipt
    except Exception as error:
        # Never overwrite concurrent edits during rollback. Exact before files and
        # applied membership allow explicit recovery if storage or finish fails.
        h.write(output / "failure.json", dict(error=str(error), appliedFrames=applied,
                                              recovery=str(backup), complete=False), sealed=True)
        raise
