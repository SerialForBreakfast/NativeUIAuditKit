"""Explain experiments for display without changing their execution specifications."""

# These questions describe the study. A job may supply only part of its answer.
STUDIES = {
    'FOCUS373': ('Check group balance, data roles, and risk support',
                 'Which comparisons justify a correction without changing evaluation roles or losing previous successes?'),
    'HCF371': ('Compare native HCF rules and learned models',
               'Which method selects focus reliably while preserving previous successes?'),
    'FOCUS366': ('Learn notification changes without losing movement',
                 'Can fresh notification examples reduce false changes while preserving dimmed-corner movement and previous successes?'),
    'FOCUS365': ('Test Settings, dialogs, and corner layouts',
                 'Do the newer authored layouts expose failures beyond media shelves?'),
    'FOCUS364': ('Focus movement versus notifications and dimming',
                 'Which appearance changes cause false changes, missed movements, or hidden focus cues?'),
    'HCF361': ('Build a native High Contrast Focus study',
               'Does HCF provide a useful focus cue, and which image view should the first trained model use?'),
    'DATASET351': ('Focus movement versus changing content',
                   'Can existing models separate focus movement, content changes, and repeated captures?'),
    'GENERATION352': ('Generate controlled focus examples',
                      'Can Fixture supply verified examples for comparing movement with content changes?'),
    'GENERATION354': ('Change one visual factor at a time',
                      'Which control sizes, growth effects, shadows, positions, or backgrounds cause missed movements or false changes?'),
    'FOCUS341': ('Add detail without replacing original crops',
                 'Does extra boundary detail help subtle effects, and do content-change examples prevent false focus changes?'),
    'FOCUS342': ('Balance old and new training examples',
                 'Can we learn content changes without forgetting movements the model already detects?'),
    'FOCUS343': ('Check whether useful focus detail reaches the model',
                 'Are misses caused by missing visual detail, repeated artwork, or something beyond crop coverage?'),
    'FOCUS344': ('Separate whole-screen evidence from control detail',
                 'Which source of visual evidence causes the wrong decision and needs correction?'),
    'HCF362': ('Capture matched native Standard and HCF frames',
               'Do native Standard and HCF captures of the same scene differ only near the observed focused control?'),
    'HCF367': ('Recover the HCF setting and repeat native captures',
               'Can the setting be restored without manual Settings changes, and do repeated captures match exactly?'),
    'HCF368': ('Capture native HCF image cards at 2 positions',
               'Does the HCF difference follow the observed focused card at both tested positions?'),
    'HCF369': ('Measure where the HCF difference falls',
               'Does at least 90% of the Standard/HCF difference fall within 64 px of the observed focused control?'),
    'HCF370': ('Test other corners, center positions, and artwork',
               'Does the spatial HCF result hold at new positions and with exchanged artwork?'),
    'HCF374': ('Find repeated images and crops in HCF371',
               'How many frames and crops are distinct, and do repeated pixels cross data roles?'),
    'HCF375': ('Train on balanced HCF and Standard examples',
               'Does adding Standard-profile examples remove Standard-profile misses without losing HCF gains?'),
    'FOCUS372': ('Check native capture records before training',
                 'Do the native records carry the geometry and receipts that a training comparison needs?'),
    'FOCUS346': ('Change appearance while keeping focus labels fixed',
                 'Which brightness, contrast, or color changes alter decisions that should stay the same?'),
    'FOCUS347': ('Find where appearance changes mislead the model',
                 'Does the error start in the whole-screen view, the detail view, or selection of the detail region?'),
    'FOCUS348': ('Teach the model to tolerate appearance changes',
                 'Does varied appearance reduce false changes without losing previously detected movements?'),
    'FOCUS349': ('Preserve movement detection during appearance training',
                 'Does giving movements more training weight keep appearance gains without losing movement detection?'),
    'FOCUS355': ('Teach focus at different screen positions',
                 'Does varied position help, or must the whole-screen part of the model also learn differently?'),
    'FOCUS356': ('Check why whole-screen scores suppress movements',
                 'Does the correction raise real movement scores more than scores for content changes?'),
    'FOCUS358': ('Test whether longer training helps',
                 'Do 30 training passes detect more real movements than 10 passes without losing previous successes?'),
    'FOCUS359': ('Test richer screens and smaller image files',
                 'Which scene features or image changes remove useful focus evidence or cause wrong decisions?'),
    'HCF350': ('Compare High Contrast Focus with normal focus',
               'When does High Contrast Focus improve selection, and when do existing methods still fail?'),
    'HCF357': ('Measure preparation speed for stored images',
               'Does parallel image decoding reduce preparation time on the USB drive?'),
    'HCF358': ('Prepare a measured High Contrast Focus study',
               'Do verified effects, training evidence, and storage capacity support the next study stage?'),
    'RESEARCH338': ('Repeat a recorded audit',
                    'Can the queue reproduce the recorded audit? Agreement does not establish model accuracy.'),
    'RESEARCH339': ('Repeat a recorded training run',
                    'Can the queue reproduce saved training results within the declared tolerances?'),
    'VISION353': ('Measure what Apple Vision adds',
                  'Do similarity, rectangle detection, or text recognition supply useful evidence about focus?'),
}

RESEARCH_TESTS = {
    'A1': ('Artwork changes with fixed focus', 'Does changing artwork cause false focus changes when geometry and focus stay fixed?'),
    'A2': ('Separate growth, border, shadow, and tint', 'Which effects help recognition, and which combinations cause errors?'),
    'A3': ('Equal image change from different causes', 'Can the model separate focus movement from equally large content changes?'),
    'A4': ('Bright decoration on unfocused controls', 'Do borders, badges, or shadows cause false selections?'),
    'A5': ('Screens with no focused control', 'Can the model report no selection instead of inventing one?'),
    'B1': ('Move the same control across the screen', 'Do corners and edges produce more errors than the center?'),
    'B2': ('Partly visible controls', 'How much clipping makes focus detection or location unreliable?'),
    'B3': ('Fractional-pixel rendering shifts', 'Do tiny rendering shifts cause false focus changes?'),
    'B4': ('Keep more of the focus boundary', 'Do current crops remove useful evidence at control edges?'),
    'B5': ('Focus between identical neighbors', 'Can the model locate focus without relying on artwork differences?'),
    'C1': ('Scrolling versus focus movement', 'Can the model separate background scrolling from focus moving between controls?'),
    'C2': ('Focus during animation', 'When can we report settled focus without declaring readiness too early?'),
    'C3': ('Read a transition in both directions', 'Does reversing the frames preserve change detection and exchange the predicted locations?'),
    'C4': ('Interrupt a screen with an overlay', 'Does the model notice interruptions without treating harmless overlays as focus movement?'),
    'C5': ('Missing, delayed, or repeated captures', 'Does the system reject stale evidence and recover without false stability?'),
    'D1': ('Learn strong effects before subtle effects', 'Does exaggerated early training improve recognition of native-strength effects?'),
    'D2': ('Generated effects versus native effects', 'Which rendering differences occur alongside model errors?'),
    'D3': ('New combinations of familiar effects', 'Can the model combine cues it has not seen together during training?'),
    'D4': ('Interactions between visual factors', 'Which combinations of size, contrast, spacing, theme, and artwork cause errors?'),
    'D5': ('Choose training examples by observed failures', 'Does targeted sampling improve more than uniform sampling with the same training budget?'),
}

NATIVE_TESTS = {
    'hero-swap': ('Change the large background artwork', 'Keep observed focus fixed while changing the large artwork behind controls.', 'Does artwork alone cause a false focus change?'),
    'selected-tab': ('Selected tabs are not always focused', 'Compare selected but unfocused tabs with the control that actually has focus.', 'Does the model confuse selection styling with focus?'),
    'identical-rows': ('Move focus between identical rows', 'Keep row content identical while moving observed focus.', 'Can the model locate focus without text or artwork differences?'),
    'library-state': ('Switch between empty and populated screens', 'Observe focus before and after library content appears or disappears.', 'Does the model detect the actual focus state and its restoration?'),
    'native-corners': ('Detect native focus near corners', 'Compare observed focus and measured bounds at screen corners.', 'Do corner positions cause missed focus or wrong locations?'),
    'growth-curve': ('Measure the native growth effect', 'Measure scale and shadow changes across control sizes. Reserve other sizes for checking the fit.', 'Can measured effects support more faithful synthetic examples?'),
    'clipping': ('Focus on partly visible controls', 'Record full and visible bounds while progressively clipping controls.', 'At which visible sizes do focus and location become unreliable?'),
    'position-grid': ('Place focus across the screen', 'Compare related scenes with focus in different measured screen regions.', 'Does screen position change recognition when other cues stay matched?'),
    'fonts': ('Change text style and measure new bounds', 'Compare font variations and their actual control geometry.', 'Do text styles or geometry changes cause focus errors?'),
    'alpha': ('Noninteractive text over varied backgrounds', 'Vary background transparency while recording which elements can actually receive focus.', 'Does decorative text produce false control candidates?'),
    'row-inversion': ('Bright rows versus focused rows', 'Compare native row focus styling with bright unfocused rows and content-only changes.', 'Does the model follow actual focus rather than row brightness?'),
    'palette': ('Change screen colors', 'Compare dark, bright, and contrasting palettes with matched measured geometry.', 'Which palettes cause wrong focus decisions?'),
    'animation': ('Measure focus through animation', 'Use actual capture times and observed focus before, during, and after transitions.', 'How early can focus be recognized without reporting stability too soon?'),
    'no-focus': ('Verify that no control has focus', 'Compare observed no-focus scenes with scenes containing a focused control.', 'Can the system avoid inventing a focused control?'),
    'renderer-gap': ('Compare native and authored rendering', 'Render matched recipes through both paths and compare eligible predictions and runtime.', 'Which rendering differences matter for model errors and generation cost?'),
    'journey-shadow': ('Replay a recorded navigation route', 'Analyze fixed routes without allowing the model to send navigation commands.', 'Which route events produce useful or misleading focus evidence?'),
    'family-holdout': ('Test on screen families absent from training', 'Separate connected templates and artwork before model selection.', 'Does performance transfer to different screen families rather than repeated scenes?'),
    'feature-cache': ('Reuse previously computed image features', 'Compare cached and uncached outputs with all input identities fixed.', 'Can feature reuse save time without changing decisions?'),
}

HCF_STAGES = {
    'visible-family': ('Find a visible native HCF effect', 'Compare matched Standard and HCF images with observed focus.', 'Is there a repeatable visible effect to teach, rather than identical images with different settings?'),
    'producer-offload': ('Move completed capture batches safely', 'Check capture quotas and verified offload before the next batch starts.', 'Can collection continue without filling storage or losing useful captures?'),
    'group-freeze': ('Separate related scenes before training', 'Check shared artwork, repeated scenes, and profile counterparts across data roles.', 'Can evaluation avoid scenes related to the training data?'),
    'resume': ('Resume training after an interruption', 'Compare restored optimizer, scheduler, random state, and model state with uninterrupted training.', 'Can long training jobs resume without silently changing the experiment?'),
    'worker-capacity': ('Check execution worker capacity', 'Measure available storage and training input throughput on the execution worker.', 'Can the worker run the approved study without unsafe storage use or input delays?'),
    'baselines': ('Measure current methods on the same cases', 'Compare pinned rules and existing models using identical eligible examples.', 'What must a new HCF model improve, and which current successes must it preserve?'),
    'seed-repeats': ('Repeat promising training with different seeds', 'Repeat selected settings with 3 seeds total and compare matched errors.', 'Does the improvement repeat, or depend on one favorable training run?'),
    'final-audit': ('Check the frozen candidate on reserved scenes', 'Evaluate fixed models and thresholds on groups excluded from development and calibration.', 'Does the selected improvement survive an independent check?'),
    'coreml': ('Check the converted model on Apple hardware', 'Compare preprocessing, predictions, decisions, package size, and runtime after Core ML conversion.', 'Does the converted model preserve useful behavior and meet runtime requirements?'),
    'shadow': ('Observe the candidate inside TTR', 'Analyze real cases without giving the candidate navigation authority.', 'Does optional TTR use reveal new failures that need targeted training examples?'),
}


def describe(row):
    """Return display text only. Do not modify the row or its specification."""
    job, task = row.get('job', ''), row.get('task', '')
    test = row.get('hypothesis') or 'The registered specification does not describe this test.'
    if row.get('question'):
        title, answer, source = row['question'], row.get('decisionRule', ''), 'job'
    elif task in STUDIES:
        (title, answer), source = STUDIES[task], 'study'
    else:
        # Show the job's own registered text. Never show placeholder text.
        title, answer, source = row.get('hypothesis', job), row.get('decisionRule', ''), 'job'
    if task in ('FOCUS364', 'FOCUS365', 'FOCUS366', 'FOCUS373'):
        title = row.get('hypothesis', title)
        answer = row.get('decisionRule', answer)
        source = 'job'
    if task.startswith('RESEARCH340-') and task.split('-')[-1] in RESEARCH_TESTS:
        title, answer = RESEARCH_TESTS[task.split('-')[-1]]
        source = 'study'
    if task in ('FOCUS355', 'FOCUS358'):
        parts = job.split('-')
        arm = parts[1] if len(parts) > 1 else ''
        arm_name = {'control': 'unchanged training examples', 'position': 'examples at varied screen positions',
                    'branch': 'varied positions with whole-screen training'}.get(arm, 'the fixed candidates')
        if job.endswith('-train'):
            title = 'Train with ' + arm_name
            duration = '30' if task == 'FOCUS358' else '10'
            test = 'Train for ' + duration + ' passes using ' + arm_name + '. Keep the registered initialization and comparison settings.'
            answer = 'Does this training produce a candidate worth testing? Only the later comparisons can show an improvement.'
        elif 'summary' in parts or 'comparison' in parts or 'decision' in parts:
            title = 'Combine results before accepting a candidate'
            test = 'Collect the required comparisons. Count recovered movements, false changes, and previous successes lost. Reject incomplete evidence.'
            answer = 'Does the candidate improve the target failure without losing previous successes? Completion alone does not mean acceptance.'
        else:
            condition = parts[-1]
            title = 'Check ' + arm_name + ': ' + condition
            test = {
                'movement': 'Score observed focus movements and count detected movements, misses, and withheld decisions.',
                'content': 'Score artwork changes while focus stays fixed. Count false focus changes and withheld decisions.',
                'recapture': 'Score repeated captures without a requested focus change. Count false changes and withheld decisions.',
                'center': 'Score retained distractions near the screen center and compare every decision with the fixed baseline.',
                'left': 'Score retained left-side distractions and compare every decision with the fixed baseline.',
                'global': 'Score retained whole-screen distractions and compare every decision with the fixed baseline.',
                'native': 'Score retained native examples and count previously correct decisions that become wrong or uncertain.',
                'replay': 'Score the retained replay set and count gains, errors, and previously correct decisions lost.',
                'original': 'Score retained original examples without changing crops or thresholds. Count gains and previous successes lost.',
                'placeholders': 'Score retained placeholder-artwork cases and count gains and previous successes lost.',
            }.get(condition, test)
            answer = 'Does this candidate preserve correct decisions on this set? Other comparison jobs check the remaining conditions.'
        source = 'job'
    for suffix, description in NATIVE_TESTS.items():
        if job.startswith('focus359-plan-') and job.endswith('-' + suffix):
            title, test, answer = description
            source = 'job'
    if job.startswith('focus359-compression-'):
        factor = job.removeprefix('focus359-compression-')
        title = 'Preserve focus evidence in smaller files: ' + factor
        test = 'Compare original, half-size PNG, half-size JPEG, and full-size JPEG images. Count misses, false changes, and lost successes.'
        answer = 'Which image changes save storage without removing useful focus evidence for this visual factor?'
        source = 'job'
    if job.startswith('focus359-lossless-'):
        level = job.removeprefix('focus359-lossless-')
        title = 'Measure lossless PNG compression: level ' + level
        test = 'Encode retained images at this compression level. Verify exact decoded pixels and measure file size and processing time.'
        answer = 'Does this setting save enough space to justify its encoding and decoding cost?'
        source = 'job'
    if job.startswith('hcf358-plan-'):
        stage = job.removeprefix('hcf358-plan-')
        if stage in HCF_STAGES:
            title, test, answer = HCF_STAGES[stage]
            source = 'job'
        for kind in ('generate', 'detector', 'classifier'):
            if stage.startswith(kind + '-'):
                count = stage.removeprefix(kind + '-')
                title = {'generate': 'Validate HCF data', 'detector': 'Find focus across the full screen',
                         'classifier': 'Recognize focus inside proposed control crops'}[kind] + ': ' + count + ' frames'
                test = {'generate': 'Generate this data stage and check observed labels, group separation, coverage, and storage.',
                        'detector': 'Train a focused-control detector at this data stage. Compare missed controls, wrong selections, and previous successes.',
                        'classifier': 'Train the existing crop classifier at this data stage. Test fixed proposals separately from known correct boxes.'}[kind]
                answer = {'generate': 'Does this stage add qualified examples for the next matched training comparison?',
                          'detector': 'Does more qualified HCF data improve full-screen selection without losing previous successes?',
                          'classifier': 'Does more data improve focus classification, or do missing control proposals limit the result?'}[kind]
                source = 'job'
    return dict(title=title, test=test, answers=answer, source=source)


def describe_jobs(data):
    """Build an immutable-spec-independent display catalog for one snapshot."""
    return {row['job']: describe(row) for row in data.get('jobs', []) if 'job' in row}
