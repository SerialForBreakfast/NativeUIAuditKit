"""P0-C validation regressions; only small generated test pixels, no simulator."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image, PngImagePlugin
import validate_reconstructed_corpus as v
import stage_reconstruction_prefix as prefix

def example(s,root):
    if "$ref" in s:return example(root["definitions"][s["$ref"].split("/")[-1]],root)
    if "const" in s:return s["const"]
    if "enum" in s:return s["enum"][0]
    t=s.get("type");t=t[0] if isinstance(t,list) else t
    if t=="object":return {k:example(s["properties"][k],root) for k in s.get("required",[])}
    if t=="array":return []
    if t=="string":return "09:41" if "pattern" in s else "test"
    if t=="boolean":return False
    return s.get("minimum",0)

class ReconstructionTests(unittest.TestCase):
    def setUp(self):
        base=v.ROOT/".build/debug-output/p0c-validator-tests";base.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=base);self.root=Path(self.tmp.name)
        (self.root/"train").mkdir();self.png=self.root/"train/image.png"
        Image.new("RGB",(20,20),"blue").save(self.png)
        schema=v.read_json(v.SCHEMA);self.ann=example(schema,schema)
        self.ann.update(imageSHA256=v.sha256(self.png))
        self.ann["image"].update(fileName="image.png",pixelWidth=20,pixelHeight=20,scale=2,platform="iOS",deviceName="test")
        self.ann["generatorProfile"].update(templateFamily="LoginForm",seed=1)
        el=example(schema["properties"]["elements"]["items"],schema)
        el.update(id="button",elementType="primaryButton",boundsPoints=dict(x=1,y=2,width=3,height=4),
                  boundsPixels=dict(x=2,y=4,width=6,height=8),boundsVisionNormalized=dict(x=.1,y=.4,width=.3,height=.4))
        self.ann["elements"]=[el]
        self.entry=dict(fileName="train/image.png",split="train",sha256=v.sha256(self.png),templateFamily="LoginForm",generatorSeed=1,pixelScale=2,deviceName="test")
        self.doc={"entries":[self.entry],"classDistribution":{"primaryButton":1}}
        self.save()

    def tearDown(self):self.tmp.cleanup()

    def save(self):
        self.png.with_suffix(".json").write_text(json.dumps(self.ann))
        (self.root/"manifest.json").write_text(json.dumps(self.doc))

    def report(self):return v.validate(self.root,{"train":1,"validation":0,"test":0})

    def test_complete_content_manifest_determinism_and_no_training(self):
        a=self.report();self.assertTrue(a["integrityValid"],a["errors"])
        self.assertEqual(a,self.report());self.assertFalse(a["trainingEligible"])
        self.assertIn("webContent",a["missingClasses"]["train"])
        self.assertEqual(len(a["members"][0]["annotationSHA256"]),64)
        self.assertEqual(a["visibleClassCounts"]["train"],{"primaryButton":1})

    def test_corrupt_decoding_not_just_header_and_hash(self):
        self.png.write_bytes(self.png.read_bytes()[:24]);self.entry["sha256"]=v.sha256(self.png)
        self.ann["imageSHA256"]=self.entry["sha256"];self.save()
        self.assertFalse(self.report()["integrityValid"])

    def test_missing_member_and_hash(self):
        self.entry["sha256"]="0"*64;self.save();self.assertEqual(self.report()["errors"][0]["error"],"image_hash")
        self.png.unlink();self.assertIn("missing_member",self.report()["errors"][0]["error"])

    def test_schema_rejects_insets_unknown_type_version_and_bool(self):
        original=copy.deepcopy(self.ann)
        for mutate in (lambda a:a["image"]["safeAreaInsets"].pop("left"),
                       lambda a:a["elements"][0].update(elementType="tabBarItem"),
                       lambda a:a.update(schemaVersion="1.1"),
                       lambda a:a["image"].update(pixelWidth=True)):
            self.ann=copy.deepcopy(original);mutate(self.ann);self.save();self.assertFalse(self.report()["integrityValid"])

    def test_pair_binding_and_visible_coordinates(self):
        original=copy.deepcopy(self.ann)
        for mutate in (lambda a:a["image"].update(pixelHeight=10),
                       lambda a:a["generatorProfile"].update(seed=999),
                       lambda a:a["elements"][0]["boundsPixels"].update(x=7),
                       lambda a:a["elements"][0]["boundsVisionNormalized"].update(y=.2),
                       lambda a:a["elements"][0]["boundsPoints"].update(x=float("nan"))):
            self.ann=copy.deepcopy(original);mutate(self.ann);self.save();self.assertFalse(self.report()["integrityValid"])

    def test_correct_top_left_clipped_intersection(self):
        e=self.ann["elements"][0];e.update(boundsPoints=dict(x=-1,y=-2,width=4,height=6),boundsPixels=dict(x=-2,y=-4,width=8,height=12),boundsVisionNormalized=dict(x=0,y=.6,width=.3,height=.4),occluded=True,occlusionType="imageBoundary")
        self.save();self.assertTrue(self.report()["integrityValid"])
        e["boundsVisionNormalized"]["width"]=.4;self.save();self.assertFalse(self.report()["integrityValid"])

    def test_invisible_elements_need_explicit_exclusion(self):
        e=self.ann["elements"][0]
        e.update(boundsPoints=dict(x=30,y=30,width=2,height=2),boundsPixels=dict(x=60,y=60,width=4,height=4),boundsVisionNormalized=dict(x=1,y=0,width=0,height=0))
        self.save();self.assertIn("unexcluded_invisible_element",self.report()["errors"][0]["error"])
        e.update(excluded=True,exclusionReason="outsideImage");self.save()
        result=self.report();self.assertTrue(result["integrityValid"])
        self.assertEqual(result["classCounts"]["train"],{"primaryButton":1})
        self.assertEqual(result["visibleClassCounts"]["train"],{})
        self.assertIn("primaryButton",result["missingVisibleClasses"]["train"])

    def test_partition_readiness_does_not_claim_missing_pixels_elsewhere(self):
        result=v.validate(self.root,{"train":2,"validation":0,"test":0})
        self.assertFalse(result["splitReady"]["train"])
        self.assertTrue(result["splitReady"]["test"])

    def test_family_split_path_escape_symlink_and_extras(self):
        for value in ("CardDetail","HardNegative_2","unregistered"):
            self.entry["templateFamily"]=value;self.save();self.assertFalse(self.report()["integrityValid"])
        self.entry["templateFamily"]="LoginForm";self.entry["fileName"]="train/../train/image.png";self.save()
        self.assertIn("unsafe_member",self.report()["errors"][0]["error"])
        self.entry["fileName"]="train/alias.png";(self.root/"train/alias.png").symlink_to(self.png);self.save()
        self.assertIn("symlink_or_escape",self.report()["errors"][0]["error"])

    def test_reencoded_pixel_duplicates_not_just_bytes(self):
        meta=PngImagePlugin.PngInfo();meta.add_text("variant","2")
        other=self.root/"train/second.png"
        with Image.open(self.png) as im:im.save(other,pnginfo=meta)
        entry={**self.entry,"fileName":"train/second.png","sha256":v.sha256(other)}
        ann=copy.deepcopy(self.ann);ann["image"]["fileName"]="second.png";ann["imageSHA256"]=entry["sha256"]
        other.with_suffix(".json").write_text(json.dumps(ann));self.doc["entries"].append(entry);self.doc["classDistribution"]["primaryButton"]=2;self.save()
        result=v.validate(self.root,{"train":2,"validation":0,"test":0})
        self.assertEqual(len(result["decodedDuplicateGroups"]),1)
        self.assertFalse(result["integrityValid"])

    def test_cli_collision_and_unsupported_schema_keyword(self):
        report=self.root/"report.json";report.write_text("preserve")
        with patch("sys.argv",["validator","--corpus",str(self.root),"--report",str(report)]):self.assertEqual(v.main(),2)
        self.assertEqual(report.read_text(),"preserve")
        with self.assertRaisesRegex(ValueError,"unsupported_schema_keyword"):v.check_schema({}, {"oneOf":[]},{})

    def test_rejected_duplicates_are_accounted_without_counting_as_members(self):
        (self.root/"rejected").mkdir()
        other=self.root/"rejected/candidate.png";other.write_bytes(self.png.read_bytes())
        ann=copy.deepcopy(self.ann);ann["image"]["fileName"]=other.name
        other.with_suffix(".json").write_text(json.dumps(ann))
        digest="a"*64
        ledger={"version":1,"accepted":{digest:"train/image.png"},"rejected":[{
            "entry":{**self.entry,"fileName":"rejected/candidate.png"},"pixelSHA256":digest,"duplicateOf":"train/image.png"}]}
        path=self.root/"capture-ledger.json";path.write_text(json.dumps(ledger))
        result=self.report();self.assertTrue(result["integrityValid"],result["errors"])
        self.assertEqual(result["manifestEntries"],1);self.assertEqual(result["rejectedDuplicateCount"],1)
        ledger["rejected"][0]["duplicateOf"]="train/missing.png";path.write_text(json.dumps(ledger))
        self.assertFalse(self.report()["integrityValid"])

    def test_prefix_preserves_complete_members_and_does_not_approve_full_corpus(self):
        ledger={"version":1,"accepted":{"a"*64:"train/image.png","b"*64:"train/unfinished.png"},"rejected":[]}
        (self.root/"capture-ledger.json").write_text(json.dumps(ledger))
        unfinished=self.root/"train/unfinished.png";unfinished.write_bytes(b"retained incomplete evidence")
        before=v.sha256(unfinished)
        with tempfile.TemporaryDirectory(dir=self.root.parent) as work:
            output=Path(work)/"prefix"
            result=prefix.stage(self.root,output)
            self.assertEqual(result["validation"]["manifestEntries"],1)
            self.assertFalse(result["trainingEligible"])
            self.assertEqual(result["fullRequiredCountsUnchanged"],v.EXPECTED)
            self.assertEqual(result["omittedUncommittedAcceptedPaths"],["train/unfinished.png"])
            self.assertFalse((output/"train/unfinished.png").exists())
            self.assertEqual(v.sha256(self.png),v.sha256(output/"train/image.png"))
        self.assertEqual(v.sha256(unfinished),before)

    def test_prefix_rejects_bad_members_and_output_collision(self):
        with tempfile.TemporaryDirectory(dir=self.root.parent) as work:
            output=Path(work)/"prefix"
            self.entry["sha256"]="0"*64;self.save()
            with self.assertRaisesRegex(ValueError,"source_not_a_valid_manifested_prefix"):
                prefix.stage(self.root,output)
            self.assertFalse(output.exists())
            output.mkdir();sentinel=output/"keep";sentinel.write_text("preserve")
            with self.assertRaisesRegex(ValueError,"output_boundary_or_collision"):
                prefix.stage(self.root,output)
            self.assertEqual(sentinel.read_text(),"preserve")

if __name__=="__main__":unittest.main()
