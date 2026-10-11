"""help_text.py の英語版（名前と形は help_text.py と同じ）。

英語の画面のとき、help_text.py の末尾でここの値に置き換える。用語は data/i18n/GLOSSARY.md にそろえる。
help_text.py を直したら、ここも同じように直す。
"""
_STYLE = "<style>h3{margin:0 0 4px 0} h4{margin:10px 0 2px 0} ul{margin-top:2px; padding-left:16px} li{margin-bottom:3px}</style>"

MAP = _STYLE + """
<h3>Using the map</h3>
<h4>Adding genes</h4>
<ul>
<li><b>Focus</b> (<span style='color:#e65100'>orange</span>): type a gene name in the search box, pick it from the suggestions, and click "Focus".
The map draws relations from that gene for the set number of "upstream" and "downstream" steps. You can also pick a suggestion with ↑↓ and Enter; Esc clears the search box.</li>
<li><b>Expand</b> (<span style='color:#6a1b9a'>purple</span>): click a gene, click it again, and choose "Expand". This adds one more step upstream and downstream.
For a gene not on the map, "Expand" from the search box adds it together with its connections to the current map.</li>
<li><b>Select</b> (<span style='color:#43a047'>green</span>): click a gene. Hold Shift to select several.
All edges of selected genes are drawn, including edges that are normally hidden.</li>
</ul>
<h4>Looking closer</h4>
<ul>
<li>Click a gene, an edge, or a complex box (dotted) to show its description, supporting papers, and members on the right (for a gene, its Complex Portal complexes are also shown).
An edge you click, or pick from a list in the details panel, is drawn on the map even if it is normally hidden.
For literature-verified edges, the details panel also shows, when the paper states them: the partner (e.g. a cyclin), the modified site, the supporting experiment, necessity/sufficiency, redundant upstream regulators, strength, what is changed (expression, activity, degradation, localization), and timing.</li>
<li>Use ◀ ▶ in the details panel to go back to genes and edges shown earlier (the map selection goes back too). "Help" at the bottom of the details panel explains how to read what is shown (◀ to return).</li>
<li>"+number" under a gene is the number of downstream genes not yet drawn. The width of a gene box reflects its number of edges (including hidden ones).</li>
<li>When a gene has more than 50 downstream genes (e.g. phosphorylation targets of kinases such as PHO85 and CDC28), they are not drawn as edges but placed at the bottom of the map
in boxes per regulation type, such as "Downstream of ○○: phosphorylation 377". Edges from the source gene into the box, and edges between genes in the box, are normally hidden;
click the box to show them (click again to hide). Selecting a gene in the box (green) also shows its edges (selecting the source gene in green does not show the edges to the box). Edges between genes in the box and other genes are drawn as usual.
Unlike complexes, focusing on or expanding a gene in the box does not add the other downstream genes of the same source.</li>
<li>Complexes (budding yeast complexes from Complex Portal) are boxed when two or more members are on the map.
A gene can be in only one box, so complexes with more members on the map are filled first. The other members of a complex are added only when you focus on or expand that gene.
When members sit in different steps, a step just for the complex is made around the middle, with members wrapped every 10.
Edges between genes within a complex are normally hidden; click the box or select a member in green to show them.</li>
<li>Relations where the paper names the partner only as a complex (TORC1, calcineurin, CK2, PKA, etc.) are stored as relations of each member gene.
On the map, if those genes are in the same box, a single edge is drawn from the box (otherwise one edge per gene). The edge's evidence in the details panel says "as complex TORC1 (upstream)".
Which genes each name stands for is in data/complex_groups.csv (PKA means only the catalytic subunits TPK1–3).</li>
<li>Paralogs (gene pairs from whole-genome duplication etc. whose roles may overlap) are enclosed in a double-line box with a color per pair and light shading (complexes use dotted boxes).
If one of a pair is on the map, the other is added next to it (in the upper of the two steps, or in the step of the focused gene if there is one;
unlike complexes, no separate step is made). Paralogs of transcription factors added from the TFs list go in the same top step. Paralogs of genes in a downstream bundle are not added, but if both are in the same bundle they are enclosed inside the bundle box. Genes already in a complex box are not enclosed. "Evidence" in the box's or gene's details shows why their functions overlap (genetic interaction of the double deletion, GO).</li>
<li>Names of complex and paralog boxes are shown only when a member is selected in green or the box is clicked (names of downstream bundles are always shown).</li>
<li>Transcriptional regulation edges between transcription factors are omitted (except edges of focused, expanded, or selected genes, and paths from the Paths tab).</li>
</ul>
<h4>Map panel controls</h4>
<ul>
<li>◀ ▶: back / forward through views (restores focus, expand, steps, TFs, and also the Legend and Conditions tab checkboxes). "Re-layout": redraw from the current focus and expand. "Fit to view": show the whole map. "Reset settings": return TFs, paths, conditions, layout, colors, edges, and Legend to their defaults (focus, expand, and steps stay). Click the background: clear highlighting.</li>
<li>"⧉ New panel": add a map panel (up to 4: the 2nd to the right, the 3rd below the 1st, the 4th below the 2nd).
It opens focused on the genes selected in green (or else the expanded or focused genes). The blue frame marks the active panel.</li>
<li>"Open in new window": with one panel, copies the current view to a new window; with two or more, moves that panel to a new window.</li>
<li>Below the search box: Layout and edge color (shared by all panels), "Reset settings", and saving the whole map as an image (PNG, SVG).</li>
<li>When there are many edges, you are asked before drawing. If layout or edge routing takes longer than 0.6 s, a spinner appears at the lower right of the cursor.</li>
<li>Edge routes stay the same until you move genes or re-layout. Routes of edges hidden by the Legend or Conditions are kept free,
and normally hidden edges (between transcription factors, inside complexes and bundles, etc.) shown by green selection are added into free space without moving other edges.</li>
</ul>
"""

LEGEND = _STYLE + """
<h3>Legend</h3>
<ul>
<li>Click a heading to open or close its section. Uncheck a row to hide that type from the map (shared by all panels).</li>
<li>Checkbox left of a heading: show or hide all items in the section (unchecked if any item is unchecked).</li>
<li><b>Highlighted</b>: genes currently selected, expanded, or focused. Click a name to go to that gene; × removes it.</li>
<li><b>Effect</b>: the mark at the end of an edge. Triangle = activation, T-bar = inhibition, open diamond = unknown effect, dotted line = undirected binding.
With edge color set to "Effect", edges are colored <span style='color:#e53935'>red = activation</span>, <span style='color:#1e88e5'>blue = inhibition</span>, gray = unknown effect.</li>
<li><b>Modification/regulation</b>: edge color and symbol (P = phosphorylation, Tx = transcriptional regulation, Ub = ubiquitination, etc.).</li>
<li><b>Role</b>: gene color, inferred from the functional description. Choosing a condition or strain in the Conditions (genes) or Deletions tab colors genes by that measurement; clearing the choice returns to role colors.</li>
<li><b>Deletion strain data</b>: changes in the strain chosen in the Deletions tab (log2 ratio vs. wild type). <span style='color:#d32f2f'>Red = up</span>,
<span style='color:#1565c0'>blue = down</span>, white = unchanged, gray = no data, black = deleted gene. ±2 (4-fold) or more is shown at full intensity.</li>
<li><b>Display</b>: "+number", whether to omit downstream tips when zoomed out, and type symbols on edges.</li>
</ul>
"""

GENES = _STYLE + """
<h3>Genes</h3>
<p>Genes on the current map (the active map panel) are split into three lists — <b>Focus</b> (orange), <b>Expand</b> (purple), and <b>Others</b> — each sorted by name (the number in each title is the gene count; empty lists are not shown). Type a name in the box at the top to filter. Click × at the right of a gene in the Expand list to remove it from Expand (same as × in the legend).</p>
<ul>
<li>Click a gene to <b>select it in green</b> on the map and show its details on the right. Genes selected in green on the map are also selected in the lists.</li>
<li>Hold Shift or ⌘ (Ctrl on Windows) to select several (selections in other lists are kept).</li>
</ul>
"""

TFS = _STYLE + """
<h3>TFs</h3>
<p>A list of the <b>transcription factors that regulate transcription</b> of the focused and expanded genes. Check one to show it in the top step of the map.</p>
<ul>
<li>Type a name in the box at the top to keep transcription factors whose names contain it (if a gene's name contains it, all that gene's transcription factors are kept).</li>
<li>The list is nested as gene (title color: orange = focus, purple = expand) → effect (<span style='color:#e53935'>→ activation</span>, <span style='color:#1e88e5'>⊣ inhibition</span>, ◇ unknown effect)
→ transcription factor. Use ▸ to open and close. Numbers in ( ) are counts.</li>
<li>Checking a gene or effect toggles all transcription factors under it. "Select all" / "Clear all" at the bottom apply to every transcription factor in the list.</li>
<li>Transcription factors are sorted by name. Gray ones are already on the map through other relations and are listed last in their group.</li>
<li>⇄ marks transcription factors listed under several genes (their checkboxes are linked).</li>
<li>Click a transcription factor's name to show its details on the right.</li>
<li>"TFs on current map" lists the transcription factors now shown on the map (by name). Click one to show its details on the right.</li>
</ul>
"""

RELATION = _STYLE + """
<h3>Paths</h3>
<p>Lists <b>the paths that connect</b> the genes you choose.</p>
<h4>1. Choose a path mode</h4>
<ul>
<li>Choose in the selector at the top left ("None" shows the normal map):
 <ul>
 <li>All paths — paths linking the chosen genes (regardless of arrow direction)</li>
 <li>Directed paths — from one chosen gene to another, following the arrows</li>
 <li>Common regulators — from genes upstream of all chosen genes</li>
 <li>Common targets — to genes downstream of all chosen genes</li>
 <li>Paths acting to / from the anchor gene — to (from) the anchor gene, following the arrows. An anchor must be chosen</li>
 </ul></li>
<li>Typing in "Filter by name" at the top right filters both the gene list and the path list (paths through genes with that name).</li>
</ul>
<h4>2. Anchor and steps</h4>
<ul>
<li><b>Anchor</b>: choose one of the checked genes to keep only paths that end at that gene.</li>
<li><b>Steps</b> (1–3): show only paths of exactly that many steps. 1 means direct relations. A complex counts as one.</li>
</ul>
<h4>3. Choose genes</h4>
<ul>
<li>The "Genes" list shows the focused and expanded genes of the active map panel, grouped and sorted by name. Check the ones to examine
(checking a group toggles its genes; "Select all" / "Clear all" also work).</li>
<li>If the list is empty, focus on or expand genes on the map to add them.</li>
<li>Paths are searched when at least two genes are checked for "All paths", "Directed paths", etc., or at least one for "Common regulators" / "Common targets".</li>
</ul>
<h4>4. Viewing paths</h4>
<ul>
<li>The "Paths" list has three levels: "from X" → "X … A" (sorted by destination name) → each path. The number at each level is the number of paths inside (e.g. TORC1 –P→ SCH9 –P⊣ MAF1).
→ activation, ⊣ inhibition, ◇ unknown effect, ← ⊢ are arrows pointing right to left, and P, Tx, etc. are relation types. Long paths are shortened; hover to see the whole path.</li>
<li>Common regulators or targets, if any, are listed below with their count and names (the first 30 if there are many; all are under "from X" in the list).</li>
<li>On the map, only the checked genes are highlighted. Path edges and intermediate genes are not drawn until you select them in the list.
Selecting draws those paths (selecting any level draws all paths inside it). Click a selected path again to deselect it.</li>
<li>The details panel on the right lists, for each selected path, the relation at each step (edge, type, confidence; up to 20 paths). Click an edge name to see that relation's details (supporting papers, etc.).
Deselecting returns to this help.</li>
<li>Clicking a gene on the map moves paths through that gene to the top and grays out and moves down pairs that do not pass through it. Click the background to undo.
While paths selected in the list are drawn, clicking genes or edges does not re-sort, and the drawn paths stay (click the background to clear).</li>
<li>If you see "Over … paths; the list was cut off there", reduce the steps or check fewer genes.
For pairs where counting stopped at … paths, the count is shown as "… or more".</li>
<li>"Open in new panel": shows only the currently highlighted genes (genes of the drawn paths, or the checked genes if none are selected) in a new map panel (that panel keeps the paths fixed).</li>
<li>Set the path mode to "None" to return to the normal map.</li>
</ul>
"""

SAVED = _STYLE + """
<h3>Saved</h3>
<p>Save map states you use often under a name and load them later.</p>
<ul>
<li><b>Save</b>: check the items to keep under "Items to save" ("Select all" / "Clear all" toggle them together), enter a name, and click "Save".
You can choose from Focus (genes and steps), Expand, Select (green selection), TFs, Paths (checks, path mode, steps, anchor gene), Conditions, and Legend.</li>
<li><b>Load</b>: pick a view in the "Saved views" list (sorted by name) and click "Load" (or double-click). Only the saved items are applied to the active panel; other items stay as they are (a view without paths keeps the current paths).
Selecting a view shows its date and contents on the right (this panel). Click the selected view again, or click outside the list, to deselect.</li>
<li>Saving with an existing name overwrites it. Saved views are kept only on this computer.</li>
</ul>
"""

CONDITIONS = _STYLE + """
<h3>Conditions</h3>
<p>Switch what to view with the selector at the top left. Both modes share the same layout: the condition list (grouped, collapsible) at the top, viewing options in the middle, and items on the current map at the bottom. Type a name in the box on the right to filter conditions.
<b>Paths</b>: highlights the map by <b>the conditions under which relations (edges) were reported</b> (stress, nutrients, cell-cycle phase, etc.). Check as many conditions as you like.
<b>Genes</b>: highlights genes whose expression or phosphorylation changed strongly in the checked conditions (see Help for "Expression and phosphorylation by condition"). The rest of this page describes "Paths".
Conditions follow the YEASTRACT+ environmental conditions (groups and subgroups), with cell-cycle phases (G1, S, G2, M, end of M) added as one group.</p>
<ul>
<li>Only relations (edges) with the checked conditions and the genes at both ends are highlighted. Other edges are removed and other genes are faded. With everything checked, you see the normal map.
Edges removed by green selection and hidden edges (between transcription factors, or unchecked in the Legend) are not counted, so only genes at the ends of visible edges are highlighted.</li>
<li><b>Show most upstream paths</b>: when checked, only the edges with the checked conditions that start a path (no matching edge enters their upstream gene) and the genes at both ends are highlighted.
Where matching edges form a loop with no start, all edges in the loop are highlighted. This works even with all conditions checked and is not changed by "Select all" / "Clear all".</li>
<li>"Select all" / "Clear all" below the list toggle all conditions. Groups (stress, carbon source, cell cycle, etc.) open and close with ▸; checking a group toggles its conditions. Only conditions attached to some relation are listed. Conditions with no edges on the current map are gray (as in the Legend).</li>
<li>"No condition recorded" means relations whose conditions are not yet known. Uncheck it to highlight only relations with known conditions.</li>
<li>The bottom box lists edges on the current map that match the checked conditions, by name (red = activation, blue = inhibition). Click one to show its details on the right.</li>
<li>Clicking an edge shows its conditions under "Condition" in the details panel (the source is in the evidence section).</li>
<li>Conditions come from YEASTRACT+ (transcriptional regulation) and the literature. A YEASTRACT+ condition means "reported under that condition";
it does not necessarily mean the relation acts only then.</li>
<li>Cell-cycle phases come from the literature ("G2/M" means both G2 and M). For transcriptional regulation by cell-cycle transcription factors (SBF, MBF, HCM1, FKH1/2, NDD1, MCM1, SWI5, ACE2),
relations to targets whose expression peaks in the same phase as the factor's activity are also given that phase (peaks are computed from expression data of synchronized cells, such as Spellman 1998; the evidence says "cell-cycle expression (SPELL)").
"Cell-cycle synchronization (any phase)" marks YEASTRACT+ transcriptional regulation reported in synchronized cells (phase unknown).</li>
</ul>
"""


def _condition_list() -> str:
    """条件ごとの説明（data/conditions.csv の description 列）を群ごとに並べる（Condition が画面の言語の群・名前・説明を返す）。"""
    from .. import conditions
    groups: dict[str, list] = {}
    for c in conditions.load():
        groups.setdefault(c.group, []).append(c)
    parts = ["<h4>Condition descriptions</h4>"]
    for group, items in groups.items():
        lines = "".join(f"<li><b>{c.label}</b> — {c.description}</li>" for c in items)
        parts.append(f"<p style='margin:6px 0 0 0'><b>{group}</b></p><ul>{lines}</ul>")
    return "".join(parts)


CONDITIONS += _condition_list()

DATA = _STYLE + """
<h3>Expression and phosphorylation by condition</h3>
<p>Separately from paths, you can see for each condition <b>how much each gene is made (expression)</b> and <b>whether it is active (phosphorylation)</b>.
All values are log2 ratios vs. the control (before or without treatment) (+1 = 2-fold, −1 = half).</p>
<ul>
<li>In the Conditions tab on the left, switch the top-left selector to "Genes" and choose <b>mRNA</b> or <b>phosphorylation</b> under "Data".
Only genes that <b>changed 2-fold or more</b> in any checked condition (any number; group checkboxes and "Select all" / "Clear all" toggle them together) are highlighted; other genes and their edges are faded (as with paths, checking everything gives the normal map). Map colors are not changed.
The box below lists the highlighted genes on the current map by name. The value is the largest change among the checked conditions, with that condition in parentheses. Click a gene to show its details on the right.
Conditions are grouped as in "Paths" (only conditions with measurements are listed; conditions without the chosen data type are gray). Switching to "Paths" removes the gene highlighting.</li>
<li>Clicking a gene shows values for all conditions under "log2 ratio by condition" in the details panel.
Click a condition name to expand the values per measurement and links to the source papers; click again to close. For phosphorylation, sites with p &lt; 0.05 or a 2-fold change are listed first, and other measured sites follow in small gray text. Conditions without measurements have gray names and cannot be opened. Opened conditions stay open when you open another gene.
The same appears in the details panel of the Database tab.</li>
<li><b>Expression (mRNA)</b>: 93 measurements from SGD expression data (SPELL) in wild type with clear conditions and a comparable control (Gasch 2000, Causton 2001, etc.).
Each measurement is the mean over time points where the response is strong (about 10–60 min for shocks). A condition's value is the median of its measurements.</li>
<li><b>Phosphorylation</b>: Leutert et al. 2023 (changes in phosphosites after 5 min exposure to about 100 conditions). A gene's value is that of the site with the largest change among sites with uncorrected p &lt; 0.05 (the site is shown in the details panel; * if also p &lt; 0.05 after correction).
If a gene was measured but no site qualifies, the details table shows n.s. (no clear change) and the map shows white. Unmeasured genes are gray. About 1,400 genes are measured.
This is whether the gene's protein was phosphorylated, not the kinase's own activity (e.g. dephosphorylation of SCH9 T467 and NPR1 with rapamycin).</li>
<li>Many genes (kinases such as TOR1 and SCH9) change their activity by phosphorylation or localization without mRNA changes, so look at expression and phosphorylation separately.</li>
</ul>
"""

DATABASE = _STYLE + """
<h3>Database</h3>
<p>Browse the lists of genes, regulatory relations, and categories; filter them and export to CSV (view only: the server version of the data is authoritative and is synced at every start).</p>
<p>Select a row to show the details of that gene, relation, or category on the right (this panel). The content is the same as the Network details panel; gene names and relations in it can be clicked. Click an empty part of the table or outside it to deselect and clear this panel (Help at the top right of the table shows this guide).
Use ◀ ▶ above this panel to go back to details shown earlier.</p>
<ul>
<li><b>Filtering genes</b>: type a name in "Gene" and pick from the drop-down of matching suggestions (clicking the box also shows suggestions; typing a suggestion exactly and pressing Enter also works). This keeps that gene and
genes reached by following relations up to the given number of "upstream" and "downstream" steps (0–3, default 1). 0 means that direction is not followed.
Check "Exact" to the right to ignore steps and keep only the chosen gene.</li>
<li><b>Filtering relations</b>: choose genes in "Upstream" / "Downstream" the same way to keep only relations going out of (into) that gene. Choose both for relations between the two.
Click "Condition" to open a drop-down of condition groups (stress, carbon source, cell cycle, etc.). Click a group to open its subgroups; relations with at least one checked condition (any number) are kept. Checking a group toggles its subgroups. Everything is checked at first (no filtering); unchecking everything gives 0 rows ("No condition recorded" is one of the conditions). "Clear all" / "Select all" to the right toggle all.</li>
<li><b>Categories</b>: budding yeast complexes from Complex Portal (about 630; a gene can belong to several complexes; on the map a complex is boxed when two or more members are shown) and paralog pairs (about 490; Alliance pairs whose functional overlap is supported by a genetic interaction of the double deletion or by GO overlap). Type part of a name in the left box ("Filter by name") to keep categories whose names contain it (case-insensitive; separate several words with spaces to require all of them, e.g. torc → TORC1, TORC2; "rna polymerase" → RNA polymerase complexes). Choosing a gene in "Gene" the same way keeps only the categories it belongs to (e.g. TOR2 → TORC1 (TOR2 form), TORC2). Using both keeps only rows matching both. Selecting a row shows its member genes and description on the right (for Complex Portal, a link to the source and its description).</li>
<li>Retyping or clearing a chosen name removes that filter. Combined filters keep rows matching all of them. The count shows "remaining / total".</li>
<li>"Export visible table to CSV…" writes only the rows left by the filters (gene and relation tables only; disabled on the Categories tab).</li>
<li>When loading, filtering, or sorting takes time, the cursor changes to a busy indicator.</li>
</ul>
"""

# 説明欄の見方: 説明欄の一番下の「Help」で、出している説明（遺伝子・関係（線）・複合体・パラログ）の見方を新しいページとして出す
NODE_DETAIL = """
<h4 style='margin-top:0'>Reading gene details</h4>
<ul>
<li><b>Focus</b> / <b>Expand</b> to the right of the gene name: focus on or expand that gene in the active map panel (a gene not on the map is added with its connections to the current map, as from the search box pop-up).</li>
<li><span style='color:#b26a00'>Orange text</span>: the number of upstream/downstream genes not on the map, that the gene is not in the active map panel, and edges between transcription factors omitted from the map.</li>
<li><b>Systematic name</b>: SGD ORF name (e.g. YJR066W). <b>Layout order</b>: the order on the map and the level in the whole network (level 1 is the most upstream; "no level" if it cannot be determined, e.g. inside a loop).
<b>ORF status</b>: SGD classification (Verified = function confirmed, Uncharacterized = not yet known, Dubious = possibly not a gene).</li>
<li>English text: SGD functional description.</li>
<li><b>Complexes</b>: Complex Portal complexes this gene belongs to. Click for the complex details. <b>Paralogs</b>: partners whose roles may overlap. "Evidence" shows why they overlap.</li>
<li><b>log2 ratio by condition</b>: change vs. the control (+1 = 2-fold, −1 = half). <span style='color:#c62828'>Red = up</span>, <span style='color:#1565c0'>blue = down</span> (1.5-fold or more);
bold is 2-fold or more, – is not measured, n.s. means phosphorylation was measured but no site changed clearly. Click a condition name to expand the values per measurement and their sources.</li>
<li><b>Deletion strain data</b>: genes that changed in the strain lacking this gene, and deletion strains in which this gene changed (log2 ratio vs. wild type, largest change first).
"Color map" / "Color" colors the map by that strain's data. Click a gene name to go to its details. "All" expands everything.
Included are mRNA changes with p &lt; 0.05 and at least 1.4-fold, and phosphosites reported as changed by the paper.</li>
<li><b>Upstream / Downstream</b>: relations into and out of this gene. → activation, ⊣ inhibition, ─◇ unknown effect (may be either activation or inhibition), — undirected binding.
Gray text is the relation type. Partners on the map are listed first; click one to show that relation's details.</li>
</ul>
"""

EDGE_DETAIL = """
<h4 style='margin-top:0'>Reading relation (edge) details</h4>
<ul>
<li>Heading: upstream → downstream. Click a gene name for its details.</li>
<li><b>Type</b>: how it acts — phosphorylation, transcriptional regulation, binding, etc.</li>
<li><b>Effect</b>: whether it strengthens (activation →) or weakens (inhibition ⊣) the downstream gene's function. An unknown effect is treated in calculations as possibly either activation or inhibition.
<span style='color:#e65100'>⚠ Sources disagree</span> means sources give opposite directions.</li>
<li><b>Basis for effect</b>: what the direction is based on (literature-verified, SGD GO annotation, GO-CAM, TF induction experiments (IDEA), YEASTRACT+, inference from deletion strain data, inference from expression by condition). For an unknown effect, the reason. Inference from expression by condition uses which way targets move in conditions that change the transcription factor's activity (heat, rapamycin, etc.), and so also includes effects through other transcription factors acting in the same condition (indirect effects).</li>
<li><b>Confidence</b>: the strongest evidence. A literature-verified (checked against a sentence in a paper), B individual experiments, C high-throughput experiments only, D inference only, U no evidence format.</li>
<li><b>Condition</b>: conditions under which the relation was reported (stress, nutrients, cell-cycle phase, etc.). It does not necessarily act only under those conditions.</li>
<li>For literature-verified relations, the following are also shown when the paper states them:
<b>Partner</b> (e.g. a cyclin of CDC28), <b>Modified site</b> (e.g. S582), <b>Supporting experiment</b> (in vivo, in vitro, genetic, structural),
<b>Necessary / sufficient</b> (whether it is lost when the upstream gene is deleted, or caused by the upstream gene alone), <b>Redundant upstream</b> (upstream regulators acting in parallel, so the effect remains when one is deleted),
<b>Strength</b>, <b>What changes</b> (expression, activity, degradation, localization), and <b>Timing</b> (transient, sustained, returns on adaptation).</li>
<li><b>Evidence and references</b>: one line per source. The colored [ ] is the source (literature, BioGRID, YEASTRACT+, SGD GO annotation, etc.); click a PMID to open PubMed.
"Literature-verified" lines give what we read from the abstract, in our own words (no sentences are quoted from the paper; the source is shown by PMID).</li>
<li>Links at the bottom let you compare with SGD's interaction and regulation lists.</li>
</ul>
"""

COMPLEX_DETAIL = """
<h4 style='margin-top:0'>Reading complex details</h4>
<ul>
<li><b>Source</b>: the Complex Portal (list of budding yeast complexes) accession. Click to open the Complex Portal page.</li>
<li><b>Description</b>: the Complex Portal description.</li>
<li><b>Members</b>: genes in the complex. Click for the gene details. On the map, a complex is enclosed in a dotted box when two or more members are shown.</li>
<li>Relations between genes in the same complex are normally hidden on the map (click the box to show them).</li>
</ul>
"""

PARALOG_DETAIL = """
<h4 style='margin-top:0'>Reading paralog details</h4>
<ul>
<li>Paralogs are gene pairs from whole-genome duplication etc. whose roles may overlap. Click a gene name in the pair for its details.</li>
<li>First line: source of the candidate pair (Alliance).</li>
<li><b>Double deletion is much worse</b>: BioGRID genetic interactions (deleting either alone is fine, but deleting both impairs growth). This is evidence of overlapping function; click a PMID to open PubMed.</li>
<li><b>GO overlap</b>: how much the two genes' GO terms (biological process, molecular function) overlap (0–1; closer to 1 means more alike).</li>
<li>On the map, each pair is enclosed in a double-line box with its own color.</li>
</ul>
"""

DETAIL_HELP = {"node": NODE_DETAIL, "edge": EDGE_DETAIL, "complex": COMPLEX_DETAIL, "paralog": PARALOG_DETAIL}


def detail_help(topic: str) -> str:
    """説明欄の一番下の Help で出すページ。topic は DETAIL_HELP のキーか、何も出していないとき map（マップの使い方）。"""
    return MAP if topic == "map" else _STYLE + DETAIL_HELP[topic]

DETAILS_ALL = _STYLE + "<h3>Reading the details panel</h3><p>While gene, edge, or complex details are shown, \"Help\" at the bottom of the details panel explains how to read them (◀ to return).</p>" + \
    NODE_DETAIL + EDGE_DETAIL + COMPLEX_DETAIL + PARALOG_DETAIL

DELETION = _STYLE + """
<h3>Deletions</h3>
<p>See on the map <b>how mRNA and phosphorylation of other genes actually changed</b> (measured data) in strains with one gene deleted.
These are measured values compared with wild type, not simulations.</p>
<ul>
<li><b>Browse by</b> (selector at the top left; changed gene by default):
<b>Changed gene</b> — genes on the current map, sorted by name (black first, gray after). Type a name in the box on the right to filter. Genes that changed in some deletion strain are black; genes that changed in none are gray and grouped at the bottom.
Selecting a gene lists, in the box below, the deletion strains that changed it (deleted gene and value; − lowered, + raised), sorted by name.
This lets you find candidate upstream regulators of that gene from measured data. Click a strain to color the map by its data.<br>
<b>Deleted gene</b> — deletion strains sorted by name (black first, gray after). Type a name in the box on the right to keep strains containing it.
A strain is black if <b>any gene on the current map changed in it</b>, and gray (grouped at the bottom) if no gene on the map changed
(this updates as the map changes; hover over a strain to see how many map genes changed).
"(phosphorylation)" marks strains with phosphorylation data only; "(mRNA, phosphorylation)" marks strains with both.
Click a strain to color the map by its data and list, in the box below, the genes on the current map that changed in it (by name). Click a gene to show its details on the right.</li>
<li>Map coloring: <span style='color:#c62828'>red = increased</span>, <span style='color:#1565c0'>blue = decreased</span>, black = deleted gene
(when the strain is deselected, e.g. by clicking it again, role colors return).
White for mRNA means measured without a large change. Gray for phosphorylation means the paper reports no change (it may also be unmeasured).
Stopping the coloring also clears the box below.</li>
<li><b>Data</b>: <b>mRNA</b> from Deleteome (Kemmeren et al. 2014; 1,481 strains, about 6,000 genes measured).
<b>Phosphorylation</b> from Bodenmiller et al. 2010 (113 strains lacking a kinase or phosphatase). Data types not measured for a strain cannot be chosen.</li>
<li>"Deletion strain data" in a gene's details panel also shows genes that changed in the strain lacking that gene, and deletion strains in which that gene changed.</li>
<li>mRNA includes only changes with p &lt; 0.05 and at least 1.4-fold. Effects of a deletion include indirect ones (X → Z → Y).
Deleteome strains were grown in rich medium, so genes that act only under stress may show no change when deleted.</li>
</ul>
"""

TOPICS = {"genes": GENES, "trf": TFS, "relation": RELATION, "conditions": CONDITIONS, "saved": SAVED, "map": MAP, "legend": LEGEND,
          "data": DATA, "deletion": DELETION}
ALL = MAP + DETAILS_ALL + LEGEND + GENES + TFS + RELATION + CONDITIONS + DELETION + DATA + SAVED + DATABASE
