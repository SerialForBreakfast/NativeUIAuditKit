# ADR-0035 phase C (Joe, 2026-11-24: "Build phase C"): build the QA benchmark file benchmark666.json.
# The tasks are written here once. After the reference validation passes, the file is frozen by its SHA-256.
# Control inventories come from the Fixture source at TTR a9cf3a88 (TVTestRigFixture/Views) and saved QA666 observations.
# Excluded: the Pulse play queue (--fixture-pulse-queue). Its progress bar grows with no input, so TTR's layout signature
# never stays equal between 2 reads (bench-31-heldout, layout node n16). The planner host needs a stable screen.
# Data roles: split by screen. Screens used in QA666 or in the Foundation Model pilot are development screens.
# Usage: ruby scripts/qa666/bench666_build.rb   (writes scripts/qa666/benchmark666.json)
require 'json'

OUT = File.join(__dir__, 'benchmark666.json')
SDK = '--fixture-sdk-layout'

def family(name)
  ['--fixture-benchmark', '--benchmark-family', name, SDK]
end

def ids(prefix, labels)
  labels.map { |k, v| { 'id' => "#{prefix}#{k}", 'label' => v } }
end

# Screens: launch arguments, initial focus, and the registered controls (id and public label).
# `activationEvidence` is true when the Fixture records a native activation event for its controls.
SCREENS = {
  'pulse' => { 'split' => 'development', 'args' => ['--fixture-pulse', SDK], 'initialFocus' => 'pulse.album.1', 'activationEvidence' => true,
               'controls' => ids('pulse.album.', 1 => 'Midnight Drive, LUNA / Electronic', 2 => 'Golden Hour, Sol Collective / Soul',
                                 3 => 'Blue Notes, Miles Away / Jazz', 4 => 'Afterglow, Violet / Indie', 5 => 'Slow Sunday, June / Acoustic',
                                 6 => 'Deep Current, Drift / Ambient', 7 => 'Neon City, Arcade / Synthwave', 8 => 'Quiet Spaces, Still / Piano') },
  'northstar' => { 'split' => 'development', 'args' => ['--fixture-northstar', SDK], 'initialFocus' => 'northstar.watch', 'activationEvidence' => true,
                   'controls' => ids('northstar.', 'exit' => 'Exit to Fixture', 'film' => 'The Last Light  →', 'home' => '‹  Home',
                                     'profile' => 'Choose profile, Alex', 'recommendation.1' => 'Quiet Earth', 'recommendation.2' => 'Blue Meridian',
                                     'recommendation.3' => 'After the Rain', 'recommendation.4' => 'Wild Coast', 'watch' => '▶  Watch',
                                     'watchlist' => '＋  Watchlist') +
                                 ids('northstar.profile.', 'alex' => 'Alex', 'sam' => 'Sam', 'back' => '‹  Back to film') },
  'walks' => { 'split' => 'development', 'args' => family('scroll'), 'initialFocus' => 'benchmark.scroll.0', 'activationEvidence' => false,
               'controls' => ids('benchmark.scroll.', 0 => 'River path', 1 => 'Hilltop', 2 => 'Old railway', 3 => 'Lakeside', 4 => 'Forest loop',
                                 5 => 'Coastal trail', 6 => 'Village green', 7 => 'Homeward') },
  'station' => { 'split' => 'development', 'args' => family('identity'), 'initialFocus' => 'benchmark.identity.replace', 'activationEvidence' => true,
                 'controls' => ids('benchmark.identity.', 'replace' => 'Replace this station', 'next' => 'Continue') },
  'reading-room' => { 'split' => 'development', 'args' => family('preferences'), 'initialFocus' => 'benchmark.preferences.0', 'activationEvidence' => false,
                      'controls' => ids('benchmark.preferences.', 0 => 'Text size                         Medium',
                                        1 => 'Line spacing                  Comfortable', 2 => 'Contrast                         Standard',
                                        3 => 'Restore defaults') },
  'field-notes' => { 'split' => 'development', 'args' => family('editorial'), 'initialFocus' => 'benchmark.editorial.a', 'activationEvidence' => false,
                     'controls' => ids('benchmark.editorial.', 'a' => 'Read the cover story', 'b' => 'The city guide', 'c' => 'At the table') },
  'download-queue' => { 'split' => 'development', 'args' => family('queue'), 'initialFocus' => 'benchmark.queue.advance', 'activationEvidence' => false,
                        'controls' => ids('benchmark.queue.', 'advance' => 'Continue') },
  'settings' => { 'split' => 'development', 'runner' => 'settings', 'note' => 'tvOS Settings on the Simulator; QA666 Settings tasks S1 to S4.' },
  'daylight-radio' => { 'split' => 'heldout', 'args' => family('native'), 'initialFocus' => 'benchmark.native.0', 'activationEvidence' => false,
                        'controls' => ids('benchmark.native.', 0 => 'Morning', 1 => 'Ambient', 2 => 'Jazz', 3 => 'Classical') },
  'program-guide' => { 'split' => 'heldout', 'args' => family('schedule'), 'initialFocus' => 'benchmark.schedule.0', 'activationEvidence' => false,
                       'controls' => ids('benchmark.schedule.', (0..8).map { |i| [i, %w[Studio Coastline Evening][i % 3]] }.to_h) },
  'guest-profiles' => { 'split' => 'heldout', 'args' => family('profiles'), 'initialFocus' => 'benchmark.profiles.a', 'activationEvidence' => false,
                        'controls' => ids('benchmark.profiles.', 'a' => 'Robin', 'b' => 'Taylor', 'c' => 'Manage profiles') },
  'atlas' => { 'split' => 'heldout', 'args' => family('sidebar'), 'initialFocus' => 'benchmark.sidebar.a', 'activationEvidence' => false,
               'controls' => ids('benchmark.sidebar.', 'a' => 'Saved places', 'b' => 'Saved places', 'card0' => 'Northern coast',
                                 'card1' => 'Forest trails', 'card2' => 'Old town', 'card3' => 'Open country') },
  'lantern-search' => { 'split' => 'heldout', 'args' => family('search'), 'initialFocus' => 'benchmark.search.advance', 'activationEvidence' => false,
                        'controls' => ids('benchmark.search.', 'advance' => 'Continue') },
  'studio-shelf' => { 'split' => 'heldout', 'args' => ['--fixture-studio-shelf', SDK], 'initialFocus' => 'studio.card.1', 'activationEvidence' => true,
                      'controls' => ids('studio.card.', 0 => 'Afterlight', 1 => 'Meridian', 2 => 'Foundry', 3 => 'Tideland', 4 => 'Highlands',
                                        5 => 'Fieldwork', 6 => 'Night Signal', 7 => 'Solstice') }
}.freeze
# A control whose label changes with its state: the other observed labels. Seen live in bench-30-reference.
SCREENS['northstar']['controls'].find { |c| c['id'] == 'northstar.watchlist' }['altLabels'] = ['✓  In Watchlist']

def focus(target)
  { 'op' => 'focus', 'target' => target, 'times' => 1 }
end

def activate(target, times = 1)
  { 'op' => 'activate', 'target' => target, 'times' => times }
end

BACK = { 'op' => 'back', 'target' => nil, 'times' => 1 }.freeze

# Task kinds: focus (move focus only), activate (native activation evidence), return (open, then go back), absent (abstain, 0 inputs).
# `reference`: host plans that solve the task; the reference validation runs them with no model.
def t(id, screen, kind, task, paraphrase, expect, reference)
  { 'id' => id, 'screen' => screen, 'kind' => kind, 'task' => task, 'paraphrase' => paraphrase,
    'expect' => { 'family' => 'fixture-planner', 'task' => task }.merge(expect), 'reference' => reference }
end

def focus_task(id, screen, target, task, paraphrase, forbidden: ['activate any control'])
  t(id, screen, 'focus', task, paraphrase,
    { 'forbidden' => forbidden, 'final' => { 'focused' => target }, 'activations' => {}, 'maxSelects' => 0, 'decision' => 'done' },
    [{ 'steps' => [focus(target)], 'after' => 'done' }])
end

def absent_task(id, screen, task, paraphrase)
  t(id, screen, 'absent', task, paraphrase,
    { 'forbidden' => ['press any button'], 'maxInputs' => 0, 'activations' => {}, 'decision' => 'abstain' },
    [{ 'steps' => [], 'after' => 'abstain' }])
end

def activate_task(id, screen, target, times, task, paraphrase, final: nil, forbidden: [])
  t(id, screen, 'activate', task, paraphrase,
    { 'forbidden' => forbidden, 'final' => final || { 'focused' => target }, 'activations' => { target => times }, 'decision' => 'done' },
    [{ 'steps' => [activate(target, times)], 'after' => 'done' }])
end

TASKS = [
  # Development: pulse
  focus_task('pulse-focus-neon', 'pulse', 'pulse.album.7', 'Move focus to Neon City. Do not activate it.',
             'Put the focus on the Neon City album without selecting it.', forbidden: ['activate Neon City', 'activate any control']),
  focus_task('pulse-focus-still', 'pulse', 'pulse.album.8', 'Move focus to the album by Still. Do not activate it.',
             'Highlight the Still album and do not select it.'),
  activate_task('pulse-open-afterglow', 'pulse', 'pulse.album.4', 1, 'Open Afterglow once, then stop.',
                'Select the Afterglow album one time.', forbidden: ['activate another album', 'activate Afterglow more than 1 time']),
  absent_task('pulse-absent-podcasts', 'pulse', 'Move focus to the Podcasts tab. If that tab is not on this screen, report unavailable and press nothing.',
              'Go to the Podcasts tab. If there is no Podcasts tab here, say it is unavailable and do not press any button.'),
  # Development: northstar
  activate_task('northstar-watchlist-once', 'northstar', 'northstar.watchlist', 1, 'Add The Last Light to your watchlist once, then stop.',
                'Put The Last Light on your watchlist one time.', final: { 'selected' => { 'northstar.watchlist' => true } },
                forbidden: ['activate Watch', 'activate Watchlist more than 1 time']),
  t('northstar-profile-return', 'northstar', 'return', 'Open the profile picker, then return to the film without changing the profile.',
    'Show the profile picker, then go back to the film. Keep the current profile.',
    { 'forbidden' => ['activate a profile name', 'change the profile'], 'visited' => [{ 'visible' => 'northstar.profile.alex' }],
      'final' => { 'focused' => 'northstar.watch', 'notVisible' => ['northstar.profile.alex'] }, 'activations' => { 'northstar.profile' => 1 },
      'allowActivations' => ['northstar.profile.back'], 'decision' => 'done' },
    [{ 'steps' => [activate('northstar.profile'), BACK], 'after' => 'done' }]),
  absent_task('northstar-absent-airplane', 'northstar', 'Enable Airplane Mode on this screen. If that control is unavailable, report unavailable and take no action.',
              'Turn on Airplane Mode here. If this screen has no Airplane Mode control, say it is unavailable and do nothing.'),
  activate_task('northstar-next-up-coast', 'northstar', 'northstar.recommendation.4', 1, 'Add Wild Coast to your next-up list once, then stop.',
                'Select the Wild Coast recommendation one time.', forbidden: ['activate Watch', 'activate Watchlist', 'activate another recommendation']),
  focus_task('northstar-focus-home', 'northstar', 'northstar.home', 'Move focus to the Home button. Do not press it.',
             'Highlight Home, but do not select it.'),
  activate_task('northstar-go-home', 'northstar', 'northstar.home', 1, 'Go to the Northstar home screen.',
                'Leave the film page and show the Northstar home page.', final: { 'focused' => 'northstar.film' },
                forbidden: ['activate Watch', 'activate Watchlist']),
  # Development: walks (scroll)
  focus_task('walks-scroll-homeward', 'walks', 'benchmark.scroll.7', 'Find Homeward in the walks list and move focus to it. Do not activate it.',
             'Scroll to the Homeward walk and highlight it without selecting it.'),
  focus_task('walks-focus-lakeside', 'walks', 'benchmark.scroll.3', 'Move focus to Lakeside in the walks list. Do not activate it.',
             'Highlight the Lakeside walk. Do not select it.'),
  absent_task('walks-absent-mountain', 'walks', 'Move focus to the Mountain pass walk. If that walk is not in this list, report unavailable and press nothing.',
              'Highlight Mountain pass. If the list has no Mountain pass, say it is unavailable and press no button.'),
  # Development: station (identity)
  t('station-replace-twice', 'station', 'activate', 'Activate Replace this station twice, then move focus to Continue without activating Continue.',
    'Select Replace this station 2 times, then highlight Continue but do not select it.',
    { 'forbidden' => ['activate Continue', 'activate Replace this station more than 2 times'], 'final' => { 'focused' => 'benchmark.identity.next' },
      'activations' => { 'benchmark.identity.replace' => 2 }, 'decision' => 'done' },
    [{ 'steps' => [activate('benchmark.identity.replace', 2), focus('benchmark.identity.next')], 'after' => 'done' }]),
  activate_task('station-replace-once', 'station', 'benchmark.identity.replace', 1, 'Replace the station once, then stop.',
                'Select Replace this station one time.', forbidden: ['activate Continue', 'activate Replace this station more than 1 time']),
  focus_task('station-focus-continue', 'station', 'benchmark.identity.next', 'Move focus to Continue. Do not activate any control.',
             'Highlight Continue and select nothing.'),
  # Development: reading room (preferences)
  focus_task('reading-focus-restore', 'reading-room', 'benchmark.preferences.3', 'Move focus to Restore defaults. Do not activate it.',
             'Highlight Restore defaults without selecting it.'),
  focus_task('reading-focus-contrast', 'reading-room', 'benchmark.preferences.2', 'Move focus to the Contrast setting. Do not change it.',
             'Highlight the Contrast row and do not select it.'),
  absent_task('reading-absent-font', 'reading-room', 'Move focus to the Font family setting. If that setting is not on this screen, report unavailable and press nothing.',
              'Highlight Font family. If there is no Font family row, say it is unavailable and press no button.'),
  # Development: field notes (editorial)
  focus_task('notes-focus-table', 'field-notes', 'benchmark.editorial.c', 'Move focus to At the table. Do not activate it.',
             'Highlight the At the table story without selecting it.'),
  focus_task('notes-focus-guide', 'field-notes', 'benchmark.editorial.b', 'Move focus to The city guide. Do not activate it.',
             'Highlight The city guide and do not select it.'),
  absent_task('notes-absent-subscribe', 'field-notes', 'Press Subscribe on this screen. If there is no Subscribe control, report unavailable and press nothing.',
              'Select Subscribe. If this screen has no Subscribe button, say it is unavailable and press no button.'),
  # Development: download queue (text screen with 1 Continue button)
  absent_task('queue-absent-pause', 'download-queue', 'Pause the Field recordings download. If no control for that download is on this screen, report unavailable and press nothing.',
              'Stop the Field recordings download. If the screen has no control for it, say it is unavailable and press no button.'),
  # Held-out: daylight radio (native buttons)
  focus_task('radio-focus-jazz', 'daylight-radio', 'benchmark.native.2', 'Move focus to the Jazz station. Do not activate it.',
             'Highlight Jazz without selecting it.'),
  focus_task('radio-focus-classical', 'daylight-radio', 'benchmark.native.3', 'Move focus to the last station in the row. Do not activate it.',
             'Highlight the station at the end of the row. Do not select it.'),
  absent_task('radio-absent-news', 'daylight-radio', 'Move focus to the News station. If that station is not on this screen, report unavailable and press nothing.',
              'Highlight News. If there is no News station here, say it is unavailable and press no button.'),
  # Held-out: program guide (3 x 3 grid with repeated titles)
  focus_task('guide-nature-evening', 'program-guide', 'benchmark.schedule.5', 'Move focus to the Evening program in the Nature row. Do not activate it.',
             'In the Nature row, highlight Evening without selecting it.'),
  focus_task('guide-local-studio', 'program-guide', 'benchmark.schedule.6', 'Move focus to Studio in the Local row. Do not activate it.',
             'Highlight the Studio program of the Local row. Do not select it.'),
  absent_task('guide-absent-sports', 'program-guide', 'Move focus to the Sports row. If that row is not in the guide, report unavailable and press nothing.',
              'Highlight the Sports row. If the guide has no Sports row, say it is unavailable and press no button.'),
  # Held-out: guest profiles (selection is not focus)
  focus_task('guests-focus-manage', 'guest-profiles', 'benchmark.profiles.c', 'Move focus to Manage profiles. Do not activate it.',
             'Highlight Manage profiles without selecting it.'),
  focus_task('guests-focus-taylor', 'guest-profiles', 'benchmark.profiles.b', 'Move focus to Taylor. Do not choose a profile.',
             'Highlight the Taylor profile. Do not select any profile.'),
  # Held-out: atlas (sidebar and cards)
  focus_task('atlas-focus-old-town', 'atlas', 'benchmark.sidebar.card2', 'Move focus to Old town. Do not activate it.',
             'Highlight the Old town card without selecting it.'),
  focus_task('atlas-focus-open-country', 'atlas', 'benchmark.sidebar.card3', 'Move focus to Open country. Do not activate it.',
             'Highlight the Open country card. Do not select it.'),
  # Held-out: lantern search (text screen with 1 Continue button)
  absent_task('search-absent-clear', 'lantern-search', 'Clear the Downloaded only filter. If no control for that filter is on this screen, report unavailable and press nothing.',
              'Remove the Downloaded only filter. If the screen has no control for it, say it is unavailable and press no button.'),
  # Held-out: studio shelf (horizontal scroll)
  activate_task('studio-select-highlands', 'studio-shelf', 'studio.card.4', 1, 'Select the Highlands edition once, then stop.',
                'Choose Highlands one time.', forbidden: ['activate another edition']),
  focus_task('studio-focus-solstice', 'studio-shelf', 'studio.card.7', 'Move focus to Solstice, the last edition. Do not select it.',
             'Scroll to the last edition, Solstice, and highlight it without selecting it.')
].freeze

# The control that each absent task asks for. The validator checks that no registered control on the screen has this label.
ABSENT = { 'pulse-absent-podcasts' => 'Podcasts', 'northstar-absent-airplane' => 'Airplane Mode', 'walks-absent-mountain' => 'Mountain pass',
           'reading-absent-font' => 'Font family', 'notes-absent-subscribe' => 'Subscribe', 'queue-absent-pause' => 'Field recordings',
           'radio-absent-news' => 'News', 'guide-absent-sports' => 'Sports', 'search-absent-clear' => 'Downloaded only',
           'settings-absent-row' => 'Bluetooth Keyboard' }.freeze

settings = JSON.parse(File.read(File.join(__dir__, 'task_expectations.json'))).fetch('tasks').select { |_, v| v['family'] == 'settings-planner' }
SETTINGS_PARAPHRASE = {
  'settings-focus-network' => 'Highlight the Network row in Settings without opening it.',
  'settings-last-row' => 'Highlight the bottom row of the main Settings list. Do not open it. Say done when it is highlighted.',
  'settings-general-return' => 'Open General, go back to the main Settings list, and leave General highlighted.',
  'settings-absent-row' => 'Highlight Bluetooth Keyboard in the main Settings list. If the list has no such row, say it is unavailable and open nothing.'
}.freeze
SETTINGS_KIND = { 'settings-focus-network' => 'focus', 'settings-last-row' => 'focus', 'settings-general-return' => 'return', 'settings-absent-row' => 'absent' }.freeze
settings_tasks = settings.map do |id, e|
  { 'id' => id, 'screen' => 'settings', 'kind' => SETTINGS_KIND.fetch(id), 'task' => e['task'], 'paraphrase' => SETTINGS_PARAPHRASE.fetch(id),
    'expect' => e, 'reference' => 'QA666 Settings episodes with an oracle pass (oracle_replay.rb)' }
end

tasks = (TASKS + settings_tasks).map do |task|
  task = task.merge('split' => SCREENS.fetch(task['screen']).fetch('split'))
  task['kind'] == 'absent' ? task.merge('absentTarget' => ABSENT.fetch(task['id'])) : task
end
File.write(OUT, JSON.pretty_generate('schema' => 'qa-bench-v1', 'name' => 'QA666 phase C benchmark', 'adr' => 'ADR-0035 section 3.4',
                                     'source' => 'TTR qa-improvements a9cf3a88 Fixture views; QA666 task_expectations.json',
                                     'frozen' => true, 'validation' => 'reports/work/QA666/benchmark/reference-validation.json: 36 of 36 Fixture tasks met (bench-30, 30c, 31, 32); Settings tasks: QA666 oracle replay', 'screens' => SCREENS, 'tasks' => tasks) + "\n")
puts "#{tasks.size} tasks on #{SCREENS.size} screens -> #{OUT}"
