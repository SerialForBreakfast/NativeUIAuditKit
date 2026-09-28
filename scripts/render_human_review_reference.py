"""Render an offline, schematic label reference; no models or source image edits."""
import argparse
import html
from pathlib import Path

from human_annotation_review import ROOT, taxonomy, fresh


def rect(x, y, w, h, fill="#e7edf5", radius=7, stroke="none"):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'


def text(x, y, value, size=13, fill="#263448"):
    return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{fill}">{html.escape(value)}</text>'


def line(x, y, x2, y2, color="#8090a5", width=2):
    return f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>'


def circle(x, y, r, fill="#75859b"):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>'


# Exact v1.0 names offered by the current editor, not a taxonomy extension.
# name -> human description, box convention, schematic, bbox (in illustration units).
SPECS = {
 "collectionItem": ("App tile / shelf card", "Tile surface only; caption below is separate. Not imageView merely because it contains art.", rect(42,12,136,70,"#416c96")+text(72,54,"APP TILE",16,"white")+text(80,105,"Photos"), (42,12,136,70)),
 "listRow": ("Settings / list row", "Entire row: title, value and chevron inside its surface.",rect(12,30,196,46)+text(23,58,"General")+text(190,59,">"), (12,30,196,46)),
 "primaryButton": ("Main action button", "Whole button including internal text. Primary describes its role, not which button is focused.",rect(24,30,172,48,"#245bc1")+text(72,60,"Continue",15,"white"), (24,30,172,48)),
 "secondaryButton": ("Alternative action", "Whole alternative/outline button; focus highlight does not change its class.",rect(24,30,172,48,"white",7,"#627287")+text(81,60,"Trailer",15), (24,30,172,48)),
 "label": ("Standalone text", "Visible text region; external tile captions are separate from the tile. Skip as a target in focus-only review.",text(54,63,"Recently added",16), (53,47,122,22)),
 "imageView": ("Noninteractive artwork", "Image/media surface. Use collectionItem for the selectable tile containing it, not a duplicate focus target.",rect(42,12,136,82,"#bfd1df")+circle(148,32,9,"#faf6d4")+'<path d="M42 94 L80 47 L113 82 L139 57 L178 94" fill="#597e8e"/>', (42,12,136,82)),
 "toggle": ("On/off switch", "Switch track and thumb, not an outside caption. State is not a different class.",rect(76,31,68,38,"#26836b",19)+circle(125,50,15,"white"), (76,31,68,38)),
 "tabBar": ("Tab navigation strip", "Whole top tvOS or bottom iOS strip; there is no tabBarItem class in this 41-label editor.",rect(10,30,200,45)+text(23,58,"Home   Browse   Library",14), (10,30,200,45)),
 "homeIndicator": ("Phone/tablet gesture pill", "Thin bottom gesture bar. NEVER a Home-screen app icon; not a tvOS focus target.",rect(64,68,92,6,"#253344",3), (64,68,92,6)),
 "destructiveButton": ("Destructive action", "Whole Delete/Remove-style control. Do not classify by red color alone.",rect(24,30,172,48,"#b92e40")+text(84,60,"Delete",15,"white"), (24,30,172,48)),
 "cancelAction": ("Cancel / dismiss action", "Cancel control or its tappable text extent, not the whole dialog.",text(81,61,"Cancel",17,"#245bc1"), (78,41,65,27)),
 "textField": ("Text input", "Whole input field; an outside field title is separate.",rect(18,28,184,46,"white",7,"#a2afbd")+text(31,57,"Name")+line(85,39,85,64), (18,28,184,46)),
 "secureField": ("Password input", "Whole obscured-text input. A row of dots alone may be ambiguous without context.",rect(18,28,184,46,"white",7,"#a2afbd")+''.join(circle(39+i*14,52,4) for i in range(6)), (18,28,184,46)),
 "searchField": ("Search input", "Whole search field, including its search affordance and inline text.",rect(18,28,184,46)+circle(39,50,8,"none")+'<circle cx="39" cy="50" r="7" fill="none" stroke="#526278" stroke-width="2"/>'+line(44,55,51,62)+text(65,57,"Search"), (18,28,184,46)),
 "slider": ("Continuous slider", "Entire track and knob, not just the movable knob.",rect(25,51,170,5,"#adb9c7",2)+rect(25,51,90,5,"#245bc1",2)+circle(115,53,11,"#245bc1"), (25,42,170,22)),
 "segmentedControl": ("Segmented choices", "Whole joined group of mutually exclusive segments.",rect(16,29,188,45)+rect(19,32,88,39,"white")+text(37,57,"Movies")+text(131,57,"Shows"), (16,29,188,45)),
 "picker": ("Wheel/date picker", "Whole visible picker, not just the centered value.",rect(47,9,126,96,"#f0f3f8")+rect(47,42,126,30)+text(81,32,"Monday")+text(81,62,"Tuesday")+text(81,92,"Wednesday"), (47,9,126,96)),
 "stepperControl": ("Minus / plus stepper", "Both buttons as one stepper control.",rect(59,30,102,44)+line(110,32,110,72)+text(78,59,"−",23)+text(125,59,"+",23), (59,30,102,44)),
 "menuButton": ("Pull-down menu trigger", "Trigger button only, not its opened menu. Usually iOS/iPadOS/macOS.",rect(43,30,134,45)+text(59,57,"Options   v"), (43,30,134,45)),
 "colorWell": ("Color chooser", "Color-selection control, not any colored swatch used as decoration.",circle(110,55,26,"#8a60ad"), (84,29,52,52)),
 "link": ("Inline text link", "Linked text only, not the whole paragraph containing it.",text(15,42,"Read our")+text(15,65,"privacy policy",15,"#245bc1")+line(15,68,108,68,"#245bc1",1), (14,48,98,22)),
 "mapView": ("Embedded map", "Whole map viewport; keep separate controls separate when doing full detection labels.",rect(20,12,180,86,"#deeadc")+line(20,68,190,25,"white",8)+line(69,12,119,98,"white",8)+circle(131,54,9,"#245bc1"), (20,12,180,86)),
 "activityIndicator": ("Loading spinner", "Spinner's visible extent. It is not a focus target.",'<circle cx="110" cy="53" r="21" fill="none" stroke="#bdc7d2" stroke-width="5"/><path d="M110 32 A21 21 0 0 1 131 53" fill="none" stroke="#245bc1" stroke-width="5"/>', (87,30,46,46)),
 "progressView": ("Progress bar", "Entire progress track, not only the filled portion.",rect(24,48,172,9,"#d7dfea",4)+rect(24,48,100,9,"#245bc1",4), (24,48,172,9)),
 "pageControl": ("Page / carousel dots", "Whole dot group; not one box per dot.",''.join(circle(77+i*22,54,5,"#245bc1" if i==1 else "#bcc6d3") for i in range(4)), (72,49,76,10)),
 "scrollIndicator": ("Scroll position bar", "Visible scroll thumb, not the whole page/content region.",rect(185,16,5,76,"#eef1f6",2)+rect(185,35,5,32,"#75859b",2), (185,35,5,32)),
 "refreshControl": ("Pull-to-refresh control", "Spinner in pull-to-refresh context. If context is missing, flag instead of guessing.",text(69,24,"Pull to refresh",12)+'<circle cx="110" cy="52" r="14" fill="none" stroke="#667c98" stroke-width="4"/>'+line(25,90,195,90,"#d9e0e9"), (94,36,32,32)),
 "statusBar": ("Time / battery strip", "Whole status strip, not each indicator separately.",rect(10,30,200,25,"#e7edf5",0)+text(21,47,"9:41")+text(155,47,"Wi-Fi  ▰",11), (10,30,200,25)),
 "navigationBar": ("In-app title / back bar", "Whole navigation strip; not a button just because it includes Back.",rect(10,29,200,44)+text(23,56,"< Back")+text(104,56,"Settings",15), (10,29,200,44)),
 "toolbar": ("Action toolbar", "Whole action strip; distinguish actions from switching app sections in tabBar.",rect(10,29,200,44)+text(25,57,"Edit     Share     More",14), (10,29,200,44)),
 "sidebar": ("Side navigation pane", "Whole side pane. Individual row targets are separate annotations in a full pass.",rect(20,7,79,98)+text(27,30,"Library")+text(27,54,"Albums")+text(27,78,"Shared")+rect(110,7,90,98,"#f2f5f9"), (20,7,79,98)),
 "dynamicIsland": ("iPhone top activity pill", "Top system island area; not the bottom homeIndicator and not tvOS.",rect(66,19,88,26,"#263448",13)+circle(138,32,5,"#697e99"), (66,19,88,26)),
 "alert": ("Alert dialog", "Whole alert container. Its buttons can be separate focus targets.",rect(35,10,150,90,"#e6edf6")+text(72,34,"Allow access?")+line(35,60,185,60)+text(51,82,"Cancel     Allow"), (35,10,150,90)),
 "actionSheet": ("Action choices sheet", "Action-list container, often bottom anchored; includes its own visible surface.",rect(31,28,158,73)+text(70,49,"Save copy")+line(31,58,189,58)+text(86,81,"Cancel"), (31,28,158,73)),
 "sheet": ("Modal content sheet", "Whole modal panel, not the dimmed background behind it.",rect(20,22,180,84)+rect(89,28,42,4,"#8090a5",2)+text(62,66,"Account details"), (20,22,180,84)),
 "popover": ("Anchored floating panel", "Panel and attached pointer, not the control that opened it.",rect(50,10,120,73)+'<path d="M95 83 L110 98 L125 83" fill="#e7edf5"/>'+text(70,52,"Options"), (50,10,120,88)),
 "disclosureGroup": ("Expandable section", "Expandable header/control, not all expanded child content.",rect(20,14,180,34)+text(30,37,"v  Advanced")+text(43,75,"Child setting",12), (20,14,180,34)),
 "tooltip": ("Hover help bubble", "Small help bubble; not a regular standalone label on the page.",rect(41,31,138,35,"#34475e")+text(53,54,"More information",13,"white"), (41,31,138,35)),
 "contextMenu": ("Context action menu", "Whole contextual menu surface associated with an item; trigger is separate.",rect(57,9,120,96)+text(70,35,"Open")+line(57,43,177,43)+text(70,66,"Copy")+line(57,74,177,74)+text(70,96,"Delete"), (57,9,120,96)),
 "unknown": ("Uncertain native element", "Flag uncertain role/bounds and leave unconfirmed. Not a background catch-all.",rect(62,27,96,52,"#f0e9db")+text(101,64,"?",28), (62,27,96,52)),
 "webContent": ("Reserved compatibility label", "Legacy reserved category; not actively generated. Do not start using it for this focus batch.",rect(28,14,164,81,"#edf0f4")+text(57,47,"WEB CONTENT",12)+text(79,70,"reserved",12), (28,14,164,81)),
}


def illustration(name):
    title, _, content, bounds = SPECS[name]
    x,y,w,h = bounds
    box = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#087c79" stroke-width="2" stroke-dasharray="5 3"/>'
    return f'<svg viewBox="0 0 220 116" role="img" aria-label="{html.escape(title)} schematic with annotation rectangle">{content}{box}</svg>'


def render(output):
    output = fresh(output); output.mkdir(parents=True)
    assert set(SPECS) == set(taxonomy()), "Reference must match every current editor label"
    common = ["collectionItem","listRow","primaryButton","secondaryButton","label","imageView","toggle","tabBar","homeIndicator"]
    def cards(names):
        return ''.join(f'<article><code>{name}</code><h3>{html.escape(SPECS[name][0])}</h3>{illustration(name)}<p>{html.escape(SPECS[name][1])}</p></article>' for name in names)
    css = '''body{margin:0;background:#f5f7fa;color:#1d2b40;font:16px/1.5 system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:32px 24px}h1{font-size:32px;line-height:1.15;margin:0 0 12px}h2{margin:32px 0 16px;font-size:23px}h3{font-size:16px;margin:4px 0}p{margin:8px 0}code{color:#075c5b;font-size:17px;font-weight:700}.intro{max-width:850px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}article{background:white;border:1px solid #d5dee8;border-radius:12px;padding:18px;break-inside:avoid}article svg{display:block;width:100%;height:130px;margin:8px 0}article p{font-size:14px}.rules{background:#e1f0ed;padding:18px 24px;border-radius:12px}.example{display:grid;grid-template-columns:220px 1fr;gap:24px;align-items:center}.example img{max-width:195px}.bad{color:#9d2537}.foot{font-size:13px;color:#526378}li{margin:6px 0}a{color:#075c5b}@media(max-width:760px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.example{grid-template-columns:1fr}}@media(max-width:460px){.grid{grid-template-columns:1fr}main{padding:22px 16px}}@media print{body{background:white}main{padding:0}.grid{grid-template-columns:repeat(3,minmax(0,1fr))}article{padding:10px}article svg{height:100px}h2{break-after:avoid}}'''
    doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>NUIAK annotation cheat sheet</title><style>{css}</style></head><body><main>
<p class="foot">NUIAK · HUMAN REVIEW · 41-label editor reference · 28 September 2026</p>
<h1>Name the control.<br>Box its surface, not its halo.</h1>
<p class="intro">Dashed teal rectangles show suggested annotation extents in <strong>schematic examples</strong>, not native geometry. Class is the control’s role; <strong>focused / unfocused</strong> is a separate flag. A rectangle stays aligned, but you must still verify its edges.</p>
<h2>Your Photos example</h2><section class="example"><img src="../photos-example.png" alt="User supplied Photos app tile with a separate Photos caption"><div><p><code>collectionItem</code> = the selectable tile. Box the white tile surface, including its artwork, <strong>not</strong> the caption below or surrounding glow.</p><p><code>label</code> = “Photos”, separately, only if doing a full detection-label pass. For this focus batch, skip the caption as a separate target.</p><p class="bad">Not homeIndicator. Not a decorative imageView. No polygon around the flower.</p></div></section>
<h2>Box rules to keep beside the editor</h2><section class="rules"><ul><li><strong>Outside caption → separate.</strong> Text inside a button or row → included.</li><li><strong>Use axis-aligned rectangles.</strong> Rounded controls still get rectangular boxes.</li><li><strong>No shadow/glow padding.</strong> The production cropper adds16% context.</li><li><strong>Recheck each frame.</strong> A focused control may be larger.</li><li><strong>Focus does not change the class.</strong> A bright secondary action stays secondary.</li><li><strong>Ambiguous? Flag it.</strong> Do not confirm a guessed role, bound or focus state.</li></ul></section>
<h2>Start here: common tvOS decisions</h2><div class="grid">{cards(common)}</div>
<h2>The rest of the label list</h2><p>Many are iOS/iPadOS/macOS controls, not targets to add to this tvOS focus batch. Annotate what is present—not every category. Containers and their children can coexist in a full detection pass; that is separate from focus-only target review.</p><div class="grid">{cards([n for n in taxonomy() if n not in common])}</div>
<h2>Rectangle workflow</h2><p>On the updated launcher: <strong>R → Create rectangle</strong>; <strong>E → Edit rectangles</strong>. Click two opposite corners. Double-click a control entry to set its class and focus/review flags. Save before changing frames. Save and close your current editor before relaunching to get the rectangle-only toolbar.</p>
<p class="foot">Source: Research/NativeUIElementDetection.md §5.2; category_map.json v1.0; tvOSHomeScreenTemplate.swift card/caption capture points; Research/HumanReviewLabelGuide.md. No labels or training eligibility are granted by this reference. The editor currently lists41 v1.0 classes; later taxonomy extensions are not silently added here.</p>
</main></body></html>'''
    (output/"LabelCheatSheet.html").write_text(doc)
    # Compact companion SVG: same code-native examples, no image alteration.
    height=1480
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="{height}" viewBox="0 0 1080 {height}">'+rect(0,0,1080,height,"#f5f7fa",0)
    svg+=text(44,62,"UI LABELS / QUICK REFERENCE",30)+text(44,97,"Teal box = control surface. Focus is a separate flag.",19)
    for n,name in enumerate(common):
        x=40+(n%3)*350; y=135+(n//3)*325
        svg+=rect(x,y,330,307,"white",12,"#d5dee8")+text(x+18,y+35,name,22,"#075c5b")+text(x+18,y+63,SPECS[name][0],15)
        content=illustration(name).split('>',1)[1].rsplit('</svg>',1)[0]
        svg+=f'<g transform="translate({x+40},{y+83}) scale(1.12)">{content}</g>'
        import textwrap
        for j,s in enumerate(textwrap.wrap(SPECS[name][1],35)[:4]):svg+=text(x+18,y+233+j*18,s,14)
    svg+=text(44,1170,"YOUR PHOTOS TILE",23)+text(44,1211,"collectionItem: white tile only. External caption: label, separately.",20)
    svg+=text(44,1250,"Include text INSIDE a button. Exclude caption BELOW a tile.",20)+text(44,1289,"Exclude diffuse shadow/glow. Cropper adds16% context.",20)
    svg+=text(44,1343,"RECTANGLES ONLY: R to draw / E to edit / save before relaunch",20,"#075c5b")
    svg+=text(44,1392,"Schematic examples • Full41-label illustrated guide: LabelCheatSheet.html",17)
    svg+=text(44,1425,"Do not treat color, class, or a saved file as human focus confirmation.",17)+"</svg>"
    (output/"QuickReference.svg").write_text(svg)
    return output


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("output")
    print(render(parser.parse_args().output))
